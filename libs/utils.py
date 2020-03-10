# Copyright 2020 Istio-Bench Authors and Hitachi Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import time
from datetime import datetime
from pathlib import Path
from libs import command
from logging import getLogger, StreamHandler, Formatter, WARNING


def get_unixepoch() -> int:
    """
    Get Unix Epoch by sec
    """
    return int(time())  # sec


def uepoch2timestamp(uepoch: int) -> str:
    dt = datetime.fromtimestamp(uepoch)
    return dt.strftime("%m/%d/%Y, %H:%M:%S")


def make_output_dir(version: str, unixepoch: int, path: str) -> str:
    if not path:
        path = "output-istio-{version}-{unixepoch}".format(
            version=version, unixepoch=unixepoch)
    Path(path).mkdir(parents=True, exist_ok=True)

    return path


def get_istio_version() -> str:
    """
    Get istio version(e.g. 1.4.5, 1.3.2) from pilot container image
    """
    cmd = "kubectl get pod -n istio-system -l istio=pilot -o jsonpath='{.items[0].spec.containers[0].image}'"
    imageName = command.run_sync(cmd)  # Output Sample: docker.io/istio/pilot:1.4.5
    return imageName[imageName.find(':')+1:]  # Extract version such as 1.4.5


def get_version() -> str:
    ver_path = "./VERSION"
    version = ""
    with Path(ver_path).open() as f:
        version = f.read()
    return version


def define_rootlogger(verbose: int):
    # https://docs.python.org/3/library/logging.html?highlight=notset#logging-levels
    loglevel = WARNING - verbose*10

    formatter = Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
    handler = StreamHandler()
    handler.setLevel(loglevel)
    handler.setFormatter(formatter)

    rootlogger = getLogger()
    rootlogger.setLevel(loglevel)
    rootlogger.addHandler(handler)
