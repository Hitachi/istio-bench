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
from libs.workload import Workload
from libs import const
from libs import utils
from libs import command
from os.path import join


class TestWorkload(unittest.TestCase):
    def setUp(self):
        test_id = utils.get_unixepoch_by_sec()
        self.workload = Workload(const.DELETE_LABEL, const.PREFIX, test_id)

    def tearDown(self):
        pass

    def load_templates(self):
        for resource in ("namespace", "deployment", "service"):
            self.workload.load_template(
                resource,
                join(const.TEMPLATE_DIR, "{}.yaml".format(resource))
            )

    def test_load_template(self):
        self.load_templates()
        self.assertIsNotNone(self.workload.ns_template)
        self.assertIsNotNone(self.workload.dep_template)
        self.assertIsNotNone(self.workload.svc_template)

    def test_gererate(self):
        self.load_templates()
        ns_name = self.workload.generate(3)
        output = command.run_sync("kubectl get svc -n {}".format(ns_name))
        self.assertEqual(len(output.splitlines()), 4)
        print("Delete workloads. Probably takes a little time.")
        self.workload.reset()


if __name__ == "__main__":
    unittest.main()
