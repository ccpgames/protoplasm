__all__ = [
    'RequestIterator',
]
from ._base import *
from .dataclassbase import T_DCB
import queue


class RequestIterator(Generic[T_DCB]):
    def __init__(self, initial_request: Optional[Union[T_DCB, List[T_DCB], Tuple[T_DCB]]] = None):
        self._queue = queue.SimpleQueue()
        if initial_request:
            if isinstance(initial_request, (list, tuple)):
                for ir in initial_request:
                    self.send(ir)
            else:
                self.send(initial_request)
        self._do_cancel: bool = False

    def close(self):
        self._do_cancel = True

    def send(self, request: T_DCB):
        self._queue.put(request)

    def __iter__(self):
        return self

    def __next__(self) -> T_DCB:
        if self._do_cancel:
            raise StopIteration()
        return self._queue.get(block=True)
