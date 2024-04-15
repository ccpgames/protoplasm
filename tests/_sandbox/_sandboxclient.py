from sandbox.test import service_grpc_sender

if __name__ == '__main__':
    srv = service_grpc_sender.SimpleService('localhost:50051')
    ret = srv.hello('darkeness my old friend')
    print(ret)

    ret2 = srv.nested_hello()
    print(ret2)