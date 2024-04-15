__all__ = [
    'GrpcExceptionWrapper',
]

import grpc
from typing import *
from protoplasm import errors

_STATUS_CODE_TO_EXCEPTION_MAP = {
    grpc.StatusCode.UNKNOWN: errors.api.Unknown,
    grpc.StatusCode.NOT_FOUND: errors.api.NotFound,
    grpc.StatusCode.INVALID_ARGUMENT: errors.api.InvalidArgument,
    grpc.StatusCode.UNIMPLEMENTED: errors.api.Unimplemented,
    grpc.StatusCode.PERMISSION_DENIED: errors.api.PermissionDenied,
    grpc.StatusCode.UNAUTHENTICATED: errors.api.Unauthenticated,
    grpc.StatusCode.UNAVAILABLE: errors.api.Unavailable,
    grpc.StatusCode.DEADLINE_EXCEEDED: errors.api.DeadlineExceeded,
    grpc.StatusCode.ALREADY_EXISTS: errors.api.AlreadyExists,
    grpc.StatusCode.FAILED_PRECONDITION: errors.api.FailedPrecondition,
    grpc.StatusCode.DATA_LOSS: errors.api.DataLoss,
    grpc.StatusCode.RESOURCE_EXHAUSTED: errors.api.ResourceExhausted,
    grpc.StatusCode.OUT_OF_RANGE: errors.api.OutOfRange,
    grpc.StatusCode.INTERNAL: errors.api.Internal,
    grpc.StatusCode.CANCELLED: errors.api.Cancelled,
    grpc.StatusCode.ABORTED: errors.api.Aborted,
}


class GrpcExceptionWrapper(object):
    def __init__(self, ex: grpc.RpcError):
        self.ex = ex
        self._code = False
        self._debug_error_string = False
        self._details = False
        self._initial_metadata = False
        self._traceback = False
        self._trailing_metadata = False

    @property
    def code(self) -> Optional[grpc.StatusCode]:
        if self._code is False:
            self._code = None
            code_call = getattr(self.ex, 'code', None)
            if code_call and hasattr(code_call, '__call__'):
                self._code = code_call()
        return self._code

    @property
    def debug_error_string(self) -> str:
        if self._debug_error_string is False:
            self._debug_error_string = ''
            code_call = getattr(self.ex, 'debug_error_string', None)
            if code_call and hasattr(code_call, '__call__'):
                self._debug_error_string = code_call()
        return self._debug_error_string

    @property
    def details(self) -> str:
        if self._details is False:
            self._details = ''
            code_call = getattr(self.ex, 'details', None)
            if code_call and hasattr(code_call, '__call__'):
                self._details = code_call()
        return self._details

    @property
    def initial_metadata(self) -> dict:
        if self._initial_metadata is False:
            self._initial_metadata = {}
            code_call = getattr(self.ex, 'initial_metadata', None)
            if code_call and hasattr(code_call, '__call__'):
                for k, v in code_call():
                    k = k.lower()
                    if k not in self._initial_metadata:
                        self._initial_metadata[k] = v
                    else:
                        if not isinstance(self._initial_metadata[k], list):
                            self._initial_metadata[k] = [self._initial_metadata[k]]
                        self._initial_metadata[k].append(v)
        return self._initial_metadata

    @property
    def traceback(self):
        if self._traceback is False:
            self._traceback = None
            code_call = getattr(self.ex, 'traceback', None)
            if code_call and hasattr(code_call, '__call__'):
                self._traceback = code_call()
        return self._traceback

    @property
    def trailing_metadata(self) -> dict:
        if self._trailing_metadata is False:
            self._trailing_metadata = {}
            code_call = getattr(self.ex, 'trailing_metadata', None)
            if code_call and hasattr(code_call, '__call__'):
                for k, v in code_call():
                    k = k.lower()
                    if k not in self._trailing_metadata:
                        self._trailing_metadata[k] = v
                    else:
                        if not isinstance(self._trailing_metadata[k], list):
                            self._trailing_metadata[k] = [self._trailing_metadata[k]]
                        self._trailing_metadata[k].append(v)
        return self._trailing_metadata

    def get_reraise(self):
        return _STATUS_CODE_TO_EXCEPTION_MAP.get(self.code, errors.api.Unknown)(self.details,
                                                                                ref_code=self.trailing_metadata.get('ref_code', None))




