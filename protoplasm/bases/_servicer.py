__all__ = [
    'BaseGrpcServicer',
]
import grpc  # noqa

from protoplasm.structs import *
from .dataclass_bases import *
from ._methwrap import *


class BaseGrpcServicer:
    def __init__(self, implementation, *args, **kwargs):
        self.impl = implementation

    def add_to_server(self, server):
        raise NotImplementedError()

    def _forward_to_impl(self, data_cls: Type[T_DCB], impl_method: Callable,
                         request: GeneratedProtocolMessageType,
                         context: grpc.ServicerContext) -> GeneratedProtocolMessageType:
        """Alias to _forward_to_unary_unary_impl for backwards compatibility"""
        return self._forward_to_unary_unary_impl(data_cls, impl_method, request, context)

    def _forward_to_unary_unary_impl(self, data_cls: Type[T_DCB], impl_method: Callable,
                                     request: GeneratedProtocolMessageType,
                                     context: grpc.ServicerContext) -> GeneratedProtocolMessageType:
        return PlasmMethodWrapper(self, data_cls, impl_method, request, context,
                                  MethodIoType.UNARY_IN_UNARY_OUT).call()

    def _forward_to_unary_stream_impl(self, data_cls: Type[T_DCB], impl_method: Callable,
                                      request: GeneratedProtocolMessageType,
                                      context: grpc.ServicerContext) -> Iterable[GeneratedProtocolMessageType]:
        return PlasmMethodWrapper(self, data_cls, impl_method, request, context,
                                  MethodIoType.UNARY_IN_STREAM_OUT).call()

    def _forward_to_stream_unary_impl(self, data_cls: Type[T_DCB], impl_method: Callable,
                                      request_iterator: Iterable[GeneratedProtocolMessageType],
                                      context: grpc.ServicerContext):
        return PlasmMethodWrapper(self, data_cls, impl_method, request_iterator, context,
                                  MethodIoType.STREAM_IN_UNARY_OUT).call()

    def _forward_to_stream_stream_impl(self, data_cls: Type[T_DCB], impl_method: Callable,
                                       request_iterator: Iterable[GeneratedProtocolMessageType],
                                       context: grpc.ServicerContext) -> Iterable[GeneratedProtocolMessageType]:
        return PlasmMethodWrapper(self, data_cls, impl_method, request_iterator, context,
                                  MethodIoType.STREAM_IN_STREAM_OUT).call()
