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

import argparse
from libs import const
from libs import utils
from os.path import join

""" Define command line options """


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog,
            max_help_position=27,
            width=110),
        description="measures cpu, memory, and network usage of Istio for each service"
    )
    parser.add_argument(
        "services",
        help="number of services to be deployed as a workload",
        type=natural_number,
        default=500,
    )
    parser.add_argument(
        "--by",
        help="number of Services by namespace",
        type=int,
        metavar="number",
        default=100
    )
    parser.add_argument(
        "--prometheus",
        help="url of Prometheus. The default url uses kubectl port-forward",
        metavar="url",
        default=const.PROMETHEUS_URL
    )
    parser.add_argument(
        "--namespace",
        help="path of Namespace template file",
        metavar="file",
        dest="namespace_template",
        default=join(const.TEMPLATE_DIR, "namespace.yaml")
    )
    parser.add_argument(
        "--deployment",
        help="path of Deployment template file",
        metavar="file",
        dest="deployment_template",
        default=join(const.TEMPLATE_DIR, "deployment.yaml")
    )
    parser.add_argument(
        "--service",
        help="path of Service template file",
        metavar="file",
        dest="service_template",
        default=join(const.TEMPLATE_DIR, "service.yaml")
    )
    parser.add_argument(
        "--no-chart",
        help="do not output chart image(svg)",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--no-predict",
        help="do not predict resource usage",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "-o", "--output",
        help="path of the output directory",
        metavar="dir",
        default=const.DEFAULT_OUTPUT_DIR
    )
    parser.add_argument(
        "--isolate",
        help="[NOT IMPLEMENTED] isolate envoy xDS by namespace",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--verbose",
        help="number for the log level verbosity",
        type=int,
        choices=[0, 1, 2, 3, 4],
        default=0
    )
    parser.add_argument(
        "-V", "--version",
        action='version',
        version=utils.get_version()
    )

    return parser


def natural_number(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("set a positive int value")
    return ivalue
