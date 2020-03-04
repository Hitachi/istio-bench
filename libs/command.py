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

import logging
from subprocess import Popen, DEVNULL
from subprocess import getoutput


def run_sync(command: str) -> str:
    """
    Returns
    -------
    stdout: str
    standard output
    """
    logging.debug("run subprocess sync: %s" % command)
    op = getoutput(command)
    return op.strip()


def run_async(command: str, stdout=DEVNULL) -> Popen:
    """
    Returns
    -------
    process: Popen
    Popen object in subprocess to kill process.
    """
    logging.debug("run subprocess async: %s" % command)
    process = Popen(command.split(" "), stdout=stdout)
    return process
