# Open vStorage - Hyperconverged Setup through Ansible

##Intro

###Description
Installs a Open vStorage HyperConverged cluster through Ansible

###Requirements
* 1 Configuration master: 1 Linux VM with Ansible 2.0 or higher installed
* At least 3 OVS controllers: These will act as the cluster-masters, they manage the databases of the cluster. (If you go for more than 3, pick an uneven amount to avoid split-brain)
* At least 1 OVS compute node: These will act as compute power for your customer VM's

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

* Starting the installation

```
cd dev_ops/Ansible/hyperconverged_project/
 
#Execute in debug mode
ansible-playbook openvstorage_hyperconverged_setup.yml -u root -k -vvvv
 
#Execute in normal mode
ansible-playbook openvstorage_hyperconverged_setup.yml -u root -k
```

## Playbook runtime: (3 controller nodes, 1 compute node on 1Gbit network)
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

## License
The Open vStorage HealthCheck is licensed under the [GNU AFFERO GENERAL PUBLIC LICENSE Version 3](https://www.gnu.org/licenses/agpl.html).