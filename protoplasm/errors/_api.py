__all__ = [
    'Unknown',
    'NotFound',
    'InvalidArgument',
    'Unimplemented',
    'PermissionDenied',
    'Unauthenticated',
    'Unavailable',
    'DeadlineExceeded',
    'AlreadyExists',
    'FailedPrecondition',
    'DataLoss',
    'ResourceExhausted',
    'OutOfRange',
    'Internal',
    'Cancelled',
    'Aborted',
    'ClientApiError',
    'PreRequestError',
    'PostRequestError',
]

import grpc
from ._base import *


class Unknown(ServiceApiException):
    def __init__(self, details='unknown', ref_code=None, should_log=True):
        """For example, this error may be returned when a Status value received
        from another address space belongs to an error-space that is not known
        in this address space. Also errors raised by APIs that do not return
        enough error information may be converted to this error.
        """
        self.status_code = grpc.StatusCode.UNKNOWN
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class NotFound(ServiceApiException):
    def __init__(self, details='not found', ref_code=None, should_log=False):
        """Some requested entity was not found.
        """
        self.status_code = grpc.StatusCode.NOT_FOUND
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class InvalidArgument(ServiceApiException):
    def __init__(self, details='invalid argument', ref_code=None, should_log=False):
        """The client specified an invalid argument.
        """
        self.status_code = grpc.StatusCode.INVALID_ARGUMENT
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Unimplemented(ServiceApiException):
    def __init__(self, details='unimplemented', ref_code=None, should_log=False):
        """The operation is not implemented or is not supported/enabled in this
        service.
        """
        self.status_code = grpc.StatusCode.UNIMPLEMENTED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class PermissionDenied(ServiceApiException):
    def __init__(self, details='permission denied', ref_code=None, should_log=True):
        """The caller does not have permission to execute the specified
        operation. PERMISSION_DENIED must not be used for rejections caused by
        exhausting some resource (use RESOURCE_EXHAUSTED instead for those
        errors). PERMISSION_DENIED must not be used if the caller can not be
        identified (use UNAUTHENTICATED instead for those errors). This error
        code does not imply the request is valid or the requested entity exists
        or satisfies other pre-conditions.
        """
        self.status_code = grpc.StatusCode.PERMISSION_DENIED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Unauthenticated(ServiceApiException):
    def __init__(self, details='unauthenticated', ref_code=None, should_log=False):
        """The request is not authenticated but needs to be.
        """
        self.status_code = grpc.StatusCode.UNAUTHENTICATED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Unavailable(ServiceApiException):
    def __init__(self, details='unavailable', ref_code=None, should_log=False):
        """The service is currently unavailable. This is most likely a transient
        condition, which can be corrected by retrying with a backoff.
        """
        self.status_code = grpc.StatusCode.UNAVAILABLE
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class DeadlineExceeded(ServiceApiException):
    def __init__(self, details='deadline exceeded', ref_code=None, should_log=False):
        """The deadline expired before the operation could complete. For
        operations that change the state of the system, this error may be
        returned even if the operation has completed successfully. For example,
        a successful response from a server could have been delayed long enough
        for the deadline to expire.
        """
        self.status_code = grpc.StatusCode.DEADLINE_EXCEEDED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class AlreadyExists(ServiceApiException):
    def __init__(self, details='already exists', ref_code=None, should_log=False):
        """The entity that a client attempted to create already exists.
        """
        self.status_code = grpc.StatusCode.ALREADY_EXISTS
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class FailedPrecondition(ServiceApiException):
    def __init__(self, details='failed precondition', ref_code=None, should_log=False):
        """The operation was rejected because the system is not in a state
        required for the operation's execution. For example, the directory to be
        deleted is non-empty, an rmdir operation is applied to a non-directory,
        etc.
        """
        self.status_code = grpc.StatusCode.FAILED_PRECONDITION
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class DataLoss(ServiceApiException):
    def __init__(self, details='data loss', ref_code=None, should_log=True):
        """Unrecoverable data loss or corruption.
        """
        self.status_code = grpc.StatusCode.DATA_LOSS
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class ResourceExhausted(ServiceApiException):
    def __init__(self, details='resource exhausted', ref_code=None, should_log=True):
        """Some resource has been exhausted, perhaps a per-user quota, or
        perhaps the entire file system is out of space.
        """
        self.status_code = grpc.StatusCode.RESOURCE_EXHAUSTED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class OutOfRange(ServiceApiException):
    def __init__(self, details='out of range', ref_code=None, should_log=False):
        """The operation was attempted past the valid range.
        """
        self.status_code = grpc.StatusCode.OUT_OF_RANGE
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Internal(ServiceApiException):
    def __init__(self, details='internal', ref_code=None, should_log=True):
        """Internal errors. This means that some invariants expected by the
        underlying system have been broken. This error code is reserved for
        serious errors.
        """
        self.status_code = grpc.StatusCode.INTERNAL
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Cancelled(ServiceApiException):
    def __init__(self, details='cancelled', ref_code=None, should_log=False):
        """The operation was cancelled, typically by the caller.
        """
        self.status_code = grpc.StatusCode.CANCELLED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class Aborted(ServiceApiException):
    def __init__(self, details='aborted', ref_code=None, should_log=False):
        """The operation was aborted, typically due to a concurrency issue such
        as a sequencer check failure or transaction abort.
        """
        self.status_code = grpc.StatusCode.ABORTED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class ClientApiError(ServiceApiException):
    def __init__(self, details='client_error', ref_code=None, should_log=True):
        """Error raised by a gRPC client when non-gRPX protoplasm errors occur.
        """
        self.status_code = grpc.StatusCode.UNKNOWN
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class PreRequestError(ClientApiError):
    def __init__(self, details='pre_request_error', ref_code=None, should_log=True):
        """Error raised by a gRPC client when exceptions occur before the actual
        gRPC request (e.g. while casting).
        """
        self.status_code = grpc.StatusCode.FAILED_PRECONDITION
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class PostRequestError(ClientApiError):
    def __init__(self, details='post_request_error', ref_code=None, should_log=True):
        """Error raised by a gRPC client when exceptions occur AFTER the actual
        gRPC request (e.g. while casting).
        """
        self.status_code = grpc.StatusCode.CANCELLED
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code
