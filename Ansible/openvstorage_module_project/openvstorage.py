#!/usr/bin/python

"""
Title: Open vAnsible
Description: Ansible Module for Open vStorage
Maintainer: Jonas Libbrecht
Version: 1.0
"""

"""
Section: Static variables
"""

OVS_CONFIG = "/opt/OpenvStorage/config/ovs.json"
OVS_CLUSTER_CONF = "/opt/OpenvStorage/config/arakoon/ovsdb/ovsdb.cfg"
ALBA_MAN_CONFIG = "/opt/alba-asdmanager/config/config.json"

"""
Section: Import package(s)
"""

#general packages
import contextlib
import warnings
import commands
import datetime
import StringIO
import os.path
import socket
import struct
import fcntl
import json
import time
import sys
import ast

#ovs packages
if os.path.isfile(OVS_CONFIG):
	#OVS is installed
	with open(OVS_CONFIG) as data_file:
		data = json.load(data_file)
		if data['core']['nodetype'] == 'UNCONFIGURED':
			#OVS is not configured yet
			HAS_OVS = False
		else:
			#OVS is configured
			sys.path.append('/opt/OpenvStorage') 
			from ovs.dal.hybrids.vdisk import VDisk
			from ovs.extensions.generic.system import System
			from ovs.dal.lists.storagerouterlist import StorageRouterList
			HAS_OVS = True
