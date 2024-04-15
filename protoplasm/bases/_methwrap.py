__all__ = [
    'PlasmMethodWrapper',
]

import grpc
import json
import uuid

from ccptools.tpu import casting as typeutils_casting

from protoplasm import casting
from protoplasm import errors
from protoplasm.bases.dataclass_bases import *
from protoplasm.structs import *

if TYPE_CHECKING:
    from .grpc_bases import BaseGrpcServicer

import logging
log = logging.getLogger(__name__)


class PlasmMethodWrapper:
    JSON_SERIALIZER = typeutils_casting.JsonSafeSerializer()

    __slots__ = ('servicer', 'data_cls', 'impl_method', 'request', 'request_iterator', 'context', 'request_dc',
                 'unpacked_args', 'raw_response_iterable', 'raw_response', 'response_dc', 'response_proto',
                 '_ref_code', 'method_io')

    def __init__(self, servicer: 'BaseGrpcServicer', data_cls: Type[T_DCB], impl_method: Callable,
                 request_or_iterator: Union[GeneratedProtocolMessageType, Iterable[GeneratedProtocolMessageType]],
                 context: grpc.ServicerContext, method_io: MethodIoType):
        """Container and worker for processing Servicer (i.e. Server Side)
        requests and responses, packing, unpacking, casting and so on as well as
        handling errors and log-dumping and all that bulky noisy jass that just
        clutters up the actual servicer code.
        """
        self.servicer: 'BaseGrpcServicer' = servicer
        self.data_cls: Type[DataclassBase] = data_cls
        self.impl_method: Callable = impl_method

        self.request: Optional[GeneratedProtocolMessageType] = None
        self.request_iterator: Optional[Iterable[GeneratedProtocolMessageType]] = None

        self.context: grpc.ServicerContext = context
        self.method_io: MethodIoType = method_io

        if self.method_io.is_input_stream():
            self.request_iterator = request_or_iterator
        else:
            self.request = request_or_iterator

        self.request_dc: Optional[DataclassBase] = None
        self.unpacked_args: Optional[Dict] = None
        self.raw_response_iterable: Optional[Iterable[Any]] = None
        self.raw_response: Any = None
        self.response_dc: Optional[DataclassBase] = None
        self.response_proto: Optional[GeneratedProtocolMessageType] = None
        self._ref_code: str = ''

    @property
    def request_dc_iterator(self) -> Iterable[T_DCB]:
        for raw_req in self.request_iterator:
            self.request = raw_req
            self._p2d()
            yield self.request_dc

    @property
    def ref_code(self) -> str:
        if not self._ref_code:
            self._ref_code = str(uuid.uuid4())
        return self._ref_code

    def _get_dump(self, **kwargs) -> dict:
        d = {
            'ref_code': self.ref_code,
            'class': str(self.servicer.__class__),
            'data_cls': str(self.data_cls),
            'impl_method': str(self.impl_method),
            'request': str(self.request),
            'method_io': self.method_io,
        }

        if self.context:
            try:
                d['invocation_metadata'] = dict(self.context.invocation_metadata())  # noqa
            except Exception:
                d['invocation_metadata'] = 'FAILED TO FETCH METADATA!'

        if self.request_dc:
            d['request_dc'] = repr(self.request_dc)
        if self.unpacked_args:
            d['unpacked_args'] = self.unpacked_args
        if self.raw_response:
            d['raw_response'] = repr(self.raw_response)
        if self.response_dc:
            d['response_dc'] = repr(self.response_dc)
        if self.response_proto:
            d['response_proto'] = repr(self.response_proto)

        if kwargs:
            d.update(kwargs)

        return d

    def _get_json_dump(self, **kwargs) -> str:
        return json.dumps(self.JSON_SERIALIZER.serialize(self._get_dump(**kwargs)), indent=4)

    def _abort(self, message: str, error_code, ex):
        self.context.set_trailing_metadata([('ref_code', self.ref_code)])
        log.exception(f'{message}::{ex!r}\n---\n{self._get_json_dump(details=repr(ex))}')
        return self.context.abort(error_code, f'{ex!r};\nref_code={self.ref_code}')

    def _abort_internal(self, ex: errors.ServiceApiException):
        details = [ex.details]
        if ex.should_log:
            details.append(f'ref_code={self.ref_code}')
            self.context.set_trailing_metadata([('ref_code', self.ref_code)])
            log.exception(f'Logging ServiceApiException::{ex!r}\n---\n'
                          f'{self._get_json_dump(status_code=ex.status_code, details=ex.details)}')
        return self.context.abort(ex.status_code, ';\n'.join(details))

    def _p2d(self):
        try:
            self.request_dc = casting.proto_to_dataclass(self.request)
        except Exception as ex:
            return self._abort('pre_request_error;Error while casting proto to dataclass',
                               grpc.StatusCode.FAILED_PRECONDITION, ex)

    def _unpack(self):
        try:
            if self.method_io.is_input_stream():
                self.unpacked_args = {'request_iterator': self.request_dc_iterator}
            else:
                self.unpacked_args = self.request_dc.unpack()
        except Exception as ex:
            return self._abort('pre_request_error;Error while unpacking arguments',
                               grpc.StatusCode.FAILED_PRECONDITION, ex)

    def _add_ctx(self):
        try:
            ctx_name = getattr(self.impl_method, '__takes_context_as__', False)
            if ctx_name:
                self.unpacked_args[ctx_name] = GrpcContext(self.context, self.method_io)
        except Exception as ex:
            return self._abort('pre_request_error;Error while adding context to parameters',
                               grpc.StatusCode.FAILED_PRECONDITION, ex)

    def prepare(self):
        if not self.method_io.is_input_stream():
            self._p2d()
        self._unpack()
        self._add_ctx()

    def _pack(self):
        self.response_dc = None
        try:
            self.response_dc = casting.pack_dataclass_response(self.data_cls, self.raw_response)
        except Exception as ex:
            return self._abort('post_request_error;Error while packing raw response to dataclass',
                               grpc.StatusCode.CANCELLED, ex)

    def _d2p(self):
        self.response_proto = None
        try:
            self.response_proto = casting.dataclass_to_proto(self.response_dc)
        except Exception as ex:
            return self._abort('post_request_error;Error while casting dataclass to proto',
                               grpc.StatusCode.CANCELLED, ex)

    def call(self) -> Union[GeneratedProtocolMessageType,
                            Iterable[GeneratedProtocolMessageType]]:
        # Prepare the call
        self.prepare()

        try:
            if self.method_io.is_output_stream():
                self.raw_response_iterable = self.impl_method(**self.unpacked_args)

            else:
                self.raw_response = self.impl_method(**self.unpacked_args)

        except errors.ServiceApiException as ex:
            return self._abort_internal(ex)

        except Exception as ex:
            return self._abort('Unexpected exception in implementation method',
                               grpc.StatusCode.UNKNOWN, ex)

        if not self.method_io.is_output_stream():
            # Pack up results for unary results
            self._pack()
            self._d2p()
            return self.response_proto

        else:
            return self.iterable_response_proto

    @property
    def wrapped_iterable_raw_response(self) -> Iterable[Any]:
        try:
            for res in self.raw_response_iterable:
                yield res
        except errors.ServiceApiException as ex:
            return self._abort_internal(ex)
        except Exception as ex:
            return self._abort('Unexpected exception in implementation method',
                               grpc.StatusCode.UNKNOWN, ex)

    @property
    def iterable_response_proto(self) -> Iterable[GeneratedProtocolMessageType]:
        for res in self.wrapped_iterable_raw_response:
            self.raw_response = res
            self._pack()
            self._d2p()
            yield self.response_proto

            self.raw_response = None
            self.response_dc = None
            self.response_proto = None
