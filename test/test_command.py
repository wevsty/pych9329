from serial import Serial

from pych9329.chip_command import get_chip_parameters
from pych9329.chip_command import send_command_reset
from pych9329.chip_command import send_command_restore_factory_config
from pych9329.chip_command import set_chip_parameters


class TestChipCommand:

    @staticmethod
    def load_shared_data(shared_datadir, filename) -> bytes:
        data_path = shared_datadir / filename
        with open(data_path, "rb") as f:
            return f.read()

    def test_chip_command_reset(self, mocker):
        serial_object = Serial()
        serial_object.write = mocker.patch.object(
            serial_object, "write", return_value=None
        )
        send_command_reset(serial_object)
        serial_object.write.assert_called_once_with(b"\x57\xab\x00\x0f\x00\x11")

    def test_chip_command_restore_factory(self, mocker):
        serial_object = Serial()
        serial_object.write = mocker.patch.object(
            serial_object, "write", return_value=None
        )
        send_command_restore_factory_config(serial_object)
        serial_object.write.assert_called_once_with(b"\x57\xab\x00\x0c\x00\x0e")

    def test_chip_command_chip_parameters(self, mocker, shared_datadir):
        get_parameters_read_packet_data = self.load_shared_data(
            shared_datadir, "get_parameters_read_packet.bin"
        )
        set_parameters_read_packet_data = self.load_shared_data(
            shared_datadir, "set_parameters_read_packet.bin"
        )
        set_parameters_write_packet_data = self.load_shared_data(
            shared_datadir, "set_parameters_write_packet.bin"
        )

        serial_object = Serial()
        serial_object.write = mocker.patch.object(
            serial_object, "write", return_value=None
        )
        serial_object.read = mocker.patch.object(
            serial_object, "read", return_value=get_parameters_read_packet_data
        )
        serial_object.flush = mocker.patch.object(
            serial_object, "flush", return_value=None
        )
        parameters = get_chip_parameters(serial_object)
        serial_object.write.assert_called_once_with(b"\x57\xab\x00\x08\x00\x0a")
        assert parameters.get("serial_baud_rate") == 9600
        assert parameters.get("usb_vid") == 6790
        assert parameters.get("usb_pid") == 57641
        # test set
        serial_object.write.reset_mock()
        serial_object.read.reset_mock()
        serial_object.read.return_value = set_parameters_read_packet_data
        set_chip_parameters(serial_object, parameters)
        serial_object.write.assert_called_once_with(set_parameters_write_packet_data)


if __name__ == "__main__":
    pass
