# Latency simulator deployment

##Description
The Open vStorage support team has created an easy way to deploy latency between nodes to simulate a WAN environment between 2 - 3 datacenters.

##Manual and more information...
Click [here](MANUAL.md) for the how to install.

Also try to have the latest Ansible installation, we tested this with:
```
  Installed: 2.0.2.0-1ppa~trusty
  Candidate: 2.0.2.0-1ppa~trusty
  Version table:
 *** 2.0.2.0-1ppa~trusty 0
        500 http://ppa.launchpad.net/ansible/ansible/ubuntu/ trusty/main amd64 Packages
        100 /var/lib/dpkg/status
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
