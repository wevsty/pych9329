from enum import Enum

from serial import Serial

import pych9329.exceptions as exceptions
import pych9329.frame_utils as frame_utils
from pych9329.struct_utils import Structure


class ChipParameter(Structure):
    _fields_ = [
        ("c", "work_mode"),
        ("c", "serial_communication_mode"),
        ("c", "serial_address"),
        (">I", "serial_baud_rate"),
        (">H", "reserve_00"),
        (">H", "communication_packet_interval"),
        ("<H", "usb_vid"),
        ("<H", "usb_pid"),
        (">H", "keyboard_upload_interval"),
        (">H", "keyboard_release_delay"),
        (">H", "keyboard_auto_enter_flag"),
        ("4s", "keyboard_enter_data_1"),
        ("4s", "keyboard_enter_data_2"),
        ("4s", "keyboard_filtering_start"),
        ("c", "usb_string_descriptor_flag"),
        ("4s", "keyboard_fast_upload_flag"),
        ("12s", "reserve_01"),
    ]


def get_chip_parameters(serial_object: Serial) -> ChipParameter:
    # request frame
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x08",
        b"\x00",
        b"",
    )
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)
    serial_object.flush()
    # Reply frame should be 56 bytes
    reply_length = 56
    reply_buffer = serial_object.read(reply_length)
    result = data_frame.parse_frame(reply_buffer)
    if result is False:
        raise exceptions.ProtocolError("parser buffer error")
    chip_parameter = ChipParameter.from_buffer(data_frame.get_data())
    return chip_parameter


def set_chip_parameters(serial_object: Serial, parameter: ChipParameter) -> bool:
    parameter.buffer_flush()
    parameter_buffer = parameter.buffer
    # request frame
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x09",
        b"\x00",
        b"\x00",
    )
    data_frame.set_data(parameter_buffer)
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)
    serial_object.flush()
    # Reply frame should be 7 bytes
    reply_length = 7
    reply_buffer = serial_object.read(reply_length)
    result = data_frame.parse_frame(reply_buffer)
    if result is False:
        raise exceptions.ProtocolError("parser buffer error")
    reply_data = data_frame.get_data()
    if reply_data == frame_utils.DataFrameStatus.SUCCESS.value:
        return True
    return False


class USBStringSubCommand(Enum):
    MANUFACTURER = b"\x00"
    PRODUCT = b"\x01"
    SERIAL_NUMBER = b"\x02"


def get_usb_string_info(serial_object: Serial, sub_command: bytes) -> str:
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x0a",
        b"\x01",
        sub_command,
    )
    request_packet = data_frame.create_frame()
    serial_object.readall()
    serial_object.write(request_packet)
    serial_object.flush()
    reply_buffer = serial_object.readall()
    result = data_frame.parse_frame(reply_buffer)
    if result is False:
        raise exceptions.ProtocolError("parser buffer error")
    if data_frame.get_data_length() < 2:
        raise exceptions.ProtocolError("parser buffer error")
    data_buffer = data_frame.get_data()
    # string_length = data_buffer[1]
    string_bytes = data_buffer[2:]
    # usb_info = string_bytes.decode('utf-8', 'ignore')
    try:
        usb_info = string_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise exceptions.InvalidStringEncoding("unable decode string")
    return usb_info


def set_usb_string_info(
    serial_object: Serial, sub_command: bytes, string_info: str
) -> bool:
    info_data = string_info.encode("utf-8")
    if len(info_data) > 23:
        raise InvalidStringLength("string too long")
    data_buffer = (
        sub_command + int.to_bytes(len(info_data), byteorder="big") + info_data
    )
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x0b",
        b"",
        b"",
    )
    data_frame.set_data(data_buffer)
    request_packet = data_frame.create_frame()
    serial_object.readall()
    serial_object.write(request_packet)
    serial_object.flush()
    reply_buffer = serial_object.readall()
    result = data_frame.parse_frame(reply_buffer)
    if result is False:
        raise exceptions.ProtocolError("parser buffer error")
    reply_data = data_frame.get_data()
    if reply_data == frame_utils.DataFrameStatus.SUCCESS.value:
        return True
    return False


def get_serial_number(serial_object: Serial) -> str:
    return get_usb_string_info(serial_object, USBStringSubCommand.SERIAL_NUMBER.value)


def set_serial_number(serial_object: Serial, string_data: str):
    return set_usb_string_info(
        serial_object, USBStringSubCommand.SERIAL_NUMBER.value, string_data
    )


def get_manufacturer(serial_object: Serial) -> str:
    return get_usb_string_info(serial_object, USBStringSubCommand.MANUFACTURER.value)


def set_manufacturer(serial_object: Serial, string_data: str):
    return set_usb_string_info(
        serial_object, USBStringSubCommand.MANUFACTURER.value, string_data
    )


def get_product(serial_object: Serial) -> str:
    return get_usb_string_info(serial_object, USBStringSubCommand.PRODUCT.value)


def set_product(serial_object: Serial, string_data: str):
    return set_usb_string_info(
        serial_object, USBStringSubCommand.PRODUCT.value, string_data
    )


def send_command_reset(serial_object: Serial) -> None:
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x0f",
        b"\x00",
        b"",
    )
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)


def send_command_restore_factory_config(serial_object: Serial) -> None:
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x0c",
        b"\x00",
        b"",
    )
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)


if __name__ == "__main__":
    pass
