#!/usr/bin/python

"""
Title: Open vAnsible
Description: Ansible Module for Open vStorage
Maintainer: Jonas Libbrecht
Licensed under: AGPLv3
Version: 3.0
"""

import contextlib
import commands
import StringIO
import sys

ovs_present = False
ovs_configured = False
asdmanager_present = False
asdmanager_configured = False

# detect if asdmanager has already been installed/configured
try:
    sys.path.append('/opt/asd-manager/')
    from source.asdmanager import setup

    asdmanager_present = True
except ImportError:
    pass

if len(commands.getoutput('ps auxf | grep [a]sdmanager').split(' ')) != 1:
    asdmanager_configured = True

# detect if openvstorage has already been installed/configured
try:
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.hybrids.vdisk import VDisk
    from ovs.extensions.generic.system import System
    from ovs.extensions.generic.sshclient import SSHClient
    from ovs.dal.lists.storagerouterlist import StorageRouterList
    from ovs.extensions.db.etcd.configuration import EtcdConfiguration
    from etcd import EtcdConnectionFailed, EtcdException, EtcdKeyError, EtcdKeyNotFound

    ovs_present = True
except ImportError:
    pass

if ovs_present:
    root_client = SSHClient(endpoint='127.0.0.1', username='root')
    unique_id = System.get_my_machine_id(root_client)

    try:
        setup_completed = False
        promote_completed = False

        type_node = EtcdConfiguration.get('/ovs/framework/hosts/{0}/type'.format(unique_id))
        setup_completed = EtcdConfiguration.get('/ovs/framework/hosts/{0}/setupcompleted'.format(unique_id))
        if type_node == 'MASTER':
            promote_completed = EtcdConfiguration.get('/ovs/framework/hosts/{0}/promotecompleted'.format(unique_id))
        if setup_completed is True and (promote_completed is True or type_node == 'EXTRA'):
            ovs_configured = True
    except (EtcdConnectionFailed, EtcdKeyNotFound, EtcdException):
        ovs_configured = False


"""
Section: Documentation
"""

DOCUMENTATION = '''
---
module: openvstorage
short_description: Setup/manage/troubleshoot a Open vStorage Cluster
description:
    - Setup/manage/troubleshoot a Open vStorage Cluster the easy way
version_added: "1.0"
options:
    state:
      description:
        - Indicates desired mode your using for Open vStorage tasks
        - Works with options
          required: true
      default: None
      choices: ['present', 'setup', 'pre_config', 'shutdown', 'restart', 'health_check', 'reconfigure']
    deploy:
      description:
        - Configuration details for Open vStorage 'setup' e.g. cluster_name
        - A key, value dictionary
      required: false
          default: None

notes:
    - Open vStorage tasks must delegate_to its tasks to a system that has Open vStorage installed
    - This module can be run from a configration-master/jumphost/...

author: "Jonas Libbrecht <jonas.libbrecht@openvstorage.com>"
requirements:
    - "python >= 2.7"
    - "ansible 2.0"
    - "qemu-kvm"
    - "libvirt0"
    - "python-libvirt"
    - "virtinst"
    - "ntp"
    - Open vStorage:
        - Hyperconverged: "openvstorage-hc" (on all nodes)
        - Hyperscale:
            - "openvstorage-backend" (on controller/compute nodes)
            - "openvstorage-sdm" (on storage nodes)
    - Ubuntu 14.04.x
'''

