# Cozy Setup

Cozy Setup contains all stuff needed to install cozy on a fresh debian server.
Validate on a debian squeeze 32 bits

# How To Install

Get a system up to date and install the daemon manager upstart.

> guest$ sudo apt-get update
> guest$ sudo apt-get upgrade
> guest$ sudo apt-get install upstart
> guest$ sudo reboot now

Launch the Fabric script to launch the cozy install

> host$ fab -H user@ip:port install

Be patient some commands could take a few minutes.

You should say 'Y' to the questions asking for memory on your hard disk 

The Postfix configuration could be (N)o configuration. Then Space. It use for cozy password recovery. 


# About Cozy

Cozy allow you to host all your personnal application in a single place you 
control. 
You can manage your data efficiently while protecting your privacy.
You will find more on our website : http://www.mycozycloud.com
