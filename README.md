# Protoplasm

Utilities for working with Protobuf & gRPC in Python, e.g; compiling Python 3 
Dataclasses from compiled proto-message-python code and casting between the two,
quickly initializing large/nested Protobuf object, simplifying gRPC service 
interfaces etc. 

## IMPORTANT

Update this README file after moving from CCP's internal code repo to Github.



## Protoplasm 4

* Unify the unary functionality of Protoplasm 2 with the streaming 
  functionality of Protoplasm 3
  * The two turn out to be completely incompatible and API shattering
  * Protoplasm 4 must incorporate BOTH functionalities wile being backwards 
    compatible enough for both Protoplasm 2 and 3 projects to be able to 
    migrate to 4
  * The key here is detecting the `stream` keyword in protos that denote 
    streaming input and/or output
* Add piled up functionality/utility/QoL improvements/bugs that's been on The 
  List™ for a while
  * Cast to/from base64 encoded strings
  * Utilize the `__all__` directive to isolate `import *` side effects 
  * Integrate the Neobuf Builder CLI (from various other projects) into 
    Protoplasm and generalize it
  * Address the "`None` is default value" issue
  * Explore the pros/cons of making non-existing Message/Object attributes 
    return `Empty` or `EmptyDict` to simplify nested attribute fetching...?
* Refactor and restructure the package properly
  * Separate the 4 main roles of the package logically
    1. Cross-piling `*.proto` to `*_pb2.py` and `*_pb2_grpc.py`
    2. Cross-piling `*_pb2.py` to `*_dc.py` Neobuf Dataclasses
    3. Generating `*_api.py` interfaces
    4. Generating gRPC implementation of Services

## Troubleshooting

* I get `TypeError: Plain typing.NoReturn is not valid as type argument`
    * Upgrade to Python 3.9. This TypeError arises from [a bug in Python 3.7](https://bugs.python.org/issue34921)


## Clever bits to document...

- Code Generation (e.g. `foo.proto`) + how to build
    - Dataclasses -> `foo_dc.py` + how to use (+ DataclassBase freebies)
        - Extending Dataclasses (a no-no for pb2 files apparently)
    - Service API -> `foo_api.py` + how to use and implement
        - Automatic parameter unpacking
        - Return value packing
        - Raising `protoplasm.errors.api.*` on errors or non-ok returns
        - Using `protoplasm.decorators` for param and type checking
        - The `takes_context` decorator and how to use it
    - GRPC DC Service Servicer -> `foo_dc_grpc.py` + how to use
- Utilities
    - Proto <-> dict <-> Dataclass casters
    - The `mkproto` and `mkdataclass` helpers
    - The `unpack_dataclass_request` and `pack_dataclass_response` helpers
