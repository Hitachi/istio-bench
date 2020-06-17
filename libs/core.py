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
from time import sleep
import sys
from libs.workload import Workload
from libs.prom import Prometheus
from libs.chart import Chart
from libs.report import Report
from libs import utils
from libs import const

logger = getLogger(__name__)


def run(args):
    exit_status = 0

    utils.setup_logger(args.verbose)

    if args.by > args.services:
        print("'by' must be less than or equal to 'services'. \
            'by' was given the same value as 'service'.")
        args.by = args.services

    istio_version = utils.get_istio_version()

    if not istio_version:
        print("istio-pilot not found. Please install Istio")
        exit_status = 1
        return exit_status

    starttime = utils.get_unixepoch_by_sec()

    # make directory if directory not exist.
    outdir = utils.make_output_dir(istio_version, starttime, path=args.output)
    print("Output directory: {}".format(outdir))

    try:
        workload = Workload(const.DELETE_LABEL, const.PREFIX, test_id=starttime)
        workload.load_template("namespace", args.namespace_template)
        workload.load_template("deployment", args.deployment_template)
        workload.load_template("service", args.service_template)
        prometheus = Prometheus(args.prometheus, const.PREFIX, outdir, const.MEASURE_SECOND)

        # Number of services deployed each namespace
        full_num, rest = divmod(args.services, args.by)
        deploy_nums = [args.by] * full_num
        if rest != 0:
            deploy_nums.append(rest)

        current_num = 0
        for test_num, deploy_num in enumerate(deploy_nums):
            current_num += deploy_num
            deploy_and_mesure(
                (test_num + 1), deploy_num, current_num,
                workload, prometheus, outdir)

        print("---")
        print("All test was finished")

        if args.services == args.by and not args.no_predict:
            print("Prediction canceled. If you want to make predictions, \
                use a higher value for <services> than for <by>.")
            args.no_predict = True

        generate_chart(istio_version, outdir, args.no_chart, args.no_predict)
        report = Report(istio_version, utils.uepoch2timestamp(starttime),
                        outdir, not args.no_chart)
        report.generate()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        exit_status = 1
    except Exception as e:
        logger.exception(e)
        exit_status = 1
    finally:
        print("\nDelete evaluating environment", end="")
        sys.stdout.flush()  # output above stdout forcefully
        workload.reset()
        print("  ...Done")

    return exit_status


def generate_chart(istio_version, outdir, no_chart, no_predict):
    chart = Chart(istio_version, outdir)

    print("Generate metrics charts", end="")
    chart.load_metrics(const.TARGET["PROXY"])
    chart.load_metrics(const.TARGET["CONTROL"])

    if not no_chart:
        chart.draw_and_save(const.TARGET["PROXY"])
        chart.draw_and_save(const.TARGET["CONTROL"])
    print("  ...Done")

    if not no_predict:
        print("Generate predicated charts", end="")
        chart.predict_draw_and_save(const.TARGET["PROXY"], no_chart)
        chart.predict_draw_and_save(const.TARGET["CONTROL"], no_chart)
        print("  ...Done")


def deploy_and_mesure(test_num, deploy_num, current_num, workload, prometheus, outdir):
    print("---")
    print("TEST {i}. Number of Services: {work_num}".format(i=test_num, work_num=deploy_num))
    print("  [Generate workloads]")
    ns_name = workload.generate(deploy_num)

    print("    Wait to all deployment available")
    # Because the wait command cannot be used for Service,
    # it is used for Deployment instead.
    workload.wait(namespace=ns_name, resource="deployment", condition="Available")

    __wait(wait_sec=const.WAIT_SECOND)
    print("  [Get metrics]")
    metrics = prometheus.calc_metrics()
    prometheus.save_metrics(metrics, current_num)
    print("    Save metrics on {outdir}".format(outdir=outdir))


def __wait(wait_sec):
    sys.stdout.write(
        "    Wait {}sec to stabilize pod resource usage".format(wait_sec),
    )
    for current in range(wait_sec):
        sleep(1)
        sys.stdout.write(
            "\r    Wait {}sec to stabilize pod resource usage".format(
                (wait_sec - current - 1)
            )
        )
        sys.stdout.flush()
    print(" ...Done")
