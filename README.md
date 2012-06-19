# Cozy Setup

Cozy Setup contains all stuff needed to install cozy on a fresh debian server.
Validate on a debian squeeze 32 bits

# How To Install Cozy Environnement

Get a system up to date and install the daemon manager upstart.  

You should use this kind of command

> guest$ sudo apt-get update  
> guest$ sudo apt-get upgrade  
> guest$ sudo apt-get install upstart  
> guest$ sudo reboot now  

Launch the Fabric script to launch the cozy install

> host$ fab -H user@ip:port install

You should answer about wired questions to construct your SSL certificat. Don't care about that.

Be patient some commands or app deployements could take few minutes. It depends about your network and your hardware capabilities.



# Issues on 20 june.

The Postfix (mail server) configuration is set to BidonCozy.com . It use for cozy password recovery. 

The data initialisation crash. (Must work on it)

Redis is set to default conf.




# About Cozy

Cozy allow you to host all your personnal application in a single place you 
control. 
You can manage your data efficiently while protecting your privacy.
You will find more on our website : http://www.mycozycloud.com
