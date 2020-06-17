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

import sys
from logging import getLogger

from libs import command


class Workload:
    """ Deploy/Delete Kubernetes resources(namespace, pod, service) as workload """

    def __init__(self, delete_label, prefix, test_id):
        self.logger = getLogger(__name__)

        self.label = delete_label
        self.prefix = prefix
        self.test_id = test_id
        self.name_index = 0  # Do not use this variable outside of __get_unique_postfix.
        self.ns_template = None
        self.svc_template = None
        self.dep_template = None
        self.aggregated_mode = True
        self.aggregated_num = 10

    def load_template(self, kind: str, filepath: str):
        manifest = ""
        try:
            with open(filepath) as f:
                manifest = f.read()
        except Exception as e:
            self.logger.error("Failed to load manifest in {}".format(filepath))
            raise e

        if kind.lower() == "namespace":
            self.ns_template = manifest
        elif kind.lower() == "deployment":
            self.dep_template = manifest
        elif kind.lower() == "service":
            self.svc_template = manifest
        else:
            raise TypeError(
                "{} is unsupported. Please use service, deployment, or namespace".format(kind)
            )

    def generate(self, number_of_services: int = 50) -> str:
        """
        Create a namespace, a deployment, and N services

        Returns
        -------
        namespace : str
        Name of Namespace generated as a workload
        """

        ns_name = self.__get_unique_name()
        self.logger.info("Create namespace: {ns}".format(ns=ns_name))
        ns_manifest = self.ns_template.format(name=ns_name)
        self.__deploy_manifest(
            manifest=ns_manifest, namespace=None,
            resource_type="namespace", resource_name=ns_name)

        dep_name = self.__get_unique_name()
        self.logger.info("Create deployment: {dep}".format(dep=dep_name))
        dep_manifest = self.dep_template.format(name=dep_name)
        self.__deploy_manifest(
            manifest=dep_manifest, namespace=ns_name,
            resource_type="deployment", resource_name=dep_name)

        self.logger.info("Create services")

        # [m1, m2, m3, m4, ... ,mn]
        svcs = [
            self.svc_template.format(
                name=self.__get_unique_name(),
                deployment_name=dep_name
            ) for _ in range(number_of_services)]

        if self.aggregated_mode:
            agg = self.aggregated_num
            # [[m1, m2, m3],[m4,m5,m6], ... [m(n-1), mn]]
            svcs = [svcs[i:i + agg] for i in range(0, len(svcs), agg)]
            svcs = ["\n---\n".join(i) for i in svcs]  # yaml aggregate

        sys.stdout.write("    Progress: 0%")
        total = len(svcs)
        for i, s in enumerate(svcs):
            self.__deploy_manifest(
                manifest=s, namespace=ns_name,
                resource_type="service", resource_name="services")
            sys.stdout.write("\r    Progress: {}%".format(int((i + 1) * 100 / total)))
            sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.flush()

        return ns_name

    def __deploy_manifest(self, manifest, namespace=None, resource_type=None, resource_name=None):
        ns = " --namespace {}".format(namespace) if namespace else ""
        cmd = "cat << EOF | kubectl {ns} apply -f -\n{manifest}EOF".format(
            ns=ns, manifest=manifest
        )

        try:
            resp = command.run_sync(cmd)
        except Exception as e:
            self.logger.error("Failed to create {} {}".format(
                resource_type,
                resource_name)
            )
            raise e
        self.logger.info("Deploy {} - {}".format(resource_type, resource_name))
        self.logger.debug("Deploy result: {}".format(resp))

    def wait(self, namespace, resource, condition, timeout="300s"):
        """
        Wait for a specific condition on deployed/deleted resources
        """
        # This function use timeout command. because --timeout option in
        # <kubectl wait> does not mean process timeout.
        # --timeout is interval of sending GET resource to api-server
        cmd = "timeout {timeout} kubectl --namespace {namespace} wait {resource} \
            --for=condition={condition} --selector={label}".format(
            namespace=namespace,
            resource=resource,
            condition=condition,
            label=self.label,
            timeout=timeout,
        )
        command.run_sync(cmd)

    def reset(self):
        """
        Delete all namespaces generated by this script
        """
        self.logger.info("Delete all namespaces that has {} label".format(self.label))
        cmd = "kubectl delete namespace --selector={}".format(self.label)
        resp = command.run_sync(cmd)
        if resp:
            self.logger.debug("Result: {}".format(resp))

    def __get_unique_name(self) -> str:
        """ Get postfix of Service, Deployment, Namespace """
        idx = self.name_index
        self.name_index += 1
        return "{}-{:04}-{}".format(self.prefix, idx, self.test_id)
