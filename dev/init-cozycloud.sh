#!/bin/bash

# This script is intented to be executed when the virtual machine starts.
# The monitor is told to start the data-system, the home and the proxy app.
# This is the last step needed to be able to develop a cozy app with the virtual machine.



#####
#
# Temporary section. This allows us to quickfix the bug that deletes redis folder
# each time the VM is stopped.
#
#####

redis_folder="/var/run/redis"
sudo mkdir -p $redis_folder
sudo chown redis:redis $redis_folder
sudo supervisorctl restart redis_cozy



#####
#
# Starts needed Cozy Applications
#
#####

coffee="/usr/local/bin/coffee"
target="/home/cozy/cozy-setup/monitor.coffee"

appsToStart=('data-system' 'home' 'proxy')


echo "STARTING MAIN APPS"
for app in ${appsToStart[@]}
do
    $coffee $target start $app
done

echo "CURRENT COZY STATUS"
$coffee $target status