else:
	#OVS is not installed
	HAS_OVS = False

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
	- Ubuntu 14.04.x (for cluster)
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
# - You can add as many MASTERS as you like, but it has to be uneven to avoid split-brain
# - You can add as many NON-MASTER nodes as you like, you need at least 3 MASTER NODES for 1 or more NON-MASTER NODE

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
	DESCRIPTION: Gather facts from OVS installation
	IMPORTANT_INFO: Local configs will be deprecated in versions higher than 2.6.1
	"""
	
	facts = {}

	if os.path.isfile(OVS_CONFIG):
		with open(OVS_CONFIG) as data_file:
			data = json.load(data_file)
			ovs = {
				'cluster_id': data['support']['cid'],
				'node_id': data['support']['nid'],
				'ovs_com_ip': data['grid']['ip'],
				'is_installed': True,
				'setup_completed': data['core']['setupcompleted'],
				'is_registered': data['core']['registered'],
				'node_type': data['core']['nodetype'],
				'base_dir': data['core']['basedir'],
				'config_dir': data['core']['cfgdir'],
                        	'log_dir': data['logging']['path'],
                        	'heartbeat_enabled': data['support']['enabled'],
                        	'remote_support_enabled': data['support']['enablesupport'],
#				'mds_ports': str(data['ports']['mds']).strip('[]'),
#				'storagedriver_ports': str(['ports']['storagedriver'][1]).strip('[]'),
#				'arakoon_ovsdb_ports': str(['ports']['arakoon']).strip('[]')
			}
			facts.update({'Open vStorage': ovs})
	else:
		not_ovs = {
			'is_installed': False
		}
		facts.update({'Open vStorage': not_ovs})

	if os.path.isfile(ALBA_MAN_CONFIG):
		with open(ALBA_MAN_CONFIG) as data_file:
			data = json.load(data_file)
			alba_man = {
				'is_installed': True,
                        	'node_id': data['main']['node_id']
			}
			facts.update({'Alba ASD manager': alba_man})
	else:
		not_alba_man = {
			'is_installed': False
		}
		facts.update({'Alba ASD manager': not_alba_man})

	return facts
	
def create_preconfig(module, node_information):
        """
        DESCRIPTION: create OVS preconfig installation answer file
	IMPORTANT_INFO: can be replaced with jinja2 implementation in future
        """

	#preambe
	join_cluster = False
	if node_information['master_ip'] != node_information['hypervisor_ip'] or node_information['ovs_master'] == "False" or node_information['ovs_master'] == "false":
		join_cluster = True

	if join_cluster == True and node_information['master_ip'] == node_information['hypervisor_ip']:
		module.fail_json(msg="extra node can't be depoyed as master, please change `master_ip` or change `ovs_master` to True")

	#write the preconfig
	try:
		target = open('/tmp/openvstorage_preconfig.cfg', 'w+')
		target.write('[setup]\n')
		target.write('target_ip = %s\n' % node_information['hypervisor_ip'])
        	target.write('target_password = %s\n' % node_information['hypervisor_password'])
        	target.write('cluster_name = %s\n' % node_information['cluster_name'])
        	target.write('cluster_ip = %s\n' % node_information['hypervisor_ip'])
        	target.write('master_ip = %s\n' % node_information['master_ip'])
        	target.write('master_password = %s\n' % node_information['master_password'])
        	target.write('join_cluster = %s\n' % join_cluster)
        	target.write('hypervisor_type = %s\n' % node_information['hypervisor_type'])
        	target.write('hypervisor_name = %s\n' % node_information['hypervisor_name'])
        	target.write('hypervisor_ip = %s\n' % node_information['hypervisor_ip'])
        	target.write('hypervisor_username = %s\n' % node_information['hypervisor_user'])
        	target.write('hypervisor_password = %s\n' % node_information['hypervisor_password'])
        	target.write('auto_config = True\n')
        	target.write('verbose = True\n')
        	target.write('configure_memcached = True\n')
        	target.write('configure_rabbitmq = True\n')
		target.write('enable_heartbeats = True')
		target.close()
	except Exception, e:
		module.fail_json(msg="Creating OVS pre-config failed with exception: %s" % e)

	return os.path.isfile('/tmp/openvstorage_preconfig.cfg')

def deploy_ovs(module, is_master):
        """
        DESCRIPTION: Deploy OVS on node in master or extra mode
        """

	if os.path.isfile('/tmp/openvstorage_preconfig.cfg'):
		if os.path.isdir('/opt/OpenvStorage'):
			sys.path.append('/opt/OpenvStorage')
			from ovs.lib.setup import SetupController
			
			if is_master == True or is_master == "True" or is_master == "true":
				with _stdout_redirect(StringIO.StringIO()) as log_stdout:
					SetupController.setup_node(force_type='master')
			else:
				with _stdout_redirect(StringIO.StringIO()) as log_stdout:
					SetupController.setup_node(force_type='extra')

			log_stdout.seek(0)
			log_output = log_stdout.read()

			if "Setup complete." and "Point your browser to" in log_output:
				return True
			else: 
				return log_output
		else:
			module.fail_json(msg="Open vStorage does not seem to be installed, please check with 'dpkg -l | grep openvstorage'")
	else:
		module.fail_json(msg="preconfig is not available, please deploy this first before running the OVS setup")

def post_deploy_check(module):
	"""
        DESCRIPTION: Post install check for services
	IMPORTANT_INFO: commands module is deprecated in Python 3.0
        """

	failed_services = []
	services = ['memcached', 'nginx', 'rabbitmq-server']
	main_output = commands.getoutput('ps -A')

	for service in services:
		count = 0
		while(count < 5):
			if service not in main_output:
				if service == 'rabbitmq-server':				
					service_output = start_rabbitmq(module, True)
				else:
					service_output = commands.getoutput('service %s start' % service)
			else:
				#service successfully started
				break
			#end
			main_output = commands.getoutput('ps -A')
			count += 1
			if count == 5:
				#debug: print service_output
				failed_services.append(service)
			time.sleep(1)
	
	if len(failed_services) > 0:
		module.fail_json(msg="An unexpected error occured, some services failed to start during setup: \n%s" % str(failed_services).strip('[]'))
	else:
		return True
	
def stop_rabbitmq(module):
	"""
        DESCRIPTION: Stops rabbitMQ the clean way
        """

	output = commands.getoutput('rabbitmqctl stop_app; sleep 3')
	if 'done' not in output:
		module.fail_json(msg="An unexpected error has occured during clean stop of rabbitMQ: \n%s" % output)
	else:
		return True

def start_rabbitmq(module, is_post_deploy_check):
	"""
        DESCRIPTION: Starts rabbitMQ the clean way
        """
	
	output = commands.getoutput('rabbitmqctl start_app; sleep 3; rabbitmqctl set_policy ha-all "^(volumerouter|ovs_.*)$" \'{"ha-mode":"all"}\'; sleep 3')
	if 'done' not in output and output.count("done") == 2:
		if is_post_deploy_check:
                	return output
		else:
			module.fail_json(msg="An unexpected error has occured during clean start of rabbitMQ: \n%s" % output)
        else:
                return True

def reset_rabbitmq(module):
        """
        DESCRIPTION: Resets rabbitMQ the clean way
        """
	output = commands.getoutput("rabbitmqctl stop_app; sleep 3; rabbitmqctl reset; sleep 3")
	if 'done' not in output and output.count("done") == 2:
                module.fail_json(msg="An unexpected error has occured during clean start of rabbitMQ: \n%s" % output)
        else:
                return True

def flush_node(module, storagerouter_ip):
        """
        DESCRIPTION: Flush write buffer to backend
        """

	sr_info = StorageRouterList.get_by_ip(ip)
        vdisks_by_guid = sr_info.vdisks_guids

        for vdisk_guid in vdisks_by_guid:
        	disk = VDisk(vdisk_guid)
                snapshot_name = "flush_snapshot"
		
		#create snapshot
                disk.storagedriver_client.create_snapshot(str(disk.volume_id), snapshot_name)

		#check if snapshot is synced to the backend
                while disk.storagedriver_client.info_snapshot(str(disk.volume_id), snapshot_name).in_backend == False:
                	time.sleep(5)

		#delete snapshot if sync is completed
		disk.storagedriver_client.delete_snapshot(str(disk.volume_id), snapshot_name)

def health_check(module):
        """
        DESCRIPTION: Perform health check on OVS node
	INFO: implementation of OVS health check library
        """

	module.fail_json(msg="Health check module not yet implemented, it still in development stage")

@contextlib.contextmanager
def _stdout_redirect(where):
	"""
        DESCRIPTION: Redirect print output of other python scripts to a variable
        """

	sys.stdout = where
	try:
		yield where
	finally:
		sys.stdout = sys.__stdout__

def _get_wrong_keys(current_dict, config_dict):
        """
        DESCRIPTION: Compare given dict with standard config dict
        """

	config_dict, current_dict = config_dict, current_dict
	set_current, set_past = set(config_dict.keys()), set(current_dict.keys())
        intersect = set_current.intersection(set_past)
        return set_past - intersect
def _get_wrong_values(current_dict, config_dict):
        """
        DESCRIPTION: Compare values in given dict with type of standard config dict
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
	
	#Ansible module implementation
	#
	#
	#

	config_deploy = {
		'cluster_name': str,
		'master_ip': str,
		'master_password': str,
		'ovs_master': str, #should be bool but it is not working for some reason
		'hypervisor_name': str,
		'hypervisor_ip': str,
		'hypervisor_user': str,
		'hypervisor_password': str,
		'hypervisor_type': str
	}

	module = AnsibleModule(
    		argument_spec = dict(
			ovs_facts = dict(required=False, default=False, type='bool'),
			state = dict(
				required=True, 
				choices=[
					'present', #says hello to ovs_node
					'setup', #execute pre_config and setup
					'pre_config', #execute pre_config only
					'shutdown', #execute flush and clean shutdown (one or more nodes)
					'restart', #execute flush and clean restart (one or more nodes)
					'health_check', #execute health check
					'reconfigure', #configure or reconfigure something in ovs
				]), 
        		deploy = dict(required=False, type='dict', default={}), #needs state: setup or no_setup
			flush = dict(required=False, default=None, type='str'),
			health_check = dict(
				required=False, 
				default='present',
				choices=[
					'present',
					'basic',
					'extended']
			),
			reconfigure_node = dict(
				required=False, 
				default='present', 
				choices=[
					'present',
					'add_role_disk',
					'remove_role_disk']
			), #perform node-wise change (e.g. configure role on disk, configure backend, configure vpool, configure hypervisor_management_center) 
			reconfigure_cluster = dict(
				required=False, 
				default='present', 
				choices=[
					'present',
					'enable_maintenance',
					'disable_maintenance']
			), #perform cluster-wise change (e.g. put a online node in maintenance mode, demote a 'broken' offline node, add-user, perform update/upgrade, configure heartbeat, configure remote_access_support, configure hypervisor_management_center, configure a ovs-user, configure a OAuth2-user, register ovs)
    		),
		supports_check_mode=False,
		mutually_exclusive=[
			['deploy', 'flush'],
			['deploy', 'health_check'],
			['deploy', 'reconfigure_node'],
			['deploy', 'reconfigure_cluster'],
		],
		required_together=[
			['state', 'deploy'],
		],
	)
	
	#OVS implementation
	#
	#
	#

	#facts can be executed at all times
	ovs_facts = module.params['ovs_facts']
	if ovs_facts:
		try:
			module.exit_json(ansible_facts=gather_facts())
		except Exception, e:
			module.fail_json(msg="Fact gather failed with exception: %s" % e)

	#check if OVS is installed
	if not HAS_OVS:
		state = module.params['state']
		deploy = module.params['deploy']
		
		if bool(deploy):
			if len(_get_wrong_keys(deploy, config_deploy)) > 0:
				module.fail_json(msg="Following keys are not valid in the deploy argument: "+",".join(_get_wrong_keys(deploy, config_deploy)))
			elif len(_get_wrong_values(deploy, config_deploy)) > 0:
				module.fail_json(msg="Following values are not correct (wrong type): %s" % str(_get_wrong_values(deploy, config_deploy)).strip('[]'))
		
			if state == 'setup':
				is_pre_created = create_preconfig(module, deploy)			
				is_post_created = deploy_ovs(module, deploy['ovs_master'])
				is_post_check_ok = post_deploy_check(module)
			
				if is_pre_created == True and is_post_created == True and is_post_check_ok == True:
					module.exit_json(changed=True)
				else:
					module.fail_json(msg="Error during deployment, please check /var/log/ovs/lib.log for more information: \n%s" % is_post_created)

			elif state == 'pre_config':
				is_created = create_preconfig(module, deploy)

				if is_created:
                                	module.exit_json(changed=is_created)
                        	else:
                                	module.fail_json(msg="Pre-config failed to create due to an unexpected error. Maybe /tmp/ is not world-accessable?")
			else:
				module.fail_json(msg="Deploy module cannot be combined with state '%s'" % state)

		elif state == 'present':
			module.exit_json(changed=False)

		elif state in ['setup', 'pre_config']:
			module.fail_json(msg="State '%s' is not available if deploy module is not included" % state)

		else:
			module.fail_json(msg="State '%s' is not available if OVS is not installed" % HAS_OVS)			
	else:
		module.fail_json(msg="post-install commands are not yet available, sorry ...")
		
"""
Section: Ansible
"""

# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
