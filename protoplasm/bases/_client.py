__all__ = [
    'BaseGrpcClientImplementation',
]
import grpc  # noqa

from protoplasm.structs import *
from ._remotewrap import *
from .dataclass_bases import *

import logging
log = logging.getLogger(__name__)


class BaseGrpcClientImplementation:
    def __init__(self, service_stub_cls: Type, grpc_host='localhost:50051',
                 credentials: Optional[Union[bool, grpc.ChannelCredentials]] = None,
                 options: Optional[Dict] = None, *args, **kwargs):
        """
        credentials:
        - None -> Automatic... will use `grpc.ssl_channel_credentials()` and secure_channel if port is 443
        - True -> Will use `grpc.ssl_channel_credentials()` and secure_channel
        - False -> Will use insecure_channel and no creds
        - grpc.ChannelCredentials -> Will use given creds and secure_channel
        """
        options = options or {}
        if 'grpc.enable_http_proxy' not in options:
            options['grpc.enable_http_proxy'] = 0
        option_tuple = tuple(options.items())

        # Backwards compatibility
        if kwargs:
            if not credentials and 'credential' in kwargs:
                credentials = kwargs.pop('credential')
                log.warning('Deprecated keyword "credential" used when initiating BaseGrpcClient.'
                            ' Please use "credentials" instead!')

        # This keeps happening...!
        if ':' not in grpc_host:
            if credentials:
                log.warning('No port used in host... adding 443 by default (cause this is a secure connection)!')
                grpc_host = f'{grpc_host}:443'
            else:
                log.warning('No port used in host... adding 50051 by default!')
                grpc_host = f'{grpc_host}:50051'

        if credentials is None:
            if grpc_host.endswith(':443'):
                credentials = grpc.ssl_channel_credentials()
        elif credentials is True:
            credentials = grpc.ssl_channel_credentials()

        if credentials:
            self.grpc_channel: grpc.Channel = grpc.secure_channel(grpc_host, credentials, options=option_tuple)
        else:
            self.grpc_channel: grpc.Channel = grpc.insecure_channel(grpc_host, options=option_tuple)

        self.stub = service_stub_cls(self.grpc_channel)

    def _forward_to_grpc(self, request_cls: Type[T_DCB], stub_method: Callable,
                         *args, **kwargs) -> Optional[Union[Any, Tuple[Any], Iterable[T_DCB]]]:
        return RemoteMethodWrapper(self, request_cls, stub_method, *args, **kwargs).call()
