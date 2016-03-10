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
git clone https://github.com/openvstorage/dev_ops.git
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
# This is the default ansible 'hosts' file. (edit these variables to your needs)
#
 
#cluster overview
 
[controllers]
ctl01 ansible_host=10.100.69.171 hypervisor_name=mas01
ctl02 ansible_host=10.100.69.172 hypervisor_name=mas02
ctl03 ansible_host=10.100.69.173 hypervisor_name=mas03
 
[computenodes]
cmp01 ansible_host=10.100.69.181 hypervisor_name=hyp01
 
#cluster details
 
[cluster:children]
controllers
computenodes
 
[cluster:vars]
cluster_name=testcluster100
cluster_user=root
cluster_password=rooter
cluster_type=KVM
install_master_ip=10.100.69.171
```

* Starting the installation
```
cd dev_ops/Ansible/hyperconverged_project/
 
#Execute in debug mode
ansible-playbook openvstorage_hyperconverged_setup.yml -u root -k -vvvv
 
#Execute in normal mode
ansible-playbook openvstorage_hyperconverged_setup.yml -u root -k
```
