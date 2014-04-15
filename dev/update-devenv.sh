#!/bin/sh

###
# Update script for the devevelopment environment virtual machine from current
# base box.
###

# we avoid the shared folder because of the symlink issue
cd ~

# update node.js to 0.10.26
if [[ $node_version == "v0.10.26" ]]
then
    echo "NODE ALREADY UP TO DATE -- v0.10.26"
else
    wget http://nodejs.org/dist/v0.10.26/node-v0.10.26.tar.gz
    tar -zxf node-v0.10.26.tar.gz
    cd node-v0.10.26/
    ./configure && make && sudo make install
fi

# Update the core apps
sudo cozy-monitor update data-system
sudo cozy-monitor update home
sudo cozy-monitor update proxy

# we stop everything
sudo supervisorctl stop cozy-controller
sudo pkill -9 node
sudo rm /usr/local/cozy/autostart/logreader*

# we start the updates
sudo npm install -g cozy-controller
sudo npm install -g cozy-monitor

sudo supervisorctl start cozy-controller

# Update the indexer
sudo supervisorctl stop cozy-indexer
cd /usr/local/var/cozy-indexer/cozy-data-indexer
sudo git pull origin master
sudo virtualenv virtualenv
. virtualenv/bin/activate
sudo pip install -r requirements/common.txt --upgrade
sudo pip install -r requirements/production.txt --upgrade
sudo supervisorctl start cozy-indexer

