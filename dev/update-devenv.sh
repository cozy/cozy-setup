#!/bin/sh

###
# Update script for the devevelopment environment virtual machine from current
# base box.
###

# we avoid the shared folder because of the symlink issue
cd ~

# we stop everything
sudo supervisorctl stop cozy-controller
sudo pkill -9 node
sudo rm /usr/local/cozy/autostart/logreader*

# we rewrite the cozy-controller configuration
# this is actually a quick fix of the base box and should be fixed properly one day
echo '[program:cozy-controller]
autorestart=true
command=cozy-controller -c -u --per 755
environment=NODE_ENV="development"
redirect_stderr=true
user=root' > /etc/supervisor/conf.d/cozy-controller.conf

sudo supervisorctl reload

# we start the updates
sudo npm install -g cozy-controller
sudo npm install -g cozy-monitor

sudo supervisorctl start cozy-controller

cozy-monitor install data-system
cozy-monitor install home
cozy-monitor install proxy


