from unittesting.unary import unaryservice_pb2
from unittesting.unary import unaryservice_pb2_grpc
import grpc
from concurrent import futures
from typing import *

import logging
log = logging.getLogger(__name__)


class UnaryServiceServicerImplementation(unaryservice_pb2_grpc.UnaryServiceServicer):
    def __init__(self):
        self.calls: Dict[str, int] = {
            'WithNoData': 0,
            'WithInput': 0,
            'WithOutput': 0,
            'WithBoth': 0,
            'WithManyInputs': 0,
            'WithManyOutputs': 0,
            'WithManyBoths': 0,
        }

    def WithNoData(self,
                   request: unaryservice_pb2.WithNoDataRequest,
                   context: grpc.ServicerContext) -> unaryservice_pb2.WithNoDataResponse:
        self.calls['WithNoData'] += 1
        log.info('WithNoData called!')
        return unaryservice_pb2.WithNoDataResponse()

    def WithInput(self,
                  request: unaryservice_pb2.WithInputRequest,
                  context: grpc.ServicerContext) -> unaryservice_pb2.WithInputResponse:
        self.calls['WithInput'] += 1
        log.info(f'WithInput called with {request}!')

        if request.unnamed_input == 'explode':
            return context.abort(grpc.StatusCode.NOT_FOUND, 'totally fake not found error')

        return unaryservice_pb2.WithInputResponse()

    def WithOutput(self,
                   request: unaryservice_pb2.WithOutputRequest,
                   context: grpc.ServicerContext) -> unaryservice_pb2.WithOutputResponse:
        self.calls['WithOutput'] += 1
        ret = unaryservice_pb2.WithOutputResponse(unnamed_output='you win')
        log.info(f'WithOutput called, returning {ret}')
        return ret

    def WithBoth(self,
                 request: unaryservice_pb2.WithBothRequest,
                 context: grpc.ServicerContext) -> unaryservice_pb2.WithBothResponse:
        self.calls['WithBoth'] += 1
        ret = unaryservice_pb2.WithBothResponse(some_output=request.some_input[::-1])
        log.info(f'WithBoth called with {request}, returning {ret}')
        return ret

    def WithManyInputs(self,
                       request: unaryservice_pb2.WithManyInputsRequest,
                       context: grpc.ServicerContext) -> unaryservice_pb2.WithManyInputsResponse:
        self.calls['WithManyInputs'] += 1
        log.info(f'WithManyInputs called with {request}!')
        return unaryservice_pb2.WithManyInputsResponse()

    def WithManyOutputs(self,
                        request: unaryservice_pb2.WithManyOutputsRequest,
                        context: grpc.ServicerContext) -> unaryservice_pb2.WithManyOutputsResponse:
        self.calls['WithManyOutputs'] += 1
        ret = unaryservice_pb2.WithManyOutputsResponse(first_output='snorlax',
                                                       second_output=7,
                                                       third_output=True)
        log.info(f'WithManyOutputs called, returning {ret}')
        return ret

    def WithManyBoths(self,
                      request: unaryservice_pb2.WithManyBothsRequest,
                      context: grpc.ServicerContext) -> unaryservice_pb2.WithManyBothsResponse:
        self.calls['WithManyBoths'] += 1
        ret = unaryservice_pb2.WithManyBothsResponse(another_first_output=request.another_first_input.upper(),
                                                     another_second_output=request.another_second_input // 2,
                                                     another_third_output=not request.another_third_input)
        log.info(f'WithManyBoths called with {request}, returning {ret}')
        return ret


class UnaryServiceServer(object):
    def __init__(self):
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer_implementation = UnaryServiceServicerImplementation()
        unaryservice_pb2_grpc.add_UnaryServiceServicer_to_server(self.servicer_implementation,
                                                                 self.grpc_server)

    def start(self, port: str = '[::]:50051'):
        self.grpc_server.add_insecure_port(port)
        log.info(f'Starting UnaryServiceServer on port {port}...')
        self.grpc_server.start()

    def stop(self):
        self.grpc_server.stop(0)
