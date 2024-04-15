__all__ = [
    'IResponseIterator',
    'ResponseIterator',
    'TimeoutResponseIterator',
]
import abc
from ._base import *
from protoplasm.errors import *
from .dataclassbase import T_DCB
import threading
import grpc  # noqa

import logging
log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from protoplasm.bases._remotewrap import RemoteMethodWrapper  # noqa


class IResponseIterator(Iterable, abc.ABC):
    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def next(self) -> Optional[T_DCB]:
        pass

    def __iter__(self):
        return self

    def __next__(self) -> T_DCB:
        n = self.next()
        if n is None:
            raise StopIteration()
        return n


class ResponseIterator(IResponseIterator, Generic[T_DCB]):
    __slots__ = ('_wrapper', '_response_iterator')

    def __init__(self, remote_wrapper: 'RemoteMethodWrapper'):
        """Super simple basic Response Iterator to wrap gRPC RPC stream responses.

        Can be used as an iterator directly in a loop or by calling `next()`
        directly to get the next iteration from the result stream.

        Note that `next()` will simply block until it receives a value to return
        from the stream (unless the stream has been closed in which case
        `next()` returns None).
        """
        self._wrapper = remote_wrapper
        self._response_iterator = iter(remote_wrapper.iterable_results)

    def close(self):
        """Cancels the RPC call mid-stream.
        """
        self._wrapper.close()

    def next(self) -> Optional[T_DCB]:
        if self._wrapper.is_closed:
            return None
        return next(self._response_iterator)

    def with_timeout(self, timeout_seconds: Optional[float] = None,
                     raise_timeout: Optional[bool] = None) -> 'TimeoutResponseIterator':
        return TimeoutResponseIterator(self, timeout_seconds, raise_timeout)

    def one_and_done(self, timeout_seconds: Optional[float] = 0,
                     raise_timeout: Optional[bool] = None) -> Optional[T_DCB]:
        """Waits for a single iteration from the stream to return and then closes the stream.

        Note the default timeout of 0, meaning this will wait forever by default!
        """
        return self.with_timeout(timeout_seconds, raise_timeout).one_and_done()


class TimeoutResponseIterator(IResponseIterator, Generic[T_DCB]):
    __slots__ = ('_response_iterator', '_timeout_seconds', '_timeout_thread', '_next',
                 '_exception', '_timed_out', '_raise_timeout')

    def __init__(self, response_iterator: ResponseIterator[T_DCB],
                 timeout_seconds: float = 60.0, raise_timeout: bool = True):
        """Response Iterator wrapper with builtin timeout (deadline)
        while waiting for next stream iteration.

        Can be used as an iterator directly in a loop or by calling `next()`
        directly to get the next iteration from the result stream.

        Note that `next()` will block until it receives a value to return
        from the stream OR it times out.

        If raise_timeout is True then a ResponseIterationTimoutError will be
        raised in case of a timeout but if not, then the iteration loop will
        simply end if this is used as such (StopIteration is raised) or the
        timed-out `next()` call returns None.
        """
        self._response_iterator: ResponseIterator = response_iterator
        self._timeout_seconds = timeout_seconds
        if self._timeout_seconds is None:
            self._timeout_seconds = 60.0
        self._timeout_thread: Optional[threading.Thread] = None
        self._next: Optional[T_DCB] = None
        self._exception: Optional[Exception] = None
        self._timed_out: bool = False
        self._raise_timeout = raise_timeout
        if self._raise_timeout is None:
            self._raise_timeout = True

    def next(self, timeout_seconds: Optional[float] = None, raise_timeout: Optional[bool] = None) -> Optional[T_DCB]:
        """The `timeout_seconds` and `raise_timeout` parameters are optional
        and override the wrappers default ones given when it was initialized.

        Returns None if `raise_timeout` is False.
        """
        self._next = None
        self._exception = None
        self._timed_out = False
        if timeout_seconds is None:
            timeout_seconds = self._timeout_seconds
        if raise_timeout is None:
            raise_timeout = self._raise_timeout
        if not timeout_seconds:  # Just wait forever! :D
            return self._response_iterator.next()

        self._timeout_thread = threading.Thread(target=self._wait_for_next)
        self._timeout_thread.start()
        self._timeout_thread.join(timeout_seconds)
        if self._timeout_thread.is_alive():
            log.info('thread is still alive... closing!')
            self._timed_out = True
            self.close()
            if raise_timeout:
                raise ResponseIterationTimoutError(f'timout while waiting for next response from'
                                                   f' {self._response_iterator._wrapper.method_name}')  # noqa
            else:
                log.info(f'stopping iteration after timeout')
                return None

        if self._exception:  # Something bad happened!
            raise self._exception

        return self._next  # noqa

    def _wait_for_next(self):
        log.info('_wait_for_next started...')
        try:
            self._next = self._response_iterator.next()
            log.info('_next happened!!')
        except grpc.RpcError as ex:
            from protoplasm.bases._exwrap import GrpcExceptionWrapper  # noqa
            wrex = GrpcExceptionWrapper(ex)
            if wrex.code == grpc.StatusCode.CANCELLED and self._timed_out:
                log.info(f'Self inflicted timeout in thread')
                return  # this means we timed out and cancelled this ourselves!
            log.exception(f'RpcError in thread: {ex!r}')
            self._exception = wrex.get_reraise()
        except Exception as ex:
            log.exception(f'Exception in thread: {ex!r}')
            self._exception = ex
        log.info('_wait_for_next ended!!')

    def close(self):
        self._response_iterator.close()

    def one_and_done(self, timeout_seconds: Optional[float] = None,
                     raise_timeout: Optional[bool] = None) -> Optional[T_DCB]:
        """Waits for a single iteration from the stream to return and then closes the stream.
        """
        the_one = self.next(timeout_seconds, raise_timeout)
        self.close()
        return the_one
