#!/bin/sh

apt-get install python python-pip
sudo pip install fabric==1.6.0 fabtools==0.13.0
wget https://raw.github.com/mycozycloud/cozy-setup/master/fabfile.py
fab -H $HOST uninstall
