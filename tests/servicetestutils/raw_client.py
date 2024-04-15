__all__ = [
    'call_WithNoData',
    'call_WithInput',
    'call_WithOutput',
    'call_WithBoth',
    'call_WithManyInputs',
    'call_WithManyOutputs',
    'call_WithManyBoths',
]
from unittesting.unary import unaryservice_pb2
from unittesting.unary import unaryservice_pb2_grpc
import grpc
from typing import *

import logging
log = logging.getLogger(__name__)


def call_WithNoData(port: str = 'localhost:50051'):
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        result: unaryservice_pb2.WithNoDataResponse = stub.WithNoData(
            unaryservice_pb2.WithNoDataRequest()
        )
        log.info(f'Called WithNoData -> {result}')


def call_WithInput(port: str = 'localhost:50051', unnamed_input: str = '?'):
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithInputRequest(unnamed_input=unnamed_input)
        result: unaryservice_pb2.WithInputResponse = stub.WithInput(req)
        log.info(f'Called WithInput with {req} -> {result}')


def call_WithOutput(port: str = 'localhost:50051') -> str:
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithOutputRequest()
        result: unaryservice_pb2.WithOutputResponse = stub.WithOutput(req)
        log.info(f'Called WithOutput with {req} -> {result}')
        return result.unnamed_output


def call_WithBoth(port: str = 'localhost:50051', some_input: str = '?') -> str:
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithBothRequest(some_input=some_input)
        result: unaryservice_pb2.WithBothResponse = stub.WithBoth(req)
        log.info(f'Called WithBoth with {req} -> {result}')
        return result.some_output


def call_WithManyInputs(port: str = 'localhost:50051',
                        first_input: str = '?',
                        second_input: int = 0,
                        third_input: bool = False):
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithManyInputsRequest(
            first_input=first_input,
            second_input=second_input,
            third_input=third_input,
        )
        result: unaryservice_pb2.WithManyInputsResponse = stub.WithManyInputs(req)
        log.info(f'Called WithManyInputs with {req} -> {result}')


def call_WithManyOutputs(port: str = 'localhost:50051') -> Tuple[str, int, bool]:
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithManyOutputsRequest()
        result: unaryservice_pb2.WithManyOutputsResponse = stub.WithManyOutputs(req)
        log.info(f'Called WithManyOutputs with {req} -> {result}')
        return result.first_output, result.second_output, result.third_output


def call_WithManyBoths(port: str = 'localhost:50051',
                       another_first_input: str = '?',
                       another_second_input: int = 0,
                       another_third_input: bool = False) -> Tuple[str, int, bool]:
    with grpc.insecure_channel(port) as channel:
        stub = unaryservice_pb2_grpc.UnaryServiceStub(channel)
        req = unaryservice_pb2.WithManyBothsRequest(
            another_first_input=another_first_input,
            another_second_input=another_second_input,
            another_third_input=another_third_input,
        )
        result: unaryservice_pb2.WithManyBothsResponse = stub.WithManyBoths(req)
        log.info(f'Called WithManyBoths with {req} -> {result}')
        return result.another_first_output, result.another_second_output, result.another_third_output
