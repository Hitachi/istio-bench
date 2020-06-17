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
from libs.prom import Prometheus
from libs import const


class TestPrometheus(unittest.TestCase):
    def setUp(self):
        print("Prerequirement: prometheus is published as prometheus service in istio-system namespace with 9090 port")
        self.prom = Prometheus(
            url=const.PROMETHEUS_URL,
            namespace_prefix="dummy",
            outdir="output_sample",
            measure_second=const.MEASURE_SECOND)
        pass

    def tearDown(self):
        del self.prom
        pass

    def test_get_metrics(self):
        resources = ["Memory", "CPU", "Traffic Rx", "Traffic Tx"]
        parameters = ["metric", "value"]
        for _, queries in self.prom.query_set.items():
            metrics = self.prom.get_data(queries)
            self.assertEqual(list(metrics.keys()), resources)
            self.assertEqual(list(metrics["Memory"][0].keys()), parameters)

    def test_to_dataframe_proxy(self):
        metrics = {
            'Memory': [{'metric': {'container': 'POD', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.453, '1.26171875']}, {'metric': {'container': 'istio-proxy', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.453, '36.3671875']}],
            'CPU': [{'metric': {'container': 'POD', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.475, '0']}, {'metric': {
                'container': 'istio-proxy', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.475, '0.5161875468398338']}],
            'Traffic Rx': [{'metric': {'container': 'POD', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.499, '0.0005826950073242188']}],
            'Traffic Tx': [{'metric': {'container': 'POD', 'pod': 'dummy-1592244981-0001-86ddc9f5f8-jd5hq'}, 'value': [1592286002.522, '0.007493209838867187']}]}
        df = self.prom.to_dataframe(metrics)
        print(df)

    def test_to_dataframe_controlplane(self):
        metrics = {
            'Memory': [{'metric': {'container': 'istio-proxy', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.544, '36.13671875']}, {'metric': {'container': 'prometheus', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.544, '808.9765625']}, {'metric': {'container': 'POD', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.544, '1.19921875']}, {'metric': {'container': 'POD', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.544, '1.27734375']}, {'metric': {'container': 'POD', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.544, '1.47265625']}, {'metric': {'container': 'discovery', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.544, '39.1796875']}, {'metric': {'container': 'istio-proxy', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.544, '35.87890625']}],
            'CPU': [{'metric': {'container': 'POD', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.566, '0']}, {'metric': {'container': 'POD', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.566, '0']}, {'metric': {'container': 'POD', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.566, '0']}, {'metric': {'container': 'discovery', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.566, '0.6972964454274245']}, {'metric': {'container': 'istio-proxy', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.566, '0.4799977207910423']}, {'metric': {'container': 'istio-proxy', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.566, '0.3988580362818221']}, {'metric': {'container': 'prometheus', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.566, '2.821866831152219']}],
            'Traffic Rx': [{'metric': {'container': 'POD', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.586, '0.004613473243637737']}, {'metric': {'container': 'POD', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.586, '0.0005734247351880211']}, {'metric': {'container': 'POD', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.586, '0.036150981058143225']}],
            'Traffic Tx': [{'metric': {'container': 'POD', 'pod': 'istio-ingressgateway-6f87db8689-tpx72'}, 'value': [1592286002.609, '0.002149808943366961']}, {'metric': {'container': 'POD', 'pod': 'prometheus-7c9ddc484d-r8kvx'}, 'value': [1592286002.609, '0.0024488306607987594']}, {'metric': {'container': 'POD', 'pod': 'istiod-7599c64cb4-wbmwx'}, 'value': [1592286002.609, '0.0011365019366498049']}]}
        self.prom.to_dataframe(metrics)
        df = self.prom.to_dataframe(metrics)
        print(df)


if __name__ == "__main__":
    unittest.main()
