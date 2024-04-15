__all__ = [
    'GrpcServer',
]

# TODO(thordurm@ccpgames.com) 2022-06-07: MOVE THIS TO A BETTER LOCATION!!

from concurrent import futures
import grpc  # noqa grpc is in the grpcio package
import time

from protoplasm.bases import grpc_bases

import logging
log = logging.getLogger(__name__)


class GrpcServer(object):
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24

    def __init__(self, port='[::]:50051', max_workers=10):
        """A simple gRPC server.

        Jusd add Servicer implementations (extending
        `protoplasm.bases.grpc_bases.BaseGrpcServicer`) and start it up with
        `serve()`.

        :param port: String listening address and port (default is `[::]:50051`)
        :param max_workers: Maximum workers via `concurrent.futures.ThreadPoolExecutor`
        """
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self.grpc_server.add_insecure_port(port)
        log.info(f'GrpcServer created on port={port}, max_workers={max_workers}')

    def add_servicer(self, servicer: grpc_bases.BaseGrpcServicer):
        """Adds a `protoplasm.bases.grpc_bases.BaseGrpcServicer` based services
        for this server to run.

        :param servicer: A servicer extending `protoplasm.bases.grpc_bases.BaseGrpcServicer`
        """
        servicer.add_to_server(self.grpc_server)
        log.info('Servicer added: %r', servicer)

    def serve(self):
        self.grpc_server.start()
        log.info('Server started')
        try:
            while True:
                log.info('Server listening...')
                time.sleep(GrpcServer._ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            log.info('Server interrupted!')
            self.grpc_server.stop(0)
            log.info('Server Stopped!')
