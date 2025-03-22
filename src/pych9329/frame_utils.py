from dataclasses import dataclass
from enum import Enum


class DataFrameStatus(Enum):
    SUCCESS = b"\x00"
    ERROR_TIMEOUT = b"\xe1"
    ERROR_HEAD = b"\xe2"
    ERROR_CMD = b"\xe3"
    ERROR_SUM = b"\xe4"
    ERROR_PARA = b"\xe5"
    ERROR_OPERATE = b"\xe6"


@dataclass
class DataFrame:
    HEAD: bytes
    ADDR: bytes
    CMD: bytes
    LEN: bytes = b"\x00"
    DATA: bytes = b""

    def create_frame(self) -> bytes:
        checksum = self.calc_checksum()
        frame = (
            self.HEAD + self.ADDR + self.CMD + self.LEN + self.DATA + bytes([checksum])
        )
        return frame

    def get_data(self) -> bytes:
        return self.DATA

    def get_data_length(self) -> int:
        length = int.from_bytes(self.LEN, byteorder="big")
        return length

    def set_data(self, data: bytes) -> None:
        self.DATA = data
        self.set_data_length(len(data))

    def set_data_length(self, length: int) -> None:
        self.LEN = int.to_bytes(length, byteorder="big")

    def calc_frame_length(self, buffer: bytes) -> int:
        header_size = 5
        frame_length = 0
        buffer_length = len(buffer)
        if buffer_length < header_size:
            return frame_length
        head_first = buffer[0:1]
        head_last = buffer[1:2]
        self.ADDR = buffer[2:3]
        self.CMD = buffer[3:4]
        self.LEN = buffer[4:5]
        self.HEAD = head_first + head_last
        data_length = self.get_data_length()
        frame_length = header_size + data_length + 1
        return frame_length

    def calc_checksum(self) -> int:
        head_list = list(self.HEAD)
        head_sum = sum(head_list)
        data_list = list(self.DATA)
        data_sum = sum(data_list)
        checksum = (
            sum(
                [
                    head_sum,
                    int.from_bytes(self.ADDR, byteorder="big"),
                    int.from_bytes(self.CMD, byteorder="big"),
                    int.from_bytes(self.LEN, byteorder="big"),
                    data_sum,
                ]
            )
            % 256
        )
        return checksum

    def parse_frame(self, buffer: bytes) -> bool:
        header_size = 5
        parse_result = False
        buffer_length = len(buffer)
        if buffer_length < header_size:
            return parse_result
        frame_length = self.calc_frame_length(buffer)
        if buffer_length < frame_length:
            return parse_result
        data_length = self.get_data_length()
        if data_length >= 0:
            self.DATA = buffer[header_size : header_size + data_length]
            _checksum = buffer[
                header_size + data_length : header_size + data_length + 1
            ]
            parse_result = True
        return parse_result


if __name__ == "__main__":
    pass
