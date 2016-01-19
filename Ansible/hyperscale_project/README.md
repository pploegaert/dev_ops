# Open vStorage - Hyperscale Setup through Ansible

##Description
Installs a Open vStorage HyperScale cluster through Ansible

##Requirements
* 1 Configuration master: 1 Linux VM with Ansible 2.0 or higher installed
* At least 3 OVS controllers: These will act as the cluster-masters, they manage the databases of the cluster. (If you go for more than 3, pick an uneven amount to avoid split-brain)
* At least 1 OVS compute node: These will act as compute power for your customer VM's
* At least 1 OVS storage node: These will act as storage power for your customer VM's
