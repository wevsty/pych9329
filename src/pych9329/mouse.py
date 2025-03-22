import random
import time
import typing

from serial import Serial

import pych9329.exceptions as exceptions
import pych9329.frame_utils as frame_utils

MOUSE_BUTTON_NAME_MAP: typing.Final[dict[str, bytes]] = {
    "null": b"\x00",
    "left": b"\x01",
    "right": b"\x02",
    "center": b"\x04",
    # alias
    "": b"\x00",
    "none": b"\x00",
    "middle": b"\x04",
}


def check_integer_range(value: int, minimum: int, maximum: int) -> bool:
    if value < minimum or value > maximum:
        return False
    return True


def send_absolute_data(
    serial_object: Serial,
    x: int,
    y: int,
    button_name: str = "null",
    x_max: int = 1920,
    y_max: int = 1080,
    wheel_value: int = 0,
) -> None:
    if not check_integer_range(x_max, 0, 4096):
        raise exceptions.InvalidCoordinateValue(
            "Max coordinate value should be between 0 and 4096"
        )
    if not check_integer_range(y_max, 0, 4096):
        raise exceptions.InvalidCoordinateValue(
            "Max coordinate value should be between 0 and 4096"
        )
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x04",
        b"",
        b"",
    )
    # CMD_SEND_MS_ABS_DATA requires 7 bytes data
    # first byte is always 0x02
    buffer = b"\x02"

    # second byte is mouse button value
    buffer += MOUSE_BUTTON_NAME_MAP[button_name]

    # third and fourth bytes are x-coordinates
    x_value = (4096 * x) // x_max
    buffer += x_value.to_bytes(2, byteorder="little")

    # fifth and sixth bytes are y-coordinates
    y_value = (4096 * y) // y_max
    buffer += y_value.to_bytes(2, byteorder="little")

    # seventh byte contains wheel data
    # If it is 0x00, it means there is no scrolling action
    # 0x01-0x7F, means scroll up
    # 0x81-0xFF, means scroll down
    if not check_integer_range(wheel_value, -128, 127):
        raise exceptions.InvalidWheelValue("Wheel value should be between -127 and 128")
    buffer += wheel_value.to_bytes(1, byteorder="little", signed=True)
    data_frame.set_data(buffer)
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)


def send_relative_data(
    serial_object: Serial,
    x: int,
    y: int,
    button_name: str = "null",
    wheel_value: int = 0,
) -> None:
    data_frame = frame_utils.DataFrame(
        b"\x57\xab",
        b"\x00",
        b"\x05",
        b"",
        b"",
    )
    # CMD_SEND_MS_REL_DATA requires 5 bytes data
    # first byte is always 0x01
    buffer = b"\x01"
    buffer += MOUSE_BUTTON_NAME_MAP[button_name]

    # x value
    if not check_integer_range(x, -128, 127):
        raise exceptions.InvalidCoordinateValue(
            "Coordinate value should be between -127 and 128"
        )
    buffer += x.to_bytes(1, byteorder="little", signed=True)
    # y value
    if not check_integer_range(y, -128, 127):
        raise exceptions.InvalidCoordinateValue(
            "Coordinate value should be between -127 and 128"
        )
    buffer += y.to_bytes(1, byteorder="little", signed=True)

    # wheel value
    if not check_integer_range(wheel_value, -128, 127):
        raise exceptions.InvalidWheelValue("Wheel value should be between -127 and 128")
    buffer += wheel_value.to_bytes(1, byteorder="little", signed=True)

    data_frame.set_data(buffer)
    request_packet = data_frame.create_frame()
    serial_object.write(request_packet)


def move(
    serial_object: Serial,
    x: int,
    y: int,
    relative_mode: bool = False,
    monitor_width: int = 1920,
    monitor_height: int = 1080,
) -> None:
    if relative_mode:
        send_relative_data(serial_object, x, y, "null")
    else:
        send_absolute_data(serial_object, x, y, "null", monitor_width, monitor_height)


def press(serial_object: Serial, button_name: str = "left") -> None:
    send_relative_data(serial_object, 0, 0, button_name, 0)


def release(serial_object: Serial) -> None:
    send_relative_data(serial_object, 0, 0, "null", 0)


def click(serial_object: Serial, button_name: str = "left") -> None:
    press(serial_object, button_name)
    # 100 to 400 milliseconds delay for simulating natural behavior
    sleep_time = random.uniform(0.20, 0.40)
    time.sleep(sleep_time)
    release(serial_object)


def wheel(serial_object: Serial, wheel_value: int = 1) -> None:
    send_relative_data(serial_object, 0, 0, "null", wheel_value=wheel_value)


if __name__ == "__main__":
    pass
