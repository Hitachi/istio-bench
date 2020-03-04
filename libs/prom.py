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
import pandas as pd
import requests
import json
import logging
from libs import const

# for port-forward
from time import sleep
from urllib.parse import urlparse
from libs import command


class Prometheus:
    """get metrics from prometheus"""

    def __init__(self, url: str, namespace_prefix: str, outdir: str):
        self.timerange = "1m"
        self.ns_prefix = namespace_prefix
        self.outdir = outdir
        self.query_set = self.__get_query_set()
        self.metrics = None

        # Sometimes Prometheus is not published to istio-bench env.
        # In such case, use port-forward to access to Prometheus
        if url == const.PROMETHEUS_URL:
            self.url = const.PROMETHEUS_URL
            prom_port = self.__get_prometheus_port()
            self.forward_process = self.__start_port_forward(prom_port)
            sleep(2)  # wait to complete the port forwarding
        else:
            self.url = url
            self.forward_process = None

    def __del__(self):
        if self.forward_process is not None:
            self.__stop_port_forward(self.forward_process)

    def calc_metrics(self):
        dfs = {}
        for target, queries in self.query_set.items():
            try:
                metrics = self.__get_data(queries)
                df = self.__to_dataframe(metrics)
                dfs[target] = df
            except ValueError:
                logging.error("Failed to make metrics dataframe")
        self.metrics = dfs

    def save_metrics(self, current_pod_num: int):
        for target, df in self.metrics.items():
            filename = (
                "{}-{:04}pod.csv".format(target, current_pod_num)
                .lower()
                .replace(" ", "_")
            )
            filepath = os.path.join(self.outdir, filename)
            df.to_csv(filepath, sep=",")

    def __get_data(self, queries):
        """
        get metrics data of istio-proxy or controlplane
        """
        metrics = {}
        for resource, query in queries.items():
            url = self.url + "/api/v1/query?query=" + query
            resp = requests.get(url, verify=False).content.decode("utf-8")
            metrics[resource] = json.loads(resp)["data"]["result"]
        return metrics

    def __to_dataframe(self, metrics):
        dfs = []
        for resource, met in metrics.items():
            if not met:
                continue

            extracted = []
            for pod in met:
                container = "-"
                if "container" in pod["metric"]:
                    container = pod["metric"]["container"]

                record = {
                    "pod": pod["metric"]["pod"],
                    "container": container,
                    resource: float(pod["value"][1]),
                }
                extracted.append(record)
            df = pd.DataFrame(extracted)

            # Simplify pod name
            # e.g.) istio-galley-cf776876f-r26ph -> istio-galley
            df.pod = df.pod.map(lambda x: "-".join(x.split("-")[:2]))
            df = df.set_index(["pod", "container"])
            df = df.sort_index()
            dfs.append(df)

        df = pd.concat(dfs, axis=1)
        df.columns = metrics.keys()
        return df

    def __get_query_set(self):
        filters = {
            const.TARGET["PROXY"]: '{namespace=~"%s.*", container=~"POD|istio-proxy"}'
            % self.ns_prefix,
            const.TARGET["CONTROL"]: '{namespace="istio-system",container!=""}',
        }
        querybase = {
            const.RESOURCES["MEMORY"]["TITLE"]:
                "sum(avg_over_time(container_memory_usage_bytes%s[%s])/1024/1024) by (pod, container)",
            const.RESOURCES["CPU"]["TITLE"]:
                "sum(rate(container_cpu_usage_seconds_total%s[%s])*100) by (pod, container)",
            const.RESOURCES["TRAFFIC_RX"]["TITLE"]:
                "sum(rate(container_network_receive_bytes_total%s[%s])/1024/1024) by (pod, container)",
            const.RESOURCES["TRAFFIC_TX"]["TITLE"]:
                "sum(rate(container_network_transmit_bytes_total%s[%s])/1024/1024) by (pod, container)",
        }
        query_set = {}
        for target, _filter in filters.items():
            queries = {}
            for resource, query in querybase.items():
                queries[resource] = query % (_filter, self.timerange)
            query_set[target] = queries
        return query_set

    def __start_port_forward(self, prom_port=9090):
        local_port = urlparse(const.PROMETHEUS_URL).port
        # ignore log because port-forward is output 'Handling connection for <local_port>' log each time
        cmd = "kubectl port-forward -n istio-system svc/prometheus %s:%s" % (local_port, prom_port)
        process = command.run_async(cmd)
        return process

    def __stop_port_forward(self, process):
        process.kill()

    def __get_prometheus_port(self):
        cmd = "kubectl get svc -n istio-system prometheus -o jsonpath='{.spec.ports[0].port}'"
        port = command.run_sync(cmd)
        return port
