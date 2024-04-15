import typing
import grpc
from concurrent import futures
from unittesting.unary.unaryservice_api import UnaryServiceInterface
from unittesting.unary.unaryservice_grpc_receiver import UnaryServiceGrpcServicer
from protoplasm import errors

import logging
log = logging.getLogger(__name__)


class UnaryServiceImplementation(UnaryServiceInterface):
    def __init__(self):
        self.calls: typing.Dict[str, int] = {
            'WithNoData': 0,
            'WithInput': 0,
            'WithOutput': 0,
            'WithBoth': 0,
            'WithManyInputs': 0,
            'WithManyOutputs': 0,
            'WithManyBoths': 0,
        }

    def with_no_data(self) -> typing.NoReturn:
        self.calls['WithNoData'] += 1
        log.info('with_no_data called!')

    def with_input(self, unnamed_input: str = None) -> typing.NoReturn:
        self.calls['WithInput'] += 1
        log.info(f'with_input called with {unnamed_input}!')
        if unnamed_input == 'explode':
            raise errors.NotFound('totally fake not found error')

    def with_output(self) -> str:
        self.calls['WithOutput'] += 1
        ret = 'you win'
        log.info(f'with_output called, returning "{ret}"')
        return ret

    def with_both(self, some_input: str = None) -> str:
        self.calls['WithBoth'] += 1
        ret = some_input[::-1]
        log.info(f'WithBoth called with "{some_input}", returning "{ret}"')
        return ret

    def with_many_inputs(self, first_input: str = None, second_input: int = None,
                         third_input: bool = None) -> typing.NoReturn:
        self.calls['WithManyInputs'] += 1
        log.info(f'WithManyInputs called with {first_input}, {second_input}, {third_input}!')

    def with_many_outputs(self) -> typing.Tuple[str, int, bool]:
        self.calls['WithManyOutputs'] += 1
        ret = 'snorlax', 7, True
        log.info(f'with_many_outputs called, returning {ret}')
        return ret

    def with_many_boths(self, another_first_input: str = None, another_second_input: int = None,
                        another_third_input: bool = None) -> typing.Tuple[str, int, bool]:
        self.calls['WithManyBoths'] += 1
        ret = another_first_input.upper(), another_second_input // 2, not another_third_input
        log.info(f'with_many_boths called with {another_first_input}, {another_second_input}, {another_third_input} returning {ret}')
        return ret


class UnaryProtoplasmServer(object):
    def __init__(self):
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer_implementation = UnaryServiceImplementation()
        self.servicer = UnaryServiceGrpcServicer(self.servicer_implementation)
        self.servicer.add_to_server(self.grpc_server)

    def start(self, port: str = '[::]:50051'):
        self.grpc_server.add_insecure_port(port)
        log.info(f'Starting UnaryProtoplasmServer on port {port}...')
        self.grpc_server.start()

    def stop(self):
        self.grpc_server.stop(0)

