__all__ = [
    'run_command',
    'dump_sys',
    'clear_imports',
    'build_new_protos',

    'HERE',
    'PROTO_ROOT',
    'BUILD_ROOT',
    'PROJECT_ROOT',
]
import os
import sys
import subprocess
import shutil
import time

import logging
log = logging.getLogger(__file__)

HERE = os.path.dirname(os.path.dirname(__file__))
PROTO_ROOT = os.path.join(HERE, 'res', 'proto')
BUILD_ROOT = os.path.join(HERE, 'res', 'build')
PROJECT_ROOT = os.path.dirname(HERE)


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=PROJECT_ROOT)
    return result.stdout, result.stderr, result.returncode


def dump_sys():
    log.info('------ DUMPING SYS -------')
    for k, v in sys.modules.items():
        if k.startswith('sandbox'):
            log.info(f'{k}: {v}')


def clear_imports():
    import importlib
    dump_list = []
    for k, v in sys.modules.items():
        if k.startswith('sandbox'):
            dump_list.append(k)
    for k in dump_list:
        del sys.modules[k]
    importlib.invalidate_caches()


def build_new_protos(package_name: str = 'sandbox'):
    build_package = os.path.join(BUILD_ROOT, package_name)
    if os.path.exists(build_package):
        shutil.rmtree(build_package)
        time.sleep(0.1)

    # from neobuilder.neobuilder import NeoBuilder
    #
    ## Build stuff...
    # builder = NeoBuilder(package='sandbox',
    #                     protopath=PROTO_ROOT,
    #                     build_root=BUILD_ROOT)
    # builder.build()
    log.info(f'{PROJECT_ROOT=}')

    stdout, stderr, retcode = run_command(f'python -m neobuilder.cli.neobuilder -b {BUILD_ROOT} {package_name} {PROTO_ROOT}')
    log.info(f'{stdout=}')
    log.info(f'{stderr=}')
    log.info(f'{retcode=}')
    # _clear_imports()