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

import os
import glob
import logging
from libs import const
from libs import utils


class Report:
    """Generate report by markdown"""

    def __init__(self, version: str, starttime: str,
                 outdir: str, has_chart: bool):
        self.version = version
        self.outdir = outdir
        self.starttime = starttime
        self.has_chart = has_chart

    def generate(self):
        # ip:istioproxy, cp:controlplane
        ip_filename, cp_filename = self.__get_files()
        raw_data = self.__generate_rawdata(ip_filename, cp_filename)

        if self.has_chart:
            path = os.path.join(const.TEMPLATE_DIR, "report.md")
        else:
            path = os.path.join(const.TEMPLATE_DIR, "report_without_chart.md")

        outpath = os.path.join(self.outdir, "report.md")

        report = None
        with open(path) as f:
            report = f.read()
        report = report % (self.starttime, self.version, raw_data)

        with open(outpath, mode="w") as f:
            f.write(report)

    def __get_files(self) -> tuple:
        ip_template = os.path.join(self.outdir, "%s*" % "istioproxy")
        cp_template = os.path.join(self.outdir, "%s*" % "controlplane")

        ip_filenames = [os.path.basename(f) for f in glob.glob(ip_template)]
        ip_filenames = sorted(ip_filenames)
        cp_filenames = [os.path.basename(f) for f in glob.glob(cp_template)]
        cp_filenames = sorted(cp_filenames)

        return (ip_filenames, cp_filenames)

    def __generate_rawdata(self, ip_filenames: list, cp_filenames: list) -> str:
        output = """Raw Data

- Istio-Proxy
%s
- ControlPlane
%s
"""
        # filename sample: istioproxy-0050pod.csv
        ip = ["    - [{0}]({0})".format(f) for f in sorted(ip_filenames)]
        cp = ["    - [{0}]({0})".format(f) for f in sorted(cp_filenames)]

        ip = "\n".join(ip)
        cp = "\n".join(cp)
        logging.debug("Istio-Proxy, %s" % ip)
        logging.debug("ControlPlane, %s" % cp)

        return output % (ip, cp)
