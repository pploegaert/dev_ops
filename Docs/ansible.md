# Ansible
At Open vStorage we build large Open vStorage clusters for customers. To prevent errors and cut-down the deployment time we don’t set up these clusters manually but we automate the deployment through Ansible, a free software platform for configuring and managing IT environments.

Before we dive into the Ansible code, let’s first have a look at the architecture of these large clusters.

There are 5 types of nodes: controllers, compute, storage, performance and capacity nodes.
* Controller nodes: 3 dedicated, hardware optimized nodes to run the master services and hold the distributed DBs. There is no vPool configured on these nodes so no VMs are running on them. These nodes can be equipped with a couple of large capacity SATA drives for scrubbing.
* Compute nodes: These nodes run the Virtual Machines or applications.
* Storage nodes: This type of server comes in 2 flavours:
    * Performance node: These server are configured with a vPool and have SSDs or PCie flash cards for performance.
    * Capacity node: These servers are equipped with a lot of SATA drives but have less RAM and CPU.


There are 3 different deployment scenario's:
* [Hyper-converged](hyperconverged.md): Compute and Storage are configured on the same server.
* [HyperScale](hyperscale.md): The compute and performance functionality run on the same server. Capacity nodes are on separate servers.
* [GeoScale](geoscale.md): The compute, performance and capacity functionality is configured on separate servers.

 Automating Open vStorage can of course also be achieved in a similar fashion with other tools like [Puppet](https://puppetlabs.com/) or [Chef](https://www.chef.io/chef/).