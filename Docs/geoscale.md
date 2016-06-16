# GeoScale

## Architecture
* The Ansible script will deploy a cluster with 4 types of nodes: controllers, compute, performance and capacity nodes.
    * **Controllers:** Dedicated nodes to run the master services and hold the distributed DBs.
    * **Compute nodes:** These nodes run the VMs.
    * **Performance nodes:** These nodes run the extra services, are configured with vPools and are equipped with SSDs for performance.
    * **Capacity nodes:** The capacity servers for the backend storage.

{% include "controlmachine.md" %}

TODO

{% include "troubleshooting.md" %}
