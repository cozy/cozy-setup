# Cozy Setup

Cozy Setup contains all stuff needed to install cozy on a fresh debian server.

# How To Install Cozy Environnement

The installation requires a system up to date with upstart as daemon manager.

You can do it with following commands.

> guest$ sudo apt-get update  
> guest$ sudo apt-get upgrade  
> guest$ sudo apt-get install upstart  
> guest$ sudo reboot now  

Once your system is prepared, then use the Fabric script to launch the cozy 
install:

> host$ fab -H user@ip:port install

Fill what you want when installer will ask you for informations about the
certificate. 

Be patient some commands or app deployements could take a few minutes. It 
depends about your network and your hardware capabilities.

# Test 

Once installation done, you can access to https://IP:80 to create your cozy
main account.

For Vagrant user, uncomment this line in the Vagrantfile and reload the vm.

> config.vm.network :hostonly, "192.168.33.10"

> vagrant reload

You can launch functional test too (see README file located in test directory).

# Issues on 20 june.

The Postfix (mail server) configuration is set to mycozycloud.com . 
Right now Cozy has just mail sending capabilities. So you don't need a perfect
configuration. Mails are only required to notify you what to do when you need
to reset your password.

Redis conf is the default one.


# About Cozy

Cozy is private pesronal cloud solution that allows you to host all your 
personnal application in a single place you control. 
This way, you can manage your data from anywhere while protecting your privacy.

http://www.mycozycloud.com
