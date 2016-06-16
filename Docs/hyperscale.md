# HyperScale

## Architecture
* The Ansible script will deploy a cluster with 3 types of nodes: controllers, compute and capacity nodes.
    * **Controllers:** Dedicated nodes to run the master services and hold the distributed DBs.
    * **Compute nodes:** These nodes run the extra services, are configured with vPools and run the VMs.
    * **Capacity nodes:** The capacity servers for the backend storage.

{% include "controlmachine.md" %}

## Deploy the cluster

* Install `Ubuntu 14.04` on all servers of the cluster. Username (default usage is `root`) and password should be the same on all servers.

* Edit the Ansible inventory file (`/etc/ansible/hosts`) and add the controller, compute and storage nodes to describe the cluster according to the below example:

```
#
# This is the default ansible 'hosts' file.
#

#cluster overview

[controllers]
ctl01 ansible_host=10.100.198.1 hypervisor_name=mas01
ctl02 ansible_host=10.100.198.2 hypervisor_name=mas02
ctl03 ansible_host=10.100.198.3 hypervisor_name=mas03

[computenodes]
cmp01 ansible_host=10.100.198.4 hypervisor_name=hyp01

[storagenodes]
str01 ansible_host=10.100.198.11 api_port=8500 excellerated_backend=false
str02 ansible_host=10.100.198.12 api_port=8500 excellerated_backend=false
str03 ansible_host=10.100.198.13 api_port=8500 excellerated_backend=true

#cluster details

[cluster:children]
controllers
computenodes
storagenodes

[cluster:vars]
cluster_password=rooter
cluster_type=KVM
install_master_ip=10.100.198.1
```

* Execute the HyperScale playbook. *(It is advised to execute the playbook in debug mode* `-vvvv`*)*

```
cd ~/dev_ops/Ansible/hyperscale_geoscale_project/
ansible-playbook openvstorage_hyperscale_setup.yml -u root -k -vvvv
```

The above playbook will install the necessary packages and run `ovs setup` on the controllers and compute nodes. It will also add the storage nodes to the Open vStorage framework database (`ovsdb`) through the `asd-manager setup`.

Next steps are assigning roles to the SSDs and PCIe flash cards, create the backend and create the first vPool.

## How fast is the playbook? (3 controller nodes, 1 compute node & 3 storage nodes on 1Gbit network)

```
Friday 22 April 2016  17:12:52 +0200 (0:00:00.530)       0:13:48.209 **********
===============================================================================
TASK: install controllers packages ------------------------------------ 170.95s
TASK: install compute packages ---------------------------------------- 169.11s
TASK: installing the open vstorage controllers ------------------------ 139.04s
TASK: install required packages ---------------------------------------- 76.79s
TASK: installing the open vstorage compute nodes ----------------------- 42.06s
TASK: install storage packages ----------------------------------------- 36.17s
TASK: fetch all etcd endpoints from controllers ------------------------ 14.07s
TASK: finalizing setup ------------------------------------------------- 12.81s
TASK: check hosts their availability ----------------------------------- 12.58s
TASK: create etcd proxy on storage nodes -------------------------------- 2.04s
TASK: installing the open vstorage storage nodes ------------------------ 0.53s
TASK: add openvstorage apt-repo ----------------------------------------- 0.40s
TASK: add performance settings to cluster ------------------------------- 0.39s
TASK: start etcd proxy on storage nodes --------------------------------- 0.26s
TASK: create required directories for alba on storage nodes ------------- 0.19s
TASK: parse etcd endpoints to a list ------------------------------------ 0.03s

real    13m51.644s
user    1m8.280s
sys     0m36.608s
```
{% include "troubleshooting.md" %}
