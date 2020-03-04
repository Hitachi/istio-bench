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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
import statsmodels.api as sm
from libs import const


class Chart:
    """deploy/delete resource on k8s"""

    def __init__(self, istio_version, outdir):
        self.istio_version = istio_version
        self.outdir = outdir
        self.metrics = {}

        plt.rcParams["font.size"] = 18
        plt.rcParams["figure.figsize"] = (16, 8)
        sns.set()
        sns.set_context(
            "notebook", font_scale=1.5, rc={"lines.linewidth": 3, "grid.linestyle": "+"}
        )

    def load_metrics(self, target):
        template = os.path.join(self.outdir, "{}*".format(target.lower()))
        filenames = sorted(glob.glob(template))

        template = os.path.join(
            self.outdir, "{}-([0-9]*)pod.csv".format(target.lower())
        )
        pod_num = [int(re.sub(template, "\\1", x)) for x in filenames]

        dfs = [pd.read_csv(f, index_col=[0, 1]) for f in filenames]
        col = [tuple(map(lambda x: (i, x), dfs[0].columns)) for i in pod_num]
        col = pd.MultiIndex.from_product((pod_num, dfs[0].columns))
        integrate = pd.concat(dfs, axis=1)
        integrate.columns = col
        integrate = integrate.reorder_levels([1, 0], axis=1).sort_index(axis=1)

        # [Column sample]
        # cpu_usage,     memory,...
        # 100, 200, ..., 100, 200, ...
        self.metrics[target] = integrate

    def draw_and_save(self, target):
        chart = self.__parse_to_chartdata(df=self.metrics, target=target)

        # Normal Chart
        for k, v in chart.items():
            name = const.RESOURCES[k]["TITLE"]
            unit = const.RESOURCES[k]["UNIT"]
            # print()
            # print(target, name, unit)
            # print(v)
            v.plot()
            self.__set_chart_format(target, name, unit)
            self.__savefig(target, k)
            plt.clf()  # clear current figure for next chart

    def predict_draw_and_save(self, target):
        """
        Predict resource usage in 0-2000 pod and Draw it
        """
        chart = self.__parse_to_chartdata(df=self.metrics, target=target)

        # x value(0...2000)
        plot_range = np.array([i for i in range(0, 2001, 100)])
        textX = 1500
        for k, v in chart.items():
            pred, params = self.__predict(v, plot_range, target)
            pred.plot()

            if target == const.TARGET["PROXY"]:
                params = params.to_frame()

            # Plot formula
            for _, item in params.iteritems():
                x1, c = item.x1, item.const
                textY = textX * x1 + c
                plt.text(x=textX, y=textY, s=r"$y=%.3fx+%.3f$" % (x1, c))

            name = const.RESOURCES[k]["TITLE"]
            unit = const.RESOURCES[k]["UNIT"]
            self.__set_chart_format(target, name, unit, is_predicated=True)
            self.__savefig(target, k, is_predicated=True)
            self.__savecsv(target, k, pred)
            plt.clf()  # clear current figure for next chart

    def __predict(self, chartdata, plotRange, target):
        # Calc liner by Ordinary Least Squares regression
        model = sm.OLS(chartdata, sm.add_constant(chartdata.index)).fit()

        if target == const.TARGET["PROXY"]:
            df = chartdata.to_frame(const.TARGET["PROXY"])
        else:
            df = chartdata

        pred = pd.DataFrame(
            model.predict(sm.add_constant(plotRange)),
            index=plotRange,
            columns=df.columns,
        )
        param = model.params

        return pred, param

    def __set_chart_format(self, target, resource_name, unit, is_predicated=False):
        title = "{target} {resource_name} Usage per Pod{pred} [{istio_version}]".format(
            target=target,
            resource_name=resource_name,
            istio_version=self.istio_version,
            pred=" (Predicated)" if is_predicated else "",
        )
        plt.title(title)
        # e.g. CPU Usage[%], Memory Usage[MB]
        plt.ylabel(
            "{resource_name} Usage[{unit}]".format(
                resource_name=resource_name, unit=unit
            )
        )
        plt.xlabel("Pods")

    def __savefig(self, target, resource, is_predicated=False):
        filename = (
            "chart_{target}_{resource}{pred}.svg".format(
                target=target,
                resource=resource,
                pred="_predicated" if is_predicated else "",
            )
            .lower()
            .replace(" ", "_")
        )

        filepath = os.path.join(self.outdir, filename)
        plt.savefig(filepath, rasterized=True, format="svg")

    def __savecsv(self, target, resource, df):
        filename = (
            "table_{target}_{resource}.csv".format(target=target, resource=resource)
            .lower()
            .replace(" ", "_")
        )

        filepath = os.path.join(self.outdir, filename)
        df.to_csv(filepath, sep=",")

    def __get_top_n(self, df, n):
        return df.sort_values(by=df.columns[-1], ascending=False)[:n].T

    def __parse_to_chartdata(self, df, target):
        integrate = df[target]

        chart = {}
        for k, v in const.RESOURCES.items():
            title = v["TITLE"]
            row_filter = None

            if v["CONTAINER"] == "ISTIO_PROXY":
                row_filter = integrate.index.get_level_values("container") != "POD"
            else:
                row_filter = integrate.index.get_level_values("container") == "POD"

            chart[k] = integrate.loc[row_filter, title]

        if target == const.TARGET["PROXY"]:
            for k, v in chart.items():
                chart[k] = v.median()
        elif target == const.TARGET["CONTROL"]:
            # A lot of controlplanes are difficult to see. Draw only top 3
            for k, v in chart.items():
                chart[k] = self.__get_top_n(v, 3)

        return chart
