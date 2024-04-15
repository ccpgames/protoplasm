from protoplasm.plasm import *

from sandbox.test import river_grpc_sender
from sandbox.test.river_dc import GuessTheNumberRequest, MarcoPoloRequest
import time
import random

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level='DEBUG')


def _guess_a_lot() -> Iterable[GuessTheNumberRequest]:
    for i in range(35, 45):
        r = GuessTheNumberRequest(number=i)
        log.info(f'yielding {r}')
        yield r
        time.sleep(2)


def _get_a_bunch_of_marcos() -> Iterable[MarcoPoloRequest]:
    for i in range(0, 100):
        r = MarcoPoloRequest(question=f'Marco! #{i}')
        log.info(f'yielding {r}')
        yield r
        time.sleep(random.randint(1, 5))


if __name__ == '__main__':
    srv = river_grpc_sender.StreamingService('localhost:50051')
    ret = srv.reverse_my_shit('this is not an anagram')
    print(ret)

    answer = srv.guess_the_number(_guess_a_lot())
    print(answer)

    ret = srv.reverse_my_shit('this is not an anagram')
    print(ret)

    for response in srv.tell_me_a_story('Three Little Pigs'):
        print(response.line)

    ret = srv.reverse_my_shit('this is not an anagram')
    print(ret)

    i = 1
    req_iter: RequestIterator[MarcoPoloRequest] = RequestIterator(MarcoPoloRequest(question=f'Marco! #{i}'))

    for response in srv.marco_polo(req_iter):
        print(response.answer)
        i += 1
        req_iter.send(MarcoPoloRequest(question=f'Marco! #{i}'))

    ret = srv.reverse_my_shit('this is not an anagram')
    print(ret)
