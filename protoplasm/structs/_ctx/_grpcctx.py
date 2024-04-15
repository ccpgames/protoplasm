__all__ = [
    'GrpcContext',
]

import re
import grpc
from ._basectx import *
from protoplasm.structs._methodtype import *


class GrpcContext(BaseContext):
    IP_MATCHER = re.compile(r'(?:(?P<ipv>ipv[46]):)?(?P<ip>(?:\[?[\da-f]{0,4}(?::[\da-f]{0,4}){2,8}]?)|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?P<port>:\d{1,5})?', re.IGNORECASE)

    def __init__(self, wrapped_context: grpc.ServicerContext, method_io: MethodIoType = None):
        super().__init__(wrapped_context)
        self.metadata = {}
        self.method_io = method_io or MethodIoType._UNKNOWN  # noqa
        self._load_metadata()
        self._origin_ip = None

    def _load_metadata(self):
        self.metadata = {}
        for k, v in self.wrapped_context.invocation_metadata():
            k = k.lower()
            if k not in self.metadata:
                self.metadata[k] = v
            else:
                if not isinstance(self.metadata[k], list):
                    self.metadata[k] = [self.metadata[k]]
                self.metadata[k].append(v)

    def get_origin_ip(self, default=None):
        if not self._origin_ip:
            if self._origin_ip is False:
                return default
            # Try x-forwarded!
            self._origin_ip = self.get_meta('x-forwarded-for', None)
            if not self._origin_ip:
                # If not, try peer
                peer = self.wrapped_context.peer()
                if peer:
                    m = GrpcContext.IP_MATCHER.match(peer)
                    if m:
                        self._origin_ip = m.group('ip')
            if not self._origin_ip:
                self._origin_ip = False
        return self._origin_ip

    def get_meta(self, name, default=None):
        return self.metadata.get(name, default)

    def __repr__(self):
        return 'GrpcContext[metadata=%r, peer=%r]' % (self.metadata, self.wrapped_context.peer())
