#!/usr/bin/env python

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

from __future__ import print_function

import argparse
from logging import getLogger
import time
import sys
from libs.dummypod import DummyPod
from libs.prom import Prometheus
from libs.chart import Chart
from libs.report import Report
from libs import utils
from libs import const

logger = getLogger(__name__)


def run(args):

    if args.version:
        print(utils.get_version())
        exit(0)

    if args.max_pod == 0:
        print("Set deploy_num at least one")
        exit(1)

    if args.interval > args.max_pod:
        print("Set Interval to the same value as max_pod")
        args.interval = args.max_pod

    utils.define_rootlogger(args.verbose)
    istio_version = utils.get_istio_version()
    starttime = utils.get_unixepoch()

    if args.output == const.DUMMY_OUTPUT_DIR:
        outdir = utils.make_output_dir(istio_version, starttime, path='')
    else:  # make directory if requested dir is not exist.
        outdir = utils.make_output_dir(istio_version, starttime, path=args.output)
    print("Output directory: {outdir}".format(outdir=outdir))

    pod_manifest = __load_manifest(args.manifest)
    ns_manifest = __load_manifest(args.ns_manifest)

    try:
        dummy_pod = DummyPod(pod_manifest, ns_manifest, args.prefix)
        prometheus = Prometheus(args.prometheus_url, args.prefix, outdir)

        deploy_and_mesure(args, dummy_pod, prometheus, outdir)

        print("---")
        print("All test was finished")

        if not args.no_graph:
            chart = Chart(istio_version, outdir)
            calc_chart(chart, dummy_pod)

        report = Report(istio_version, utils.uepoch2timestamp(starttime),
                        outdir, not args.no_graph)
        report.generate()
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc(file=sys.stdout)
    finally:
        print("\nReset evaluating environment", end="")
        sys.stdout.flush()  # output above stdout forcefully
        dummy_pod.reset()
        print("  ...Done")


def calc_chart(chart, dummy_pod):
    print("Generate metrics charts", end="")
    chart.load_metrics(target=const.TARGET["PROXY"])
    chart.load_metrics(target=const.TARGET["CONTROL"])
    chart.draw_and_save(target=const.TARGET["PROXY"])
    chart.draw_and_save(target=const.TARGET["CONTROL"])
    print("  ...Done")
    print("Generate predicated charts", end="")
    chart.predict_draw_and_save(target=const.TARGET["PROXY"])
    chart.predict_draw_and_save(target=const.TARGET["CONTROL"])
    print("  ...Done")


def deploy_and_mesure(args, dummy_pod, prometheus, outdir):
    for i, d_num in enumerate(range(args.interval, args.max_pod + 1, args.interval)):
        pod_num = (i + 1) * args.interval
        print("---")
        print("TEST {i}. Number of Pods: {pod_num}".format(i=(i + 1), pod_num=pod_num))

        print("  [Deploy Dummy Pods]")
        __deploy(dummy_pod, d_num)
        __wait(wait_sec=20)
        print("  [Get metrics]")
        prometheus.calc_metrics()
        prometheus.save_metrics(pod_num)
        print("    Save metrics on {outdir}".format(outdir=outdir))


def __deploy(dummy_pod, deploy_num):
    namespace = dummy_pod.create_env(deploy_num=50)
    sys.stdout.write("    Wait until all deployments are available")
    sys.stdout.flush()

    res = dummy_pod.wait(
        namespace=namespace, resource="deployment", condition="Available"
    )
    logger.debug(res)
    print(" ...Done")


def __wait(wait_sec):
    print(
        "    Wait {time}sec to stabilize pod resource usage".format(time=wait_sec),
        end="",
    )
    for current in range(wait_sec):
        time.sleep(1)
        sys.stdout.write(
            "\r    Wait {time}sec to stabilize pod resource usage".format(
                time=(wait_sec - current - 1)
            )
        )
        sys.stdout.flush()
    print(" ...Done")


def __load_manifest(filepath):
    try:
        with open(filepath) as f:
            return f.read()
    except Exception as e:
        print(e)


def get_parser():
    parser = argparse.ArgumentParser(
        description="Measure resource usage test",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--max_pod",
        help="maximum number of pods used in the test",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--interval",
        help="number of pods to deploy at one time",
        type=int,
        default=100
    )
    parser.add_argument(
        "--prometheus_url",
        help="url of prometheus. default url uses kubectl port-forward automatically",
        default=const.PROMETHEUS_URL
    )
    parser.add_argument(
        "--manifest",
        help="manifest filepath of dummmy pods",
        default="./template/nginx.yaml",
    )
    parser.add_argument(
        "--ns_manifest",
        help="manifest filepath of dummmy namespaces",
        default="./template/namespace.yaml",
    )
    parser.add_argument(
        "--prefix",
        help="prefix of pod and namespaces for test",
        default="dummy-"
    )
    parser.add_argument(
        "--no-graph",
        help="do not output graph image(svg)",
        action="store_true"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path of the output directory",
        default=const.DUMMY_OUTPUT_DIR
    )
    parser.add_argument(
        "-v", "--verbose",
        help="increase output verbosity[-2 < x < 2]",
        type=int,
        default=0
    )
    parser.add_argument(
        "--version",
        help="get version",
        action="store_true"
    )
    # parser.add_argument(
    #     "--target",
    #     help="proxy, controlplane, both",
    #     default='both')

    return parser


def main(argv):
    args = get_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
