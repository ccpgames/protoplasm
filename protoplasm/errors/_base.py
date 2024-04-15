__all__ = [
    'ProtoplasmError',
    'ServiceApiException',
    'ResponseIterationTimoutError',
]


class ProtoplasmError(Exception):
    pass


class ServiceApiException(ProtoplasmError):
    def __init__(self, status_code=2, details='unknown', ref_code=None, should_log=False):
        """Base Error/Exception raised by service API implementations that can
        not return normally.
        """
        self.status_code = status_code
        self.details = details
        self.should_log = should_log
        self.ref_code = ref_code


class ResponseIterationTimoutError(ProtoplasmError, TimeoutError):
    pass
