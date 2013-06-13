# Cozy Setup

Cozy Cloud is designed to be used remotely on your own server.
So, this project contains what you need to achieve that goal 
(it only works for Debian/Ubuntu systems). 

# How to install Cozy on your server?

On your local machine install Fabric and fabtools:

    apt-get install python python-pip python-dev software-properties-common
    sudo pip install fabric fabtools

Download our Fabric file (a script that will run commands on your remote
server):

    wget https://raw.github.com/mycozycloud/cozy-setup/master/fabfile.py


Once your system is prepared, use the Fabric script from your local
machine to launch the Cozy installation (run it in the same directory as the fabfile
you downloaded before):

    fab -H user@ip:port install

Enter your settings (such as domain name) when prompted by the installer.

Be patient; some commands or app deployments can take some time. It 
depends on your network and hardware capabilities.

*About local installation*

To install Cozy locally, we recommend you to create a virtual machine, 
and then to run the fabfile script with your virtual machine as target.
This allows you to experiment with Cozy without installing numerous packages
into your environment.

*Try Cozy with Vagrant*

If you want to use Vagrant to run Cozy Cloud Setup in a virtual machine
we recommend you use the Ubuntu 12.04 box. Be careful as the update will require that
you configure your boot sequence. Choose the first filesystem that is offered, then click ok.

http://files.vagrantup.com/precise64.box

*Assistance*

You can either read ou [Trouble
Shootings](https://github.com/mycozycloud/cozy-setup/wiki/Trouble-shootings) section or contact us via email
contact@cozycloud.cc or join our IRC channel and ask for assistance #cozycloud
on freenode.net.

## Test 

Once the installation is done, you can access https://IP:80 to create your Cozy
main account. Be sure that you used the HTTPS protocol if you just see the nginx
welcome page.

## What will this script install on your server?

The Cozy install script installs the following tools:

* Python runtime
* Node.js runtime
* CouchDB document database
* Node tools: cozy-controller, cozy-monitor, coffee-script, compound, brunch
* Cozy Controller Daemon
* Cozy data indexer
* Cozy data layer 
* Cozy proxy
* Cozy Home (web app)


If you want to know more about how Cozy works you can check our [architecture
page](https://github.com/mycozycloud/cozy-setup/wiki/Cozy-architecture).


## About virtual machines and containers

Because of the numerous technologies involved, we recommend you to run the Cozy
stack in an isolated virtual machine or in a container (OpenVz or LXC). But
it's not mandatory, you can install Cozy Cloud on your server (that's
what you should do if you have a small server like a Sheeva Plug or an old
machine).


# About Cozy

Cozy is a private personal cloud solution that allows you to host all your 
personal applications in a single place that you control.
This way, you can manage your data from anywhere while protecting your privacy.

https://cozycloud.cc

# Cozy on IRC
Feel free to check out our IRC channel (#cozycloud at freenode.net) if you have
any technical issues/inquiries or simply to speak about Cozy Cloud in general.
