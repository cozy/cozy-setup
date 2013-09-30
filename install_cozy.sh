#!/bin/sh

sudo apt-get install python python-pip python-dev
sudo pip install fabric==1.6.0 fabtools==0.14.0
wget https://raw.github.com/mycozycloud/cozy-setup/master/fabfile.py
fab -H $HOST install
