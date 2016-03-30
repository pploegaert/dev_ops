#Open vStorage goes Ansible!

##Description
The Open vStorage support team has created an easy way to install your future, high-performance, highly-scalable cloud through Ansible. 

##Manual and more information...
If you click on the respective cluster, you can find a full manual to install it through Ansible

Also try to have the latest Ansible installation, we tested this with:
```
ansible:
  Installed: 2.0.1.0-1ppa~trusty
  Candidate: 2.0.1.0-1ppa~trusty
  Version table:
 *** 2.0.1.0-1ppa~trusty 0
        500 http://ppa.launchpad.net/ansible/ansible/ubuntu/ trusty/main amd64 Packages
        100 /var/lib/dpkg/status
```

##If something goes wrong...

* **Open vSwiper:**
  If something goes wrong you can run the dev_ops Open vStorage wiper to redo the installation. 
  Just go to: `dev_ops/Bash/` and run on the nodes: `bash OpenvSwiper.sh`
  
  If you need a one liner to execute the wiper from your Ansible configuration master:
  ```
  ansible cluster -m shell -a "wget https://raw.githubusercontent.com/openvstorage/dev_ops/master/Bash/OpenvSwiper.sh -O /root/wiper.sh; bash /root/wiper.sh; bash /root/wiper.sh" -u root -k`
  ```

* **Ansible** `host_key_checking`: 
  If you get host key checking errors when you start the script, change this in `/etc/ansible/ansible.cfg`:
  ```
  # uncomment this to disable SSH key host checking
  host_key_checking = False
  ```

##Compatibility
* Open vStorage HyperScale (Enterprise Level Cloud)
* Open vStorage HyperConverged (Small - Medium level Cloud)
