__all__ = [
    'RemoteMethodWrapper',
]
import json
import uuid

import grpc  # noqa
from grpc._channel import _UnaryUnaryMultiCallable as _UnaryUnaryStub  # noqa
from grpc._channel import _UnaryStreamMultiCallable as _UnaryStreamStub  # noqa
from grpc._channel import _StreamUnaryMultiCallable as _StreamUnaryStub  # noqa
from grpc._channel import _StreamStreamMultiCallable as _StreamStreamStub  # noqa

from ccptools.tpu import casting as typeutils_casting

from protoplasm.structs import *
from protoplasm import casting
from protoplasm import errors

from .dataclass_bases import *
from ._exwrap import *

import logging
log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .grpc_bases import BaseGrpcClientImplementation
    from grpc._channel import _MultiThreadedRendezvous  # noqa


class RemoteMethodWrapper:
    JSON_SERIALIZER = typeutils_casting.JsonSafeSerializer()

    __slots__ = ('client', 'request_cls', 'stub_method', 'args', 'kwargs',
                 'request_iterator', 'response_iterator', 'request_dc',
                 'request_proto', 'response_proto', 'response_dc',
                 'unpacked_results', 'method_io', '_ref_code')

    def __init__(self, client: 'BaseGrpcClientImplementation', request_cls: Type[T_DCB],
                 stub_method: Callable, *args, **kwargs):
        """Container and worker for processing BaseGrpcClient (i.e. Client Side)
        requests and responses, packing, unpacking, casting and so on as well as
        handling errors and log-dumping and all that bulky noisy jass that just
        clutters up the actual client code.
        """
        self.client: 'BaseGrpcClientImplementation' = client
        self.request_cls: Type[T_DCB] = request_cls
        self.stub_method: Callable = stub_method
        self.args: List[Any] = args or []
        self.kwargs: Dict[str, Any] = kwargs or {}

        self.request_iterator: Optional[Iterable[DataclassBase]] = None
        self.response_iterator: Optional['_MultiThreadedRendezvous'] = None

        self.request_dc: Optional[DataclassBase] = None
        self.request_proto: Optional[GeneratedProtocolMessageType] = None
        self.response_proto: Optional[GeneratedProtocolMessageType] = None
        self.response_dc: Optional[DataclassBase] = None
        self.unpacked_results: Optional[Any, Tuple[Any]] = None

        self.method_io: MethodIoType = MethodIoType._UNKNOWN  # noqa

        self._ref_code: str = ''
        self._eval_method_io()

    def _eval_method_io(self):
        if isinstance(self.stub_method, _UnaryUnaryStub):
            self.method_io = MethodIoType.UNARY_IN_UNARY_OUT

        elif isinstance(self.stub_method, _UnaryStreamStub):
            self.method_io = MethodIoType.UNARY_IN_STREAM_OUT

        elif isinstance(self.stub_method, _StreamUnaryStub):
            self.method_io = MethodIoType.STREAM_IN_UNARY_OUT

        elif isinstance(self.stub_method, _StreamStreamStub):
            self.method_io = MethodIoType.STREAM_IN_STREAM_OUT

        else:
            self._abort_preflight('Unable to determine stub method io channels (unary vs. stream)')

    @property
    def ref_code(self) -> str:
        if not self._ref_code:
            self._ref_code = str(uuid.uuid4())
        return self._ref_code

    @property
    def method_name(self) -> str:
        m = getattr(self.stub_method, '_method', str(self.stub_method))
        if isinstance(m, bytes):
            return m.decode()
        return m

    def _get_dump(self, **kwargs) -> dict:
        d = {
            'ref_code': self.ref_code,
            'class': str(self.client.__class__),
            'request_cls': str(self.request_cls),
            'method_name': self.method_name,
            'method_io': self.method_io
        }
        if self.args:
            d['args'] = repr(self.args)
        if self.kwargs:
            d['kwargs'] = repr(self.kwargs)

        if self.request_dc:
            d['request_dc'] = repr(self.request_dc)
        if self.request_proto:
            d['request_proto'] = repr(self.request_proto)

        if self.response_proto:
            d['response_proto'] = repr(self.response_proto)

        if self.response_dc:
            d['response_dc'] = repr(self.response_dc)

        if self.unpacked_results:
            d['unpacked_results'] = repr(self.unpacked_results)

        if kwargs:
            d.update(kwargs)

        return d

    def _get_json_dump(self, **kwargs) -> str:
        return json.dumps(self.JSON_SERIALIZER.serialize(self._get_dump(**kwargs)), indent=4)

    def _abort_preflight(self, message: str, ex: Optional[Exception] = None):
        if ex:
            log.exception(f'{message}::{ex!r}\n---\n{self._get_json_dump(details=repr(ex))}')
            raise_msg = f'{message}: {ex!r}'
        else:
            log.exception(f'{message}\n---\n{self._get_json_dump()}')
            raise_msg = message
        raise errors.api.PreRequestError(raise_msg, self.ref_code, True)

    def _abort_inflight(self, message: str, ex: grpc.RpcError):
        gex = GrpcExceptionWrapper(ex)
        reex = gex.get_reraise()
        if reex.should_log:
            d = dict(details=gex.details,
                     debug_message=gex.debug_error_string,
                     trailing_metadata=gex.trailing_metadata,
                     initial_metadata=gex.initial_metadata,
                     gex=gex,
                     status_code=gex.code,
                     ref_code=reex.ref_code)
            log.exception(f'{message}::{ex!r}\n---\n{self._get_json_dump(**d)}')
        raise reex

    def _abort_postflight(self, message: str, ex: Exception):
        log.exception(f'{message}::{ex!r}\n---\n{self._get_json_dump(details=repr(ex))}')
        raise errors.api.PostRequestError(f'{message}: {ex!r}', self.ref_code, True)

    def _abort(self, message: str, ex: Exception):
        log.exception(f'{message}::{ex!r}\n---\n{self._get_json_dump(details=repr(ex))}')
        raise errors.api.Unknown(f'{message}: {ex!r}', self.ref_code, True)

    def prepare(self):
        if not self.method_io.is_input_stream():
            self._mkdc()
            self._d2p()
        else:
            self._find_request_iterator()
            if isinstance(self.request_iterator, (list, tuple)):
                self.request_iterator = RequestIterator(self.request_iterator)

            elif isinstance(self.request_iterator, self.request_cls):
                self.request_iterator = RequestIterator(self.request_iterator)

    def _find_request_iterator(self):
        if not self.kwargs and self.args and len(self.args) == 1:
            self.request_iterator = self.args[0]
            return

        if not self.args and self.kwargs and len(self.kwargs) == 1 and 'request_iterator' in self.kwargs:
            self.request_iterator = self.kwargs['request_iterator']
            return

        self._abort_preflight('Expected a single arg or kwarg called "request_iterator" as input')

    @property
    def request_proto_iterator(self) -> Iterable[GeneratedProtocolMessageType]:
        for raw_req in self.request_iterator:
            self.request_dc = raw_req
            self._d2p()
            yield self.request_proto
        log.debug('Request Iterator Cancelled!')

    def _mkdc(self):
        try:
            self.request_dc = self.request_cls(*self.args, **self.kwargs)
        except Exception as ex:
            self._abort_preflight('Error while populating request class with arguments', ex)

    def _d2p(self):
        try:
            self.request_proto = self.request_dc.to_proto()
        except Exception as ex:
            self._abort_preflight('Error while casting request dataclass to proto', ex)

    def call(self) -> Optional[Union[ResponseIterator[T_DCB], Any, Tuple[Any]]]:
        # Prepare the call
        self.prepare()

        try:
            if self.method_io.is_input_stream():
                if self.method_io.is_output_stream():
                    self.response_iterator = self.stub_method(self.request_proto_iterator)
                else:
                    self.response_proto = self.stub_method(self.request_proto_iterator)

            else:
                if self.method_io.is_output_stream():
                    self.response_iterator = self.stub_method(self.request_proto)
                else:
                    self.response_proto = self.stub_method(self.request_proto)

        except grpc.RpcError as ex:
            self._abort_inflight('RpcError exception while performing gRPC request', ex)

        except Exception as ex:
            self._abort('Unknown exception while performing gRPC request', ex)

        if self.method_io.is_output_stream():
            return ResponseIterator(self)

        else:
            self._p2d()
            self._unpack()
            return self.unpacked_results

    @property
    def iterable_results(self) -> Iterable[T_DCB]:
        for raw_response in self.response_iterator:
            self.response_proto = raw_response
            self._p2d()
            yield self.response_dc

    def close(self):
        if self.response_iterator:
            self.response_iterator.cancel()

    @property
    def is_closed(self) -> Optional[bool]:
        if self.response_iterator:
            return self.response_iterator.cancelled()
        return None  # If we don't have a result stream this doesn't make sense

    def _p2d(self):
        try:
            self.response_dc = casting.proto_to_dataclass(self.response_proto)
        except Exception as ex:
            self._abort_postflight('Error while casting response proto to dataclass', ex)

    def _unpack(self):
        try:
            self.unpacked_results = self.response_dc.explode()
        except Exception as ex:
            self._abort_postflight('Error while unpacking dataclass arguments', ex)
