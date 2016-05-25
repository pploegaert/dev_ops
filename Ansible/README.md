#Open vStorage goes Ansible!

##Description
The Open vStorage support team has created an easy way to install your future, high-performance, highly-scalable cloud through Ansible. 

##Manual and more information...
If you click on the respective cluster, you can find a full manual to install it through Ansible

Also try to have the latest Ansible installation, we tested this with:
```
ansible:
  Installed: 2.0.2.0-1ppa~trusty
  Candidate: 2.0.2.0-1ppa~trusty
  Version table:
 *** 2.0.2.0-1ppa~trusty 0
        500 http://ppa.launchpad.net/ansible/ansible/ubuntu/ trusty/main amd64 Packages
        100 /var/lib/dpkg/status
```

##If something goes wrong...

* **Open vSwiper:**
  If something goes wrong you can run the dev_ops Open vStorage wiper to redo the installation. 
  Just go to: `dev_ops/Bash/` and run on the nodes: `bash OpenvSwiper.sh`
  
  If you need a one liner to execute the wiper from your Ansible configuration master:
  ```
  ansible cluster -m shell -a "wget https://raw.githubusercontent.com/openvstorage/dev_ops/fargo-release3/Bash/OpenvSwiper.sh -O /root/wiper.sh; bash /root/wiper.sh; bash /root/wiper.sh" -u root -k`
  ```

* **Ansible** `host_key_checking`: 
  If you get host key checking errors when you start the script, change this in `/etc/ansible/ansible.cfg`:
  ```
  # uncomment this to disable SSH key host checking
  host_key_checking = False
  ```
  
##Performance issue's
If the installation is on a large scale, you will probably experience a slow installation.
This is because Ansible only performance 5 parallel connections by default.
If you want to install packages faster you can uncomment & edit the `forks` parameter in `/etc/ansible/ansible.cfg`:

* By default: 
```
#forks          = 5
```

* Change to: 
```
forks          = 200
```

## How fast is the playbook?
If you want to know how long the installation last, you can enable the Ansible `profile_tasks` in `/etc/ansible/ansible.cfg`:
``` 
callback_whitelist = profile_tasks 
```

##Compatibility
* Open vStorage HyperScale / GeoScale (Enterprise Level Cloud)
* Open vStorage HyperConverged (Small - Medium level Cloud)

## License
The Open vStorage HealthCheck is licensed under the [GNU AFFERO GENERAL PUBLIC LICENSE Version 3](https://www.gnu.org/licenses/agpl.html).
