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

from logging import getLogger
from subprocess import Popen, DEVNULL, getoutput, CalledProcessError, SubprocessError

logger = getLogger(__name__)


def run_sync(command: str) -> str:
    """
    Returns
    -------
    stdout: str
    Standard output
    """
    logger.debug("Run subprocess with sync: {}".format(command))
    try:
        op = getoutput(command)
    except CalledProcessError as e:
        logger.error("Failed to run command: {}".format(e))
        raise e

    return op.strip()


def run_async(command: str, stdout=DEVNULL) -> Popen:
    """
    Returns
    -------
    process: Popen
    Popen object in subprocess to kill process.
    """
    logger.debug("Run subprocess with async: %s" % command)
    try:
        process = Popen(command.split(" "), stdout=stdout)
    except SubprocessError as e:
        logger.error("Failed to run command with async: {}".format(e))
        raise e

    return process
