# Open vStorage - Hyperconverged Setup through Ansible

##Description
Installs a Open vStorage HyperConverged cluster through Ansible

##Requirements (Full Hyperconverged)
* 1 Configuration master: 1 Linux VM with Ansible 2.0 or higher installed
* At least 1 OVS controllers: These will act as the cluster-masters and will run your customer their VM's. They also manage the databases of the cluster. (If you go for more than 1, pick an uneven amount to avoid split-brain)
* Zero to unlimited hyperconverged compute nodes. They will only manage your customer their VM's

##Requirements (Semi Hyperconverged)
* 1 Configuration master: 1 Linux VM with Ansible 2.0 or higher installed
* At least 3 OVS controllers: These will act as cluster-masters only. They manage the databases of the cluster
* At least 1 OVS compute node: These will act as the compute power and storage power for your cloud.