EXAMPLES = '''
#Deploy Open vStorage 1 NODE SETUP
#Returns changed = True when the task has succeeded
#Returns failure when Open vStorage task has failed due to a known or unknown error
# Options ['state', 'deploy'] are required together

    - name: 1st node (MASTER)
      openvstorage:
            state: setup
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "True"
               hypervisor_name: "hyp01"
               hypervisor_ip: "172.19.0.100"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.100

#Deploy the Open vStorage pre-configuration file only on a HYPERCONVERGED 1 NODE SETUP
#Returns changed = True when the task has succeeded
#Returns failure when Open vStorage task has failed due to a known or unknown error
# Options ['state', 'deploy'] are required together
#Notes: No Open vStorage installation will take place

    - name: 1st node (MASTER)
      openvstorage:
            state: pre_config
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "True"
               hypervisor_name: "hyp01"
               hypervisor_ip: "172.19.0.100"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.100

#Deploy Open vStorage 4 NODE SETUP
#Returns changed = True when the task has succeeded
#Returns failure when Open vStorage task has failed due to a known or unknown error
# Options ['state', 'deploy'] are required together
#Notes: 
# - You can add as many MASTERS as you like.
# - You can add as many NON-MASTER nodes as you like, you need at least 3 MASTER NODES for 1 or more NON-MASTER NODE(S)

    - name: 1st node (MASTER)
      openvstorage:
            state: setup
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "True"
               hypervisor_name: "hyp01"
               hypervisor_ip: "172.19.0.100"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.100

    - name: 2nd node (MASTER)
      openvstorage:
            state: setup
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "True"
               hypervisor_name: "hyp02"
               hypervisor_ip: "172.19.0.101"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.101

    - name: 3rth node (MASTER)
      openvstorage:
            state: setup
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "True"
               hypervisor_name: "hyp03"
               hypervisor_ip: "172.19.0.102"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.102

    - name: 4th node (NON-MASTER)
      openvstorage:
            state: setup
            deploy:
               cluster_name: "testcluster01"
               master_ip: "172.19.0.100"
               master_password: "JSkxIAYbULGlx2AUe0JE"
               ovs_master: "False"
               hypervisor_name: "hyp04"
               hypervisor_ip: "172.19.0.103"
               hypervisor_user: "root"
               hypervisor_password: "JSkxIAYbULGlx2AUe0JE"
               hypervisor_type: "KVM"
      run_once: true
      delegate_to: 172.19.0.103
'''

"""
Section: Methods
"""


def gather_facts():
    """
    Gather facts from a node

    :returns dictionary with information about Open vStorage on the target node
    :rtype dict
    """

    facts = {}

    # fetch present information from 'ovs setup'
    setup_information = {
        'ovs_installed': ovs_present,
        'ovs_setup_completed': ovs_configured,
        'alba_installed': asdmanager_present,
        'alba_setup_completed': asdmanager_configured
    }

    facts.update({'general': setup_information})

    # fetch ovs information if ovs is installed and configured
    if ovs_present and ovs_configured:

        # pre-fetch data
        openvstorage_id = open('/etc/openvstorage_id', 'r')
        node_id = openvstorage_id.read().strip()
        openvstorage_id.close()
        support = EtcdConfiguration.get('/ovs/framework/support')
        grid_ip = str(EtcdConfiguration.get('/ovs/framework/hosts/{0}/ip'.format(node_id)))

        ovs_cluster_information = {
            'cluster_id': str(EtcdConfiguration.get('/ovs/framework/cluster_id')),
            'node_id': str(node_id),
            'grid_ip': grid_ip,
            'node_type': str(EtcdConfiguration.get('/ovs/framework/hosts/{0}/type'.format(node_id))),
            'base_dir': str(EtcdConfiguration.get('/ovs/framework/paths').get('basedir')),
            'heartbeat_enabled': str(support.get('enabled')),
            'remote_support_enabled': str(support.get('enablesupport')),
            'etcd_proxy': '{0}=http://{1}:2380'.format(node_id, grid_ip)
        }
        facts.update({'ovs': ovs_cluster_information})

    return facts


