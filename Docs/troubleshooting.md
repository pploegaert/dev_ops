## If something goes wrong...

* **Open vSwiper:**
  If something goes wrong you can run the dev_ops Open vStorage wiper to redo the installation.
  Just go to : [dev_ops/Bash/](https://github.com/openvstorage/dev_ops) and run on the nodes: `bash OpenvSwiper.sh`

  **WARNING:** This script wipes all the disks / partitions that are not in use by the operating system. Also it wipes the content of `/root/.ssh/`.

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

## Performance issue's
If the installation is on a large scale, you will probably experience a slow installation.
This is because Ansible only performs 5 parallel connections by default.
If you want to install packages faster, you can uncomment & edit the `forks` parameter in `/etc/ansible/ansible.cfg`:

* By default:

```
#forks          = 5
```

* Change to:

```
forks          = 200
```

If you want to know how long the installation last, you can enable the Ansible `profile_tasks` in `/etc/ansible/ansible.cfg`:

```
callback_whitelist = profile_tasks
```

## For more information:

### Full overview
For a full overview of the separate repo to install Open vStorage through Ansible, click [here](https://github.com/openvstorage/dev_ops/tree/fargo-release3).

### Older versions:
* For a full overview of the seperate releases, click [here](https://github.com/openvstorage/dev_ops/releases).
* To install a `eugene-updates` just follow the instructions on the `release02` branch, click [here](https://github.com/openvstorage/dev_ops/tree/release2.0).
