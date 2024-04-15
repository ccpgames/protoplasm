__all__ = [
    'BaseContext',
]


class BaseContext(object):
    def __init__(self, wrapped_context, *args, **kwargs):
        self.wrapped_context = wrapped_context
        self.metadata = {}

    def get_origin_ip(self, default=None):
        raise NotImplementedError('BaseContext needs to be extended to account for different invocation contexts')

    def get_meta(self, name, default=None):
        raise NotImplementedError('BaseContext needs to be extended to account for different invocation contexts')
