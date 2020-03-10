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

DUMMY_OUTPUT_DIR = "./output-istio[version]-[timestamp]"
TEMPLATE_DIR = "./template"
PROMETHEUS_URL = "http://127.0.0.1:9090"
TARGET = {"PROXY": "IstioProxy", "CONTROL": "ControlPlane"}
RESOURCES = {
    "CPU": {"TITLE": "CPU", "UNIT": "%", "CONTAINER": "ISTIO_PROXY"},
    "MEMORY": {"TITLE": "Memory", "UNIT": "MiB", "CONTAINER": "ISTIO_PROXY"},
    "TRAFFIC_TX": {"TITLE": "Traffic Tx", "UNIT": "Mbps", "CONTAINER": "APP"},
    "TRAFFIC_RX": {"TITLE": "Traffic Rx", "UNIT": "Mbps", "CONTAINER": "APP"},
}
