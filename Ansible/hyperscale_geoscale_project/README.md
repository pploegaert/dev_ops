# Open vStorage - GeoScale / Hyperscale Setup through Ansible

##Intro

###Description
Installs a Open vStorage GeoScale / HyperScale cluster through Ansible

###Requirements
* 1 Configuration master: 1 Linux VM with Ansible 2.0 or higher installed
* At least 3 OVS controllers: These will act as the cluster-masters, they manage the databases of the cluster. (If you go for more than 3, pick an uneven amount to avoid split-brain)
* At least 1 OVS compute node: These will act as compute power for your customer VM's
* At least 1 OVS storage node: These will act as storage power for your customer VM's

##How-to

###Fetching the git repo

```
sudo apt-get install git
git clone -b fargo-release3 https://github.com/openvstorage/dev_ops.git
```

###Installing & configuring

* Installing ansible
```
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
```

* Copy the openvstorage module to the ansible library

```
mkdir -p /usr/lib/ansible
cp dev_ops/Ansible/openvstorage_module_project/openvstorage.py /usr/lib/ansible
```

* Configuring ansible libraries (`/etc/ansible/ansible.cfg`)

```
##change this part
 
#inventory      = /etc/ansible/hosts
#library        = /usr/share/my_modules/
 
##to this
 
inventory      = /etc/ansible/hosts
library        = /usr/lib/ansible
```

* Configuring ansible for your Open vStorage cluster (`/etc/ansible/hosts`)

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

* Starting the installation

```
cd dev_ops/Ansible/hyperscale_project/
 
#Execute in debug mode
ansible-playbook openvstorage_hyperscale_setup.yml -u root -k -vvvv
 
#Execute in normal mode
ansible-playbook openvstorage_hyperscale_setup.yml -u root -k
```

## Playbook runtime: (3 controller nodes, 1 compute node & 3 storage nodes on 1Gbit network)
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