def create_ovs_preconfig(module, node_information):
    """
    Create Open vStorage pre-config installation answer file

    :param module: Ansible module
    :type module: Ansible module

    :param node_information: information fetched from the Ansible Playbook
    :type node_information: dict

    :returns if pre-config exists
    :rtype bool
    """

    try:
        # create required directories
        required_directory = '/opt/OpenvStorage/config'
        if not os.path.exists(required_directory):
            os.makedirs(required_directory)

        # deploy the pre-config
        with open('/opt/OpenvStorage/config/openvstorage_preconfig.json', 'w') as preconfig:

            data = {
                "setup":
                {
                    "master_ip": node_information['master_ip'],
                    "cluster_ip": node_information['hypervisor_ip'],
                    "master_password": node_information['master_password'],
                    "hypervisor_name": node_information['hypervisor_name'],
                    "hypervisor_type": node_information['hypervisor_type'],
                    "enable_heartbeats": True,
                    "node_type": node_information['node_type']
                }
            }

            json.dump(data, preconfig)

    except Exception, e:
        module.fail_json(msg="Creating Open vStorage pre-config failed with exception: {0}".format(e))

    return os.path.isfile('/opt/OpenvStorage/config/openvstorage_preconfig.json')


def deploy_ovs(module):
    """
    Start the OPEN vSTORAGE setup on a future Open vStorage node

    :param module: Ansible module
    :type module: Ansible module

    :returns if Open vStorage deployment was correctly executed
    :rtype bool
    """

    if os.path.isfile('/opt/OpenvStorage/config/openvstorage_preconfig.json'):
        if ovs_present and not ovs_configured:
            sys.path.append('/opt/OpenvStorage')
            from ovs.lib.setup import SetupController

            with _stdout_redirect(StringIO.StringIO()) as log_stdout:
                SetupController.setup_node()

            log_stdout.seek(0)
            log_output = log_stdout.read()

            if not asdmanager_present:
                # hyperscale or geoscale
                return _ovs_post_deploy_check(log_output)
            else:
                # hyperconverged
                if _ovs_post_deploy_check(log_output) and _asd_managers_post_deploy_check(log_output):
                    return True
                else:
                    return False

        else:
            module.fail_json(msg="Open vStorage does not seem to be installed at this time!")
    else:
        module.fail_json(msg="Pre-config is not available at this time!")


def create_alba_preconfig(module, node_information):
    """
    Creates the ASD MANAGER pre-config on a future Open vStorage node

    :param module: Ansible module
    :type module: Ansible module

    :returns if the preconfig exists
    :rtype bool
    """

    try:
        # create required directories
        required_directory = '/opt/OpenvStorage/config'
        if not os.path.exists(required_directory):
            os.makedirs(required_directory)

        # deploy the pre-config
        if not os.path.exists('/opt/OpenvStorage/config/openvstorage_preconfig.json'):
            with open('/opt/OpenvStorage/config/openvstorage_preconfig.json', 'w') as preconfig:

                data = {
                    "asdmanager":
                    {
                        "api_ip": node_information['api_ip'],
                        "api_port": int(node_information['api_port'])
                    }
                }

                json.dump(data, preconfig)

        else:
            preconfig = open('/opt/OpenvStorage/config/openvstorage_preconfig.json', 'r+w')

            data = json.load(preconfig)
            preconfig.seek(0)  # clear file till offset 0
            preconfig.truncate()

            if not data.get('asdmanager'):
                data['asdmanager'] = {
                    "api_ip": node_information['api_ip'],
                    "api_port": int(node_information['api_port'])
                }
            json.dump(data, preconfig)
            preconfig.close()

    except Exception, e:
        module.fail_json(msg="Creating Alba pre-config failed with exception: {0}".format(e))

    return os.path.isfile('/opt/OpenvStorage/config/openvstorage_preconfig.json')

def deploy_alba(module):
    """
    Start the ASD MANAGER setup on a future Open vStorage node (only for hyperscale/geoscale)
    We assume that the etcd proxy has already been set up and started.

    :param module: Ansible module
    :type module: Ansible module
    """

    if asdmanager_present:
        if not asdmanager_configured:
            sys.path.append('/opt/asd-manager/')
            from source.asdmanager import setup

            with _stdout_redirect(StringIO.StringIO()) as log_stdout:
                setup()

            log_stdout.seek(0)
            log_output = log_stdout.read()

            return _asd_managers_post_deploy_check(log_output)
        else:
            module.fail_json(msg="Alba can't be redeployed.")
    else:
        module.fail_json(msg="openvstorage-sdm packages seem to be absent on this node.")


