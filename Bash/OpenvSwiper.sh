#!/bin/bash

#Title: Open vSwiper
#Description: removes OpenvStorage & its dependencies 
#Maintainer: Jonas Libbrecht
#E-mail: jonas.libbrecht@openvstorage.com
#Version: 2.5 (compatible with Chicago, Denver, Eugene, Eugene-updates & Unstable (Currently Fargo))

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

#remove remaining avahi records
rm -rf /etc/avahi/services/*

#kill remaining ovs services and log files (fix for 2.4 webapps problem)
# rm -rf /etc/init/ovs-*
# rm -rf /etc/init/alba-*
for f in $(ls /etc/init/ovs-*.conf /etc/init/alba-*.conf)
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

#removes known_hosts, authorized_hosts and used private/public keys in OVS
#in 3.0 it will remove the needed lines in the files
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

#remove ovs preconfig
rm -f /tmp/openvstorage_preconfig.cfg

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
