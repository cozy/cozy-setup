# Cozy Setup

Cozy Setup contains all stuff needed to install cozy on a fresh debian server.

Cozy Cloud aims to be used remotely. We provide here only stuff to deploy
it on a remote server. To make a local installation, we recommend you to start a
virtual machine, then run script with this vm as your remote server.

# How To Install Cozy Environnement

The installation requires a system up to date with upstart as daemon manager.
You can do it by running following commands on your target server:

    sudo apt-get update  
    sudo apt-get upgrade  
    sudo apt-get install upstart  
    sudo reboot now  

On your local machine install Fabric. Fabric is a tool to run scripts on a 
remote server:

    apt-get install python python-pip
    pip install fabric fabtools

Once your system is prepared, then use the Fabric script from your local
machine to launch the cozy installation:

    fab -H user@ip:port install

Fill what you want when installer will ask you for informations about the
certificate. 

Be patient some commands or app deployements could take a few minutes. It 
depends about your network and your hardware capabilities.

# Test 

Once installation done, you can access to https://IP:80 to create your cozy
main account.

You can launch automatic test too (see README file located in test directory).

# About Cozy

Cozy is private pesronal cloud solution that allows you to host all your 
personnal application in a single place you control. 
This way, you can manage your data from anywhere while protecting your privacy.

https://cozycloud.cc