def _asd_managers_post_deploy_check(log_output):
    """
    Checks if the ASD MANAGER setup was executed correctly

    :param module: Ansible module
    :type module: Ansible module

    :param log_output: log output from a python file
    :type log_output: str

    :returns if ASD manager setup was successfully executed
    :rtype bool
    """

    if "ASD Manager setup completed" in log_output:
        return True
    else:
        return False


def _ovs_post_deploy_check(log_output):
    """
    Checks if the OPEN vSTORAGE setup was executed correctly

    :param module: Ansible module
    :type module: Ansible module

    :param log_output: log output from a python file
    :type log_output: str

    :returns if Open vStorage setup was successfully executed
    :rtype bool
    """

    if "Setup complete." and "Point your browser to" in log_output:
        return True
    else:
        return False


def framework_post_deploy_check(module):
    """
    Post-install check for non-openvstorage framework services

    :param module: Ansible module
    :type module: Ansible module

    :returns if all requested services are up
    :rtype bool
    """

    failed_services = []
    services = ['memcached', 'nginx', 'rabbitmq-server']
    main_output = commands.getoutput('ps -A')

    for service in services:
        count = 0
        while count < 5:
            if service not in main_output:
                if service == 'rabbitmq-server':
                    start_rabbitmq(module)
                else:
                    commands.getoutput('service {0} start'.format(service))
            else:
                # service successfully started
                break
            main_output = commands.getoutput('ps -A')
            count += 1
            if count == 5:
                failed_services.append(service)
            time.sleep(1)

    if len(failed_services) > 0:
        module.fail_json(msg="An unexpected error occured, some services failed to start during setup: \n{0}".format(str(failed_services).strip('[]')))
    else:
        return True


def stop_rabbitmq(module):
    """
    Stops rabbitMQ the clean way

    :param module: Ansible module
    :type module: Ansible module

    :returns if rabbitmq stop was correctly executed
    :rtype bool
    """

    output = commands.getoutput('rabbitmqctl stop_app; sleep 3')
    if 'done' not in output:
        module.fail_json(msg="An unexpected error has occured during clean stop of rabbitMQ: \n{0}".format(output))
    else:
        return True


def start_rabbitmq(module):
    """
    Starts rabbitMQ the clean way

    :param module: Ansible module
    :type module: Ansible module

    :param is_post_deploy_check: tells the function if this is triggered as post deployment check of Open vStorage
           or not.
    :type is_post_deploy_check: bool

    :returns log output of
    :rtype bool
    """

    output = commands.getoutput('rabbitmqctl start_app; sleep 3; rabbitmqctl set_policy ha-all "^(volumerouter|ovs_.*)$" \'{"ha-mode":"all"}\'; sleep 3')
    if 'done' not in output and output.count("done") == 2:
        return True
    else:
        module.fail_json(msg="An unexpected error has occured during clean start of rabbitMQ: \n{0}".format(output))


def reset_rabbitmq(module):
    """
    Resets rabbitMQ the clean way

    :param module: Ansible module
    :type module: Ansible module

    :returns if rabbitmq reset was correctly executed
    :rtype bool
    """
    output = commands.getoutput("rabbitmqctl stop_app; sleep 3; rabbitmqctl reset; sleep 3")
    if 'done' not in output and output.count("done") == 2:
        module.fail_json(msg="An unexpected error has occured during clean start of rabbitMQ: \n{0}".format(output))
    else:
        return True


def flush_node(storagerouter_ip):
    """
    Flush write buffer to backend

    :param storagerouter_ip: ip of a storage router were to perform the flush
    :type storagerouter_ip: str
    """

    sr_info = StorageRouterList.get_by_ip(storagerouter_ip)
    vdisks_by_guid = sr_info.vdisks_guids

    for vdisk_guid in vdisks_by_guid:
        disk = VDisk(vdisk_guid)
        snapshot_name = "flush_snapshot"

    # create snapshot
    disk.storagedriver_client.create_snapshot(str(disk.volume_id), snapshot_name)

    # check if snapshot is synced to the backend
    while not disk.storagedriver_client.info_snapshot(str(disk.volume_id), snapshot_name).in_backend:
        time.sleep(5)

    # delete snapshot if sync is completed
    disk.storagedriver_client.delete_snapshot(str(disk.volume_id), snapshot_name)


