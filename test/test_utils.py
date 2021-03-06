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

import unittest
from libs import utils


class TestCommand(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_istio_version(self):
        version = utils.get_istio_version()
        self.assertRegex(version, r"[0-9]\.[0-9]\.[0-9]")  # e.g. 1.5.0


if __name__ == "__main__":
    unittest.main()
