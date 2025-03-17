from serial import Serial

from pych9329 import keyboard
from pych9329 import mouse
from pych9329.chip_command import get_manufacturer
from pych9329.chip_command import get_product
from pych9329.chip_command import get_serial_number


def main():
    ser = Serial("COM10", 9600, timeout=0.50)

    keyboard.click(ser, "a")
    keyboard.click(ser, "A")
    keyboard.send_text_data(ser, "\n")
    keyboard.send_text_data(ser, "Hello World\n")
    keyboard.send_text_data(ser, "abcdefghijklmnopqrstuvwxyz\n")
    keyboard.send_text_data(ser, "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n")
    keyboard.send_text_data(ser, "0123456789\n")
    keyboard.send_text_data(ser, "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n")

    mouse.move(ser, x=500, y=500)
    mouse.move(ser, x=50, y=50, relative_mode=True)
    # For supported key names, please see mouse.MOUSE_BUTTON_NAME_MAP
    mouse.click(ser, button_name="left")

    # 2019A152BB40
    print(get_serial_number(ser))
    # WCH UART TO KB-MS_V1.8
    print(get_product(ser))
    # WWW.WCH.CN
    print(get_manufacturer(ser))
    ser.close()


if __name__ == "__main__":
    main()
