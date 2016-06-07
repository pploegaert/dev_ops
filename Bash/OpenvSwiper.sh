#!/usr/bin/env bash

#Title: Open vSwiper
#Description: removes OpenvStorage & its dependencies 
#Maintainer: Jonas Libbrecht
#Licensed under: AGPLv3
#Warning: Use at own risk
#Version: 3 (compatible with Chicago, Denver, Eugene, Eugene-updates & Unstable (Currently Fargo))

#remove keys/values from etcd so future setups don't have problems
etcdctl rm /ovs -recursive

set -f 

#variables
packages='openvstorage* rabbitmq-server* alba* volumedriver-base* volumedriver-server* gunicorn* memcached* python-memcache* nginx* arakoon* etcd python-etcd'

#removes OVS packages from dpkg
apt-get purge -qq -y --allow-unauthenticated $packages

#removes config files
apt-get remove -qq -y --allow-unauthenticated $packages

#delete orphaned packages and (their) dependecies
apt-get autoremove -qq -y --allow-unauthenticated

set +f

#removes leftovers of OVS
rm -rf /opt/OpenvStorage
rm -rf /opt/alba-asdmanager
rm -rf /opt/asd-manager

#remove remaining avahi records
rm -rf /etc/avahi/services/*

#kill remaining ovs services and log files (fix for 2.4 webapps problem)
# rm -rf /etc/init/ovs-*
# rm -rf /etc/init/alba-*
for f in $(ls /etc/init/ovs-*.conf /etc/init/alba-*.conf /etc/init/asd-*.conf)
do
  rm ${f}
  #mv ${f} ${f}-disabled
done

#remove remaining log files 
rm -rf /var/log/upstart/alba*
rm -rf /var/log/upstart/ovs-*
rm -rf /var/log/ovs
rm -rf /var/log/arakoon

#kill remaining arakoon & alba processes
pkill arakoon
pkill alba
pkill asd
pkill etcd

pkill -9 -f OpenvStorage
pkill -9 failovercache

#remove gunicorn, ovs-webapps.api pid & runtime locks
rm -f /run/ovs_api.pid
rm -rf /run/lock/ovs_*

#removes known_hosts, authorized_hosts and used private/public keys in OVS
#in 4.0 it will remove the needed lines in the files
rm -rf /root/.ssh/*

#remove arakoon on ssd's, due to bug: OVS-3671
rm -rf /mnt/ssd*/arakoon
rm -rf /mnt/ssd*/*

#umount previous ovs mounts/disks
umount -lf /mnt/ssd*
umount -lf /mnt/hdd*
umount -lf /mnt/alba-asd/*

#remove avahi leftovers from alba and ovs
rm /etc/avahi/services/ovs_cluster.service
rm /etc/avahi/services/asdnode.service

# wipe all info from used disks (filesystem + partition)
awk '/^#/ { next } /\/mnt\/alba-asd\// { print $1,$2 }' /etc/fstab | while read p m
do
  umount -lf $m
  wipefs -a $p
  [ -n "${p%-part*}" ] && parted ${p%-part*} rm ${p##*-part}
done

awk '/^#/ { next } /\/mnt\/ssd[0-9]+/ { print $1,$2 }' /etc/fstab | while read p m
do 
  umount -lf $m
  wipefs -a $p
  [ -n "${p%-part*}" ] && parted ${p%-part*} rm ${p##*-part}
done

awk '/^#/ { next } /\/mnt\/hdd[0-9]+/ { print $1,$2 }' /etc/fstab | while read p m
do 
  umount -lf $m
  wipefs -a $p
  [ -n "${p%-part*}" ] && parted ${p%-part*} rm ${p##*-part}
done

awk '/fuse\./ { print $2 }' /proc/mounts | xargs fusermount -u 

#add support for NVMe (delete 10 partitions, this should be enough :D)
for i in {1..10}
do
  parted -s /dev/nvme0n1 rm $i
done

#remove persistent mounts (and keep backup for safety reasons)
cp /etc/fstab /etc/fstab.backup
sed -i -e '/# BEGIN Open vStorage/,/# END Open vStorage/d' \
       -e '/# BEGIN ALBA ASDs/,/# END ALBA ASDs/d' \
       -e '/\/mnt\/ssd[0-9]*/d' \
       -e '/\/mnt\/hdd[0-9]*/d' \
       -e '/\/mnt\/alba-asd\//d' /etc/fstab

#remove mount directories
rmdir /mnt/ssd*
rmdir /mnt/hdd*
rmdir /mnt/alba-asd/* /mnt/alba-asd

#remove ovs (resume)preconfig and apt information
rm -f /tmp/openvstorage_preconfig.cfg
rm -f /tmp/openvstorage_resumeconfig.cfg
rm -f /etc/apt/sources.list.d/ovsaptrepo.list
apt-get update

#remove ovs, alba and other associated logfiles
rm -rf /var/log/upstart/ovs*
rm -rf /var/log/upstart/alba*
rm -rf /var/log/ovs
rm -rf /var/gunicorn
rm -rf /var/rabbitmq
rm -rf /var/nginx
rm -f /var/log/memcached.log

#remove ovs user and group
ps aux | awk '/^ovs/  { print $2 }' | xargs kill -9
deluser --remove-home ovs 
delgroup ovs

#remove rest
rm /etc/openvstorage_id

#reset /etc/hosts file
fqdn=$(hostname -f)
shortname=$(hostname -s)

if [ $shortname = $(cat /etc/hostname) ]; then
    # remove shortname because fqdn = shortname
    shortname=""
fi

cp /etc/hosts /etc/hosts.backup

cat << EOF > /etc/hosts
127.0.0.1   localhost
127.0.1.1   $fqdn $shortname

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

#remove etcd proxies from storage nodes
rm /etc/init/sdm-etcd-config.conf
