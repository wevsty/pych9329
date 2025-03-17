import serial
import serial.tools.list_ports
from serial import Serial

from pych9329.chip_command import get_chip_parameters
from pych9329.chip_command import send_command_reset
from pych9329.chip_command import set_chip_parameters


def main():
    comports = serial.tools.list_ports.comports()
    for device in comports:
        try:
            print("serial device pid:%s vid:%s" % (device.pid, device.vid))
            print("open serial device: %s" % device.device)
            ser = Serial(device.device, 9600, timeout=1.0)
            chip_parameters = get_chip_parameters(ser)
            # Update baud rate to 57600
            # chip_parameters.attribute['serial_baud_rate'] = 57600
            ret = set_chip_parameters(ser, chip_parameters)
            if ret:
                print("set chip parameters succeed.")
            else:
                print("set chip parameters failed.")
            print("send reset command")
            send_command_reset(ser)
            ser.close()
        except serial.serialutil.SerialException as err:
            print(err)


if __name__ == "__main__":
    main()
