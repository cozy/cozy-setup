#!/bin/bash

# This script is intented to be executed when the virtual machine starts.
# The monitor is told to start the data-system, the home and the proxy app.
# This is the last step needed to be able to develop a cozy app with the virtual machine.

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