## Prepare your control machine

* To orchestrate the setup we are going to use a Control Machine. The Control Machine is used to send instructions to all hosts in the Open vStorage cluster. Note that the Control Machine should not be part of the cluster so it can later also be used for troubleshooting the Open vStorage cluster.

```
Linux control-machine 3.19.0-56-generic #62~14.04.1-Ubuntu SMP Fri Apr 27 10:03:15 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux

ansible:
  Installed: 2.0.2.0-1ppa~trusty
  Candidate: 2.0.2.0-1ppa~trusty
  Version table:
 *** 2.0.2.0-1ppa~trusty 0
        500 http://ppa.launchpad.net/ansible/ansible/ubuntu/ trusty/main amd64 Packages
        100 /var/lib/dpkg/status
```

* Install Ansible on a pc or server you can use as Control Machine.

```
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
```

* Create `/usr/lib/ansible`, download the Open vStorage module to the Control Machine and put the module in `/usr/lib/ansible`.

```
sudo apt-get install git
cd ~; sudo git clone -b fargo-release3 https://github.com/openvstorage/dev_ops.git
sudo mkdir /usr/lib/ansible; sudo cp ~/dev_ops/Ansible/openvstorage_module_project/openvstorage.py /usr/lib/ansible
```

* Edit the Ansible config file `/etc/ansible/ansible.cfg` describing the library. Uncomment it and change it to `/usr/lib/ansible`.

```
vim /etc/ansible/ansible.cfg

##change
#inventory = /etc/ansible/hosts
#library = /usr/share/my_modules/

##to
inventory = /etc/ansible/hosts
library = /usr/lib/ansible
```