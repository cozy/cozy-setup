# Cozy Setup
test

Cozy Setup contains all stuff needed to install cozy on a fresh debian server.
Validate on a debian squeeze 32


Lancement du script  
Si le port 22 est bien routé sur le port 2200
Possibilité de rerouter sur le port de votre choix manuellement sinon cf shell de pendant le lancement de la VM
> $ fab -H vagrant@localhost:2200 install  

mot de passe : vagrant

Attention une mise à jour Grub est possible. Utiliser les touches tab et espace.



# About Cozy

Cozy allow you to host all your personnal application in a single place you 
control. 
You can manage your data efficiently while protecting your privacy.
You will find more on our website : http://www.mycozycloud.com
