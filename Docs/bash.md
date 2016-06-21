# Bash

## OpenvSwiper.sh
The OpenvSwiper is a bash script which removes OpenvStorage & its dependencies from a server. Use this script before you re-install Open vStorage on the node.

**Execute as:** `rm /root/wiper.sh; wget https://raw.githubusercontent.com/openvstorage/dev_ops/master/Bash/OpenvSwiper.sh -O /root/wiper.sh; bash /root/wiper.sh; bash /root/wiper.sh`

**WARNING:** This script wipes all the disks / partitions that are not in use by the operating system. It wipes the content of `/root/.ssh/`.

## Lsi.sh
The LSI script is a collection of scripts to setup or inspect a RAID controller.

**Dependancies:** MegaRAID64
