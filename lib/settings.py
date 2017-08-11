# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import boto3

metadata_file = "/var/local/cloudformation/stack-meta.json"
version_config_file_path = "/var/local/version_config.json"


class Settings:
    def __init__(self):
        self.opsman_user = 'admin'

        self.parse_meta(read_meta())
        self.get_parameters()
        self.describe_stack()
        self.parse_version_config(read_version_config())

        self.zones = [
            self.pcf_privatesubnetavailabilityzone,
            self.pcf_privatesubnet2availabilityzone
        ]

    def parse_meta(self, meta):
        self.stack_name = meta["StackName"]
        self.stack_id = meta["StackId"]
        self.region = meta["Region"]

    @property
    def pcf_elbdnsname(self):
        return self.parameters["PcfElbDnsName"]

    @property
    def pcf_elasticruntimes3buildpacksbucket(self):
        return self.parameters["PcfElasticRuntimeS3BuildpacksBucket"]

    @property
    def pcf_iamuseraccesskey(self):
        return self.parameters["PcfIamUserAccessKey"]

    @property
    def pcf_iamusersecretaccesskey(self):
        return self.parameters["PcfIamUserSecretAccessKey"]

    @property
    def pcf_vpc(self):
        return self.parameters["PcfVpc"]

    @property
    def pcf_opsmanageradminpassword(self):
        return self.parameters["PcfOpsManagerAdminPassword"]

    @property
    def pcf_opsmanagers3bucket(self):
        return self.parameters["PcfOpsManagerS3Bucket"]

    @property
    def pcf_vmssecuritygroupid(self):
        return self.parameters["PcfVmsSecurityGroupId"]

    @property
    def pcf_privatesubnetavailabilityzone(self):
        return self.parameters["PcfPrivateSubnetAvailabilityZone"]

    @property
    def pcf_privatesubnet2availabilityzone(self):
        return self.parameters["PcfPrivateSubnet2AvailabilityZone"]

    @property
    def pcf_privatesubnetid(self):
        return self.parameters["PcfPrivateSubnetId"]

    @property
    def pcf_privatesubnet2id(self):
        return self.parameters["PcfPrivateSubnet2Id"]

    @property
    def pcf_rdsaddress(self):
        return self.parameters["PcfRdsAddress"]

    @property
    def pcf_rdsusername(self):
        return self.parameters["PcfRdsUsername"]

    @property
    def pcf_rdspassword(self):
        return self.parameters["PcfRdsPassword"]

    @property
    def pcf_rdsport(self):
        return self.parameters["PcfRdsPort"]

    @property
    def pcf_elasticruntimes3buildpacksbucket(self):
        return self.parameters["PcfElasticRuntimeS3BuildpacksBucket"]

    @property
    def pcf_elasticruntimes3dropletsbucket(self):
        return self.parameters["PcfElasticRuntimeS3DropletsBucket"]

    @property
    def pcf_elasticruntimes3packagesbucket(self):
        return self.parameters["PcfElasticRuntimeS3PackagesBucket"]

    @property
    def pcf_elasticruntimes3resourcesbucket(self):
        return self.parameters["PcfElasticRuntimeS3ResourcesBucket"]

    @property
    def pcf_pcfnumberofazs(self):
        return int(self.parameters["PcfNumberOfAZs"])

    @property
    def pcf_pcfcustomresourcesqsqueueurl(self):
        return self.parameters["PcfCustomResourceSQSQueueUrl"]

    @property
    def pcf_pcfwaithandle(self):
        return self.parameters["PcfWaitHandle"]

    @property
    def pcf_pcfopsmanagerinstanceip(self):
        return self.parameters["PcfOpsManagerInstanceIP"]

    @property
    def pcf_input_pivnettoken(self):
        return self.input_parameters["PivnetToken"]

    @property
    def pcf_input_pcfkeypair(self):
        return self.input_parameters["PCFKeyPair"]

    @property
    def pcf_input_adminemail(self):
        return self.input_parameters["AdminEmail"]

    @property
    def pcf_input_elbprefix(self):
        return self.input_parameters["ElbPrefix"]

    @property
    def pcf_input_hostedzoneid(self):
        return self.input_parameters["HostedZoneId"]

    @property
    def pcf_input_domain(self):
        return self.input_parameters["Domain"]

    @property
    def pcf_input_skipsslvalidation(self):
        return self.input_parameters["SkipSSLValidation"]

    @property
    def opsman_url(self):
        return "https://opsman.{}".format(self.pcf_input_domain)

    def get_s3_endpoint(self):
        stack_region = self.region
        if stack_region == "us-east-1":
            return "s3.amazonaws.com"
        else:
            return "s3-{}.amazonaws.com".format(stack_region)

    def get_parameters(self):
        self.parameters = {}
        client = boto3.client(
            service_name='ssm', region_name=self.region
        )
        ssm_response = client.get_parameter(
            Name="{}.SSMParameterJSON".format(self.stack_name),
            WithDecryption=False
        )

        json_param_document = ssm_response.get("Parameter")
        params = json.loads(json_param_document['Value'])
        for param_name in params:
            self.parameters[param_name] = params[param_name]

    def describe_stack(self):
        self.input_parameters = {}
        client = boto3.client(
            service_name='cloudformation', region_name=self.region
        )
        response = client.describe_stacks(StackName=self.stack_id)
        param_results = response['Stacks'][0].get("Parameters")

        for result in param_results:
            self.input_parameters[result.get('ParameterKey')] = result['ParameterValue']

    def parse_version_config(self, version_config):
        ert = version_config.get('ert')
        stemcell = version_config.get('stemcell')

        self.ert_release_id = ert.get('id')
        self.ert_release_version = ert.get('version')
        self.ert_release_sha256 = ert.get('sha256')

        self.stemcell_release_id = stemcell.get('id')
        self.stemcell_release_version = stemcell.get('version')
        self.stemcell_release_sha256 = stemcell.get('sha256')


def read_version_config():
    with open(version_config_file_path) as version_config_file:
        return json.load(version_config_file)


def read_meta():
    with open(metadata_file) as meta_json:
        return json.load(meta_json)


def chunk(l, n):
    return list(__chunk_generator(l, n))


def __chunk_generator(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
