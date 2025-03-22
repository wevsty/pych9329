# pych9329
Python module to control ch9329

## Installation

You can install the package via pip:

```bash
pip install pych9329
```

## Usage

```py
from serial import Serial

from pych9329 import keyboard
from pych9329 import mouse
from pych9329 import chip_command


def main():
    ser = Serial("COM10", 9600, timeout=0.50)

    # Receive the keyboard lock status
    result, kb_status = keyboard.receive_indicator_status(ser)
    if result:
        # {'usb_connect_status': True, 'num_lock': True, 'caps_lock': False, 'scroll_lock': False}
        print(kb_status)
        # Automatically turn off caps_lock
        if kb_status["caps_lock"]:
            keyboard.click(ser, "caps_lock")

    keyboard.click(ser, "a")
    keyboard.click(ser, "A")
    keyboard.send_text(ser, "\n")
    keyboard.send_text(ser, "Hello World\n")
    keyboard.send_text(ser, "abcdefghijklmnopqrstuvwxyz\n")
    keyboard.send_text(ser, "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n")
    keyboard.send_text(ser, "0123456789\n")
    keyboard.send_text(ser, "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n")

    mouse.move(ser, x=500, y=500)
    mouse.move(ser, x=50, y=50, relative_mode=True)
    # For supported key names, please see mouse.MOUSE_BUTTON_NAME_MAP
    mouse.click(ser, button_name="left")

    # 2019A152BB40
    print(chip_command.get_serial_number(ser))
    # WCH UART TO KB-MS_V1.8
    print(chip_command.get_product(ser))
    # WWW.WCH.CN
    print(chip_command.get_manufacturer(ser))
    ser.close()


if __name__ == "__main__":
    main()

```

## License

MIT license.

## Contributing

This project is modified from ch9329 library.

Thanks to the original author of the ch9329 library [Pradish Bijukchhe](https://github.com/pradishb)
