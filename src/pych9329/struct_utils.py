import struct
import typing
import pych9329.exceptions as exceptions
from typing import Any


class StructureMeta(type):
    def __init__(
        cls, _cls_name: str, _bases: tuple[type, ...], _cls_dict: dict[str, Any]
    ):
        super().__init__(cls)
        fields = getattr(cls, "_fields_", [])

        offset = 0
        for field_format, field_name in fields:
            if field_format.startswith(("<", ">", "!", "@")):
                byte_order = field_format[0]
                field_format = field_format[1:]
            else:
                byte_order = ""
            field_format = byte_order + field_format
            offset += struct.calcsize(field_format)
        setattr(cls, "_fields_struct_size_", offset)


class Structure(metaclass=StructureMeta):
    def __init__(self, data: bytes):
        self.buffer = data
        self.attribute = dict()
        self.load()

    def load(self):
        fields = self._fields_
        offset = 0
        for field_format, field_name in fields:
            field_length = struct.calcsize(field_format)
            field_data = struct.unpack_from(field_format, self.buffer, offset)
            if len(field_data) == 1:
                self.attribute[field_name] = field_data[0]
            elif len(field_data) == field_length:
                buffer = bytearray()
                for item in field_data:
                    buffer += item
                self.attribute[field_name] = bytes(buffer)
            else:
                self.attribute[field_name] = None
            offset += struct.calcsize(field_format)

    def save(self):
        fields = self._fields_
        binary_data = bytearray()
        for field_format, field_name in fields:
            field_data = self.attribute[field_name]
            field_bytes = struct.pack(field_format, field_data)
            binary_data += bytearray(field_bytes)
        self.buffer = bytes(binary_data)

    def get(self, key: str) -> Any:
        data = self.attribute.get(key, None)
        return data

    def set(self, key: str, value: Any) -> None:
        self.attribute[key] = value

    def buffer_load(self, buffer: bytes) -> None:
        self.buffer = buffer
        self.attribute.clear()
        self.load()

    def buffer_flush(self) -> None:
        self.save()

    @classmethod
    def from_buffer(cls, buffer: bytes):
        buffer_len = len(buffer)
        if buffer_len >= cls._fields_struct_size_:
            return cls(buffer)
        else:
            raise exceptions.BufferTooSmall()

    @classmethod
    def from_file(cls, buffer: typing.BinaryIO):
        return cls(buffer.read(cls._fields_struct_size_))


"""
class ExampleStruct(Structure):
    _fields_ = [
        ('d', 'min_x'),
        ('d', 'min_y'),
    ]
"""

if __name__ == "__main__":
    pass
