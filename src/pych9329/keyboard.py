import random
import time
from collections import OrderedDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from serial import Serial

import pych9329.frame_utils as frame_utils
from pych9329.hid_code_map import HID_CODE_MAP

MODIFIER_KEY_NAME_MAP = {
    "": 0b00000000,
    "ctrl": 0b00000001,
    "ctrl_left": 0b00000001,
    "shift": 0b00000010,
    "shift_left": 0b00000010,
    "alt": 0b00000100,
    "alt_left": 0b00000100,
    "win": 0b00001000,
    "win_left": 0b00001000,
    "ctrl_right": 0b00010000,
    "shift_right": 0b00100000,
    "alt_right": 0b01000000,
    "win_right": 0b10000000,
    # alias win
    "gui": 0b00001000,
    "meta": 0b00001000,
    # alias empty
    "null": 0b00000000,
    "none": 0b00000000,
}


def deduplicate_list(lt: List) -> List:
    return list(OrderedDict.fromkeys(lt))


def receive_indicator_status(serial_object: Serial) -> Tuple[bool, Dict[str, bool]]:
    result_dict: Dict[str, bool] = {
        "usb_connect_status": False,
        "num_lock": False,
        "caps_lock": False,
        "scroll_lock": False,
    }
    result_value = False
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x01",
        b"\x00",
        b"",
    )
    frame_packet = data_frame.create_frame()
    # clear connection buffer
    serial_object.readall()
    # write command
    serial_object.write(frame_packet)
    serial_object.flush()
    # read packet
    reply_packet: bytes = serial_object.readall()
    parse_result = data_frame.parse_frame(reply_packet)
    if parse_result is False:
        return result_value, result_dict
    reply_data = data_frame.get_data()
    # 获取USB连接状态
    usb_connect_status: bytes = reply_data[1:2]
    if usb_connect_status == b"0x00":
        result_dict["usb_connect_status"] = False
    else:
        result_dict["usb_connect_status"] = True
    # 获取键盘锁定状态
    indicator_bytes: bytes = reply_data[2:3]
    indicator_flag = int.from_bytes(indicator_bytes, byteorder="little")
    if indicator_flag & 0x01 != 0:
        result_dict["num_lock"] = True
    else:
        result_dict["num_lock"] = False
    if indicator_flag & 0x02 != 0:
        result_dict["caps_lock"] = True
    else:
        result_dict["caps_lock"] = False
    if indicator_flag & 0x04 != 0:
        result_dict["scroll_lock"] = True
    else:
        result_dict["scroll_lock"] = False
    result_value = True
    return result_value, result_dict


def send_general_data(
    serial_object: Serial,
    key_tuple: Tuple[str, str, str, str, str, str] = ("", "", "", "", "", ""),
    modifiers: Optional[List[str]] = None,
) -> None:
    if modifiers is None:
        modifiers = []

    # CMD_SEND_KB_GENERAL_DATA data has exactly 8 bytes
    data = b""

    # first byte modifiers key, each bit represents 1 key
    #
    # BIT0 - ctrl_left
    # BIT1 - shift_left
    # BIT2 - alt_left
    # BIT3 - win_left
    # BIT4 - ctrl_right
    # BIT5 - shift_right
    # BIT6 - alt_right
    # BIT7 - win_right
    modifier_value: int = 0x00
    for key_name in modifiers:
        if key_name not in MODIFIER_KEY_NAME_MAP:
            raise InvalidModifierKey(key_name)
        modifier_value |= MODIFIER_KEY_NAME_MAP[key_name]
    data += modifier_value.to_bytes(1, byteorder="little")

    # second byte must be 0x00
    data += b"\x00"

    # third to eighth bytes are keys
    # we can press upto 6 buttons
    for key in key_tuple:
        if key not in HID_CODE_MAP:
            raise InvalidKey(key)
        hid_code, _ = HID_CODE_MAP[key]
        data += hid_code

    # create packet and send
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x02",
        b"",
        b"",
    )
    data_frame.set_data(data)
    frame_packet = data_frame.create_frame()
    serial_object.write(frame_packet)
    serial_object.flush()


def trigger(
    serial_object: Serial,
    keys: list[str],
    modifiers: Optional[List[str]] = None,
) -> None:
    trigger_keys = keys.copy()
    trigger_modifiers = modifiers.copy()
    trigger_keys = deduplicate_list(trigger_keys)
    trigger_modifiers = deduplicate_list(trigger_modifiers)
    # Supports press to 6 normal buttons at the same time
    if len(trigger_keys) > 6:
        raise TooManyKeys("CH9329 supports maximum of 6 keys to be pressed at once.")
    if len(trigger_modifiers) > 8:
        raise TooManyKeys(
            "CH9329 supports maximum of 8 control keys to be pressed at once."
        )
    # if len(keys) < 6, add empty keys
    while len(trigger_keys) < 6:
        trigger_keys.append("")
    send_general_data(
        serial_object,
        (
            trigger_keys[0],
            trigger_keys[1],
            trigger_keys[2],
            trigger_keys[3],
            trigger_keys[4],
            trigger_keys[5],
        ),
        trigger_modifiers,
    )


def press(
    serial_object: Serial, key: str, modifiers: Optional[List[str]] = None
) -> None:
    if modifiers is None:
        modifiers_copy = []
    elif isinstance(modifiers, list):
        modifiers_copy = modifiers.copy()
    else:
        modifiers_copy = []
    if key not in HID_CODE_MAP:
        raise InvalidKey(key)
    _, shift = HID_CODE_MAP[key]
    if shift:
        modifiers_copy.append("shift")
    send_general_data(serial_object, (key, "", "", "", "", ""), modifiers_copy)


def release(serial_object: Serial) -> None:
    send_general_data(serial_object, ("", "", "", "", "", ""))


def click(
    serial_object: Serial,
    key: str,
    min_interval: float = 0.02,
    max_interval: float = 0.05,
) -> None:
    sleep_time = random.uniform(min_interval, max_interval)
    press(serial_object, key)
    time.sleep(sleep_time)
    release(serial_object)


def send_text(
    ser: Serial,
    text: str,
    min_interval: float = 0.02,
    max_interval: float = 0.05,
) -> None:
    for char in text:
        click(ser, char, min_interval, max_interval)


if __name__ == "__main__":
    pass
