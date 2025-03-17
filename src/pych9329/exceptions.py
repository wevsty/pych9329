class ChipBaseException(Exception):
    pass


# 协议错误
class ProtocolError(ChipBaseException):
    pass


# 无效的字符串编码
class InvalidStringEncoding(ChipBaseException):
    pass


# 无效的字符串长度
class InvalidStringLength(ChipBaseException):
    pass


# 无效的坐标值
class InvalidCoordinateValue(ChipBaseException):
    pass


# 无效的滚轮值
class InvalidWheelValue(ChipBaseException):
    pass


# 无效的特殊按键
class InvalidModifierKey(ChipBaseException):
    pass


# 无效的按键
class InvalidKey(ChipBaseException):
    pass


# 传入太多按键
class TooManyKeys(ChipBaseException):
    pass


# 缓冲区太小
class BufferTooSmall(ChipBaseException):
    pass

if __name__ == '__main__':
    pass
