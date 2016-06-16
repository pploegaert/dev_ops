# Hyper-converged

## Architecture
* The Ansible script will deploy a cluster with 2 types of nodes: controllers and compute/storage nodes.
    * **Controllers:** Dedicated nodes to run the master services and hold the distributed DBs. Can be configured with vPools and run the VMs
    * **Compute/storage nodes:** These nodes run the extra services, are configured with vPools, run the VMs and store the actual data.

{% include "controlmachine.md" %}

## Deploy the cluster

* Install `Ubuntu 14.04` on all servers of the cluster. Username (default usage is `root`) and password should be the same on all servers.

* Edit the Ansible inventory file (`/etc/ansible/hosts`) and add the controller, compute/storage nodes to describe the cluster according to the below example:

```
#
# This is the default ansible 'hosts' file.
#

#cluster overview

[controllers]
ctl01 ansible_host=10.100.198.1 hypervisor_name=mas01 api_port=8500 excellerated_backend=false
ctl02 ansible_host=10.100.198.2 hypervisor_name=mas02 api_port=8500 excellerated_backend=false
ctl03 ansible_host=10.100.198.3 hypervisor_name=mas03 api_port=8500 excellerated_backend=false

[computenodes]
cmp01 ansible_host=10.100.198.4 hypervisor_name=hyp01 api_port=8500 excellerated_backend=false

#cluster details

[cluster:children]
controllers
computenodes

[cluster:vars]
cluster_password=rooter
cluster_type=KVM
install_master_ip=10.100.198.1
```

* Execute the Open vStorage HyperConverged playbook. *(It is advised to execute the playbook in debug mode* `-vvvv`*)*

```
cd ~/dev_ops/Ansible/hyperconverged_project/
ansible-playbook openvstorage_hyperconverged_setup.yml -u root -k -vvvv
```

The above playbook will install the necessary packages and run `ovs setup` on the controllers and compute/storage nodes.

Next steps are assigning roles to the SSDs and PCIe flash cards, create the backend and create the first vPool.

## How fast is the playbook? (3 controller nodes & 1 compute node on 1Gbit network)

```
Friday 22 April 2016  17:35:26 +0200 (0:00:12.733)       0:11:35.012 **********
===============================================================================
TASK: install controllers packages ------------------------------------ 176.44s
TASK: install compute packages ---------------------------------------- 168.71s
TASK: installing the open vstorage controllers ------------------------ 120.92s
TASK: installing the open vstorage compute nodes ----------------------- 43.94s
TASK: install required packages ---------------------------------------- 19.26s
TASK: finalizing setup ------------------------------------------------- 12.73s
TASK: check hosts their availability ----------------------------------- 12.57s
TASK: add performance settings to cluster ------------------------------- 0.27s
TASK: add openvstorage apt-repo ----------------------------------------- 0.20s

real    11m37.835s
user    0m55.560s
sys     0m29.860s
```

{% include "troubleshooting.md" %}