def health_check(module):
    """
    Perform health check on Open vStorage local node

    :param module: Ansible module
    :type module: Ansible module
    """

    module.fail_json(msg="Health check module not yet implemented, it still in development stage")


@contextlib.contextmanager
def _stdout_redirect(where):
    """
    Redirect print output of other python scripts to a variable
    """

    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


def _get_wrong_keys(current_dict, config_dict):
    """
    Compare given dict with standard config dict
    """

    config_dict, current_dict = config_dict, current_dict
    set_current, set_past = set(config_dict.keys()), set(current_dict.keys())
    intersect = set_current.intersection(set_past)

    return set_past - intersect


def _get_wrong_values(current_dict, config_dict):
    """
    Compare values in given dict with type of standard config dict
    """

    wrong_values = []
    for (k,v), (k2,v2) in zip(current_dict.items(), config_dict.items()):
        if v2 != type(v):
            wrong_values.append(k)

    return wrong_values

"""
Section: Main
"""


def main():

    config_deploy_ovs = {
        'master_ip': str,
        'master_password': str,
        'node_type': str,  # master or extra
        'hypervisor_name': str,
        'hypervisor_ip': str,
        'hypervisor_type': str
    }

    config_deploy_alba = {
        'api_ip': str,
        'api_port': str
    }

    module = AnsibleModule(
            argument_spec=dict(
            facts=dict(required=False, default=False, type='bool'),
            state=dict(
                required=True,
                choices=[
                    'present',       # pre-install: says hello to ovs_node
                    'setup',         # pre-install: execute pre_config and setup
                    'pre_config',    # pre-install: execute pre_config only
                    'shutdown',      # post-install: execute flush and clean shutdown (one or more nodes)
                    'restart',       # post-install: execute flush and clean restart (one or more nodes)
                    'health_check',  # post-install: execute health check
                    'reconfigure',   # post-install: configure or reconfigure something in ovs
                ]),
            ovs=dict(required=False, type='dict', default={}),   # needs state: setup or pre_config
            alba=dict(required=False, type='dict', default={}),  # needs state: setup or pre_config
            flush=dict(required=False, default=None, type='str'),
            health_check=dict(
                required=False,
                default='present',
                choices=[
                    'present',
                    'basic',
                    'extended']
            ),
            reconfigure_node=dict(
                required=False,
                default='present',
                choices=[
                    'present',
                    'add_role_disk',
                    'remove_role_disk']
            ),  # perform node-wise change (e.g. configure role on disk, configure vpool,
                # configure hypervisor_management_center)
            reconfigure_cluster=dict(
                required=False,
                default='present',
                choices=[
                    'present',
                    'enable_maintenance',
                    'disable_maintenance']
            ),  # perform cluster-wise change (e.g. put a online node in maintenance mode, demote a 'broken' offline
                # node, add-user, perform update/upgrade, configure heartbeat, configure remote_access_support,
                # configure hypervisor_management_center, configure a ovs-user, configure a OAuth2-user, register ovs)
            ),
        supports_check_mode=False,
        mutually_exclusive=[
            ['deploy', 'flush'],
            ['deploy', 'health_check'],
            ['deploy', 'reconfigure_node'],
            ['deploy', 'reconfigure_cluster'],
        ],
        required_together=[
            ['state', 'ovs'],
            ['state', 'alba'],
        ],
    )

    """
    Gathering facts
    """
    if module.params['facts']:
        module.exit_json(ansible_facts=gather_facts())

    if ovs_present or asdmanager_present:
        # check if Open vStorage is NOT configured yet
        if not ovs_configured and ovs_present:
            state = module.params['state']
            deploy = module.params['ovs']

            if bool(deploy):
                if len(_get_wrong_keys(deploy, config_deploy_ovs)) > 0:
                    module.fail_json(msg="Following keys are not valid in the deploy argument: " +
                                         ",".join(_get_wrong_keys(deploy, config_deploy_ovs)))
                elif len(_get_wrong_values(deploy, config_deploy_ovs)) > 0:
                    module.fail_json(msg="Following values are not correct (wrong type): {0}"
                                     .format(str(_get_wrong_values(deploy, config_deploy_ovs)).strip('[]')))

                if state == 'setup':
                    is_pre_created = create_ovs_preconfig(module, deploy)

                    # check if asdmanagers need to be preconfigured (for openvstorage-hc)
                    if asdmanager_present and is_pre_created:
                        alba = module.params['alba']
                        if bool(alba):
                            create_alba_preconfig(module, alba)
                        else:
                            module.fail_json(msg="No alba module present although the 'openvstorage-sdm' packages "
                                                 "are available ...")

                    is_post_created = deploy_ovs(module)
                    is_post_check_ok = framework_post_deploy_check(module)

                    if is_post_created and is_post_check_ok:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Error during Open vStorage deployment, please check /var/log/ovs/lib.log"
                                             " for more information: \n{0}".format(is_post_created))

                elif state == 'pre_config':
                    is_created = create_ovs_preconfig(module, deploy)

                    # check if asdmanagers need to be preconfigured (for openvstorage-hc)
                    if asdmanager_present and is_created:
                        alba = module.params['alba']
                        if bool(alba):
                            create_alba_preconfig(module, alba)
                        else:
                            module.fail_json(msg="No alba module present although the 'openvstorage-sdm' packages "
                                                 "are available!")

                    if is_created:
                            module.exit_json(changed=is_created)
                    else:
                            module.fail_json(msg="Pre-config failed to create due to an unexpected error.")
                else:
                    module.fail_json(msg="Deploy module cannot be combined with state '{0}'".format(state))

            elif state == 'present':
                module.exit_json(changed=False)

            elif state in ['setup', 'pre_config']:
                module.fail_json(msg="'openvstorage' seems to be installed but no 'ovs' module seems to be provided"
                                 .format(state))

            else:
                module.fail_json(msg="State '{0}' is not available "
                                     "if Open vStorage is not installed".format(state))

        # check if asdmanager is NOT configured yet
        elif not asdmanager_configured:
            state = module.params['state']
            deploy = module.params['alba']

            if bool(deploy):
                if len(_get_wrong_keys(deploy, config_deploy_alba)) > 0:
                    module.fail_json(msg="Following keys are not valid in the deploy argument: "+","
                                     .join(_get_wrong_keys(deploy, config_deploy_ovs)))
                elif len(_get_wrong_values(deploy, config_deploy_alba)) > 0:
                    module.fail_json(msg="Following values are not correct (wrong type): {0}"
                                     .format(str(_get_wrong_values(deploy, config_deploy_ovs)).strip('[]')))

                if state == 'setup':
                    is_pre_created = create_alba_preconfig(module, deploy)
                    is_post_created = deploy_alba(module)

                    if is_pre_created and is_post_created:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Error during alba deployment, "
                                             "please check the logfiles for more information")

                elif state == 'pre_config':
                    is_created = create_alba_preconfig(module, deploy)

                    if is_created:
                            module.exit_json(changed=True)
                    else:
                            module.fail_json(msg="Pre-config failed to create due to an unexpected error.")
                else:
                    module.fail_json(msg="Deploy module cannot be combined with state '{0}'".format(state))

            elif state == 'present':
                module.exit_json(changed=False)

            elif state in ['setup', 'pre_config']:
                module.fail_json(msg="State '{0}' is not available if deploy ['ovs', 'alba'] module is not included"
                                 .format(state))

            else:
                module.fail_json(msg="State '{0}' is not available if Open vStorage is not installed"
                                 .format(ovs_present))

        else:
            module.fail_json(msg="Post-install commands for Open vStorage or Alba are not yet available!")
    else:
        module.fail_json(msg="No Open vStorage packages do not seem installed at this time!")


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
