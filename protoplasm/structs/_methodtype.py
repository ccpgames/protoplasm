__all__ = [
    'MethodIoType',
]

import enum


class MethodIoType(enum.IntFlag):
    _UNKNOWN = 0b0000  # 0
    _INPUT_UNARY = 0b0001  # 1
    _INPUT_STREAM = 0b0010  # 2
    _INPUT_MASK = 0b0011  # 3

    _OUTPUT_UNARY = 0b0100  # 4
    _OUTPUT_STREAM = 0b1000  # 8
    _OUTPUT_MASK = 0b1100  # 12

    UNARY_IN_UNARY_OUT = _INPUT_UNARY | _OUTPUT_UNARY    # 0b0101  # 5
    UNARY_IN_STREAM_OUT = _INPUT_UNARY | _OUTPUT_STREAM   # 0b0110  # 6
    STREAM_IN_UNARY_OUT = _INPUT_STREAM | _OUTPUT_UNARY   # 0b1001  # 9
    STREAM_IN_STREAM_OUT = _INPUT_STREAM | _OUTPUT_STREAM  # 0b1010  # 10

    def is_valid(self) -> bool:
        return self.value in (self.UNARY_IN_UNARY_OUT.value,
                              self.UNARY_IN_STREAM_OUT.value,
                              self.STREAM_IN_UNARY_OUT.value,
                              self.STREAM_IN_STREAM_OUT.value)

    def is_input_stream(self) -> bool:
        return (self.value & self._INPUT_STREAM) == self._INPUT_STREAM

    def is_output_stream(self) -> bool:
        return (self.value & self._OUTPUT_STREAM) == self._OUTPUT_STREAM
