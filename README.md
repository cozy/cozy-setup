<<<<<<< HEAD
Static website for the community project.
=======
# Cozy Setup

Cozy Cloud aims to be used remotely on your own server.
So this project contains what you need to achieve that goal 
(it works only for debian/ubuntu systems). 

# How to install cozy on your server ?

On your local machine install fabric and fabtools:

    apt-get install python python-pip
    sudo pip install fabric fabtools

Download our Fabric file (a script that will run commands on your remote
server):

    wget https://raw.github.com/mycozycloud/cozy-setup/master/fabfile.py


Once your system is prepared, then use the Fabric script from your local
machine to launch the cozy installation (run it in the same direction where is
located the fabfile you downloaded):

    fab -H user@ip:port install

Fill what you want when installer will ask you for informations. 

Be patient some commands or app deployements could take a lot of time. It 
depends about your network and your hardware capabilities.

*About local installation*

To make a local installation, we recommend you to create a
virtual machine, and then to run the fabfile script with your virtual machine as
target.


*Try Cozy with Vagrant*

If you want to use vagrant to run Cozy Cloud Setup in a virtual machine
we recommend you the Ubuntu 12.04 box. Be careful update will require that
you configure your boot sequence. Chose the first filesystem they will propose
you, then click ok.

http://files.vagrantup.com/precise64.box

## Test 

Once installation done, you can access to https://IP:80 to create your cozy
main account. Be sure that you use the https protocol if you just see the Nginx
welcome page.

## What this script installs on your server ?

The Cozy install script install the following tools :

* Python runtime
* Node.js runtime
* Redis key-value store
* CouchDB document database
* Haibu node.js application manager
* Node tools: cozy-controller, cozy-monitor, coffee-script, compound
* Cozy data indexer
* Cozy data layer 
* Cozy proxy
* Cozy Home (web app)
* Cozy Notes (web app)
* Cozy Todos (web app)


If you want to know more about how works Cozy you can check our [architecture
page](https://github.com/mycozycloud/cozy-setup/wiki/Cozy-architecture).


## About virtual machines and containers

Because of the numerous technologies involved, we recommend you to run Cozy
stack in an isolated virtual machine or in a container (OpenVz or LXC). But
it's not mandatory, you can set up directly Cozy Cloud on your server (that's
what you should do if you have a small server like a Sheeva Plug or an old
machine).


# About Cozy

Cozy is private pesronal cloud solution that allows you to host all your 
personnal application in a single place you control. 
This way, you can manage your data from anywhere while protecting your privacy.

https://cozycloud.cc

# Cozy on IRC
Feel free to check out our IRC channel (#cozycloud at freenode.net) if you have any technical issues/inquiries or simply to speak about Cozy cloud in general.
>>>>>>> 7ec66b396bd1ee6b3dc5a3265e59c01cb6fb5483
