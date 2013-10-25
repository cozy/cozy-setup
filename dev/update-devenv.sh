#!/bin/sh

###
# Update script for the devevelopment environment virtual machine from current
# base box.
###

# we avoid the shared folder because of the symlink issue
cd ~

# Update the core apps
sudo cozy-monitor light-update data-system
sudo cozy-monitor light-update home
sudo cozy-monitor light-update proxy

# we stop everything
sudo supervisorctl stop cozy-controller
sudo pkill -9 node
sudo rm /usr/local/cozy/autostart/logreader*

# we rewrite the cozy-controller configuration
# this is actually a quick fix of the base box and should be fixed properly one day
echo '[program:cozy-controller]
autorestart=true
command=cozy-controller -u --per 755
environment=NODE_ENV="development"
redirect_stderr=true
user=root' > /etc/supervisor/conf.d/cozy-controller.conf

sudo supervisorctl reload

# we start the updates
sudo npm install -g cozy-controller
sudo npm install -g cozy-monitor

sudo supervisorctl start cozy-controller

# Update the indexer
sudo supervisorctl stop cozy-indexer
cd /usr/local/var/cozy-indexer/cozy-data-indexer
git pull origin master
virtualenv virtualenv
. virtualenv/bin/activate
sudo pip install -r requirements/common.txt
sudo pip install -r requirements/production.txt
sudo supervisorctl start cozy-indexer



