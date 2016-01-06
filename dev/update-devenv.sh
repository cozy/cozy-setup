#!/bin/sh

###
# Update script for the devevelopment environment virtual machine from current
# base box.
###

# we avoid the shared folder because of the symlink issue
cd ~

# Update the core apps
sudo cozy-monitor update data-system
sudo cozy-monitor update home
sudo cozy-monitor update proxy

# we stop everything
sudo supervisorctl stop cozy-controller
sudo pkill -9 node

# we start the updates
sudo npm install -g cozy-controller
sudo npm install -g cozy-monitor

sudo supervisorctl start cozy-controller

