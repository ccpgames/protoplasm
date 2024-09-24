# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.3.0] - 2024-09-24

### Added

- Support for the `google.protobuf.Value` message


## [5.2.0] - 2024-09-23

### Added

- Support for the `google.protobuf.Struct` message



## [5.0.0] - 2024-04-15

### Changed

- Moved this entire project over to Github 
- Bumped the version in order to not confuse older stuff that doesn't expect 
  protoplasm to exist in Pypi.org (if we end up migriting this there and 
  just open-sourcing the whole thing)
  - Also in case something changes in the API while migrating, cause I tend 
    to fiddle with the code and tidy up and refactor when moving stuff


## [4.6.0] - 2024-03-19

### Added

- Docker image building of the latest stable version of Protoplasm and all 
  its dependencies to this project for both Alpine and Debian and Python 
  versions 3.8-3.12
  - Thus, checking in and publishing a new stable version of Protoplasm 
    should trigger new Docker base images with Protoplasm and all the gRPC 
    binaries up-to-date and ready to be used by other projects (speeding up 
    their testing and building considerably)
  - ...at least in the old CI/CD environment... We'll see what's what once 
    this is all in Github and Github Actions

### Changed

- A ton of CI/CD stuff that's irrelevant now that we've moved to Github



## [4.3.0] - 2022-08-03

Fixed ANOTHER bug in type hint importing

### Fixed

- Now importing `List` and `Dict` with nested dots work (e.g. `List[foo.Bar]`)


## [4.2.0] - 2022-08-03

Fixed bug in type hint importing

### Fixed

- Now importing `List` and `Dict` works (was only `typing.List` and `typing.Dict` before)



## [4.1.0] - 2022-04-24

### Added

- Added the `ResponseIterator` which remote method calls with stream output now return as a wrapper around the previously returned iterable results.
- Added `TimeoutResponseIterator` which wraps the new `ResponseIterator` with timeout functionality while waiting for response stream iterations.
- `ResponseIterator` has a `with_timeout()` method which automatically wraps it in a `TimeoutResponseIterator`
- Both `ResponseIterator` and `TimeoutResponseIterator` have a `one_and_done()` method which waits for one next response stream iteration and then closes the stream.
- `RequestIterator` can now take in a `list` or `tuple` as `initial_request` to load up multiple initial requests.
- Added `close()` method to `RequestIterator` to close the request stream (force a cancel event)
- Added `unpack()` to `DataclassBase`


## [4.0.0] - 2022-06-18

Major update that unifies the API and functionality of versions 2 and 3.

Skipping a bunch of versions and checkins between 3.0 and 4.0 cause they're 
not really important at the moment (it's 2024 and I'm migrating this from 
our internal Gitlab repo to Github).

### Added

- Unify the unary functionality of Protoplasm 2 with the streaming 
  functionality of Protoplasm 3
  - The two turn out to be completely incompatible and API shattering 
    Protoplasm 4 must incorporate BOTH functionalities wile being backwards 
    compatible enough for both Protoplasm 2 and 3 projects to be able to 
    migrate to 4
  -The key here is detecting the `stream` keyword in protos that denote 
    streaming input and/or output
- Add piled up functionality/utility/QoL improvements/bugs that's been on The 
  List™ for a while
  - Cast to/from base64 encoded strings
  - Utilize the `__all__` directive to isolate `import *` side effects 
  - Integrate the Neobuf Builder CLI (from various other projects) into 
    Protoplasm and generalize it
  - Address the "`None` is default value" issue
  - Explore the pros/cons of making non-existing Message/Object attributes 
    return `Empty` or `EmptyDict` to simplify nested attribute fetching...?

### Changed

- Refactor and restructure the package properly
  - Separate the 4 main roles of the package logically
    1. Cross-piling `*.proto` to `*_pb2.py` and `*_pb2_grpc.py`
    2. Cross-piling `*_pb2.py` to `*_dc.py` Neobuf Dataclasses
    3. Generating `*_api.py` interfaces
    4. Generating gRPC implementation of Services


## [3.0.0] - 2021-05-11

Major update including support for gRPC streams.

Skipping a bunch of versions and checkins between 2.0 and 3.0 cause they're 
not really important at the moment (it's 2024 and I'm migrating this from 
our internal Gitlab repo to Github).

## Added

- Support for gRPC streams

## Changed

- This broke backwards compatibility with version 1 and 2's non-streaming 
  gRPC calls


## [2.0.0] - 2021-02-18

Major update including support for secure channels.

Skipping a bunch of versions and checkins between 1.0 and 2.0 cause they're 
not really important at the moment (it's 2024 and I'm migrating this from 
our internal Gitlab repo to Github).

### Added

- Support for Secure gRPC channels


## [1.0.0] - 2019-07-11

Initial stable release. 

Skipping a bunch of versions and checkins between 0.1 and 1.0 cause they're 
not really important at the moment (it's 2024 and I'm migrating this from 
our internal Gitlab repo to Github).

### Added

- A bunch of features


## [0.1.0] - 2019-01-17

### Added

- The initial checkin of this project