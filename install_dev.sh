# Script that help developers which use Ubuntu to have a complete environment 
# for working on Cozy tools.

# Update system
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python openssl libssl-dev pkg-config
sudo apt-get install g++ make

# install Node JS
wget http://nodejs.org/dist/v0.6.15/node-v0.6.15.tar.gz
tar -xvzf node-v0.6.15.tar.gz 
cd node-v0.6.15
./configure
make
sudo make install
cd ..
rm node-v0.6.15.tar.gz
rm -rf node-v0.6.15

# Install Mongodb
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
sudo echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee --append /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install mongodb-10gen

# install Redis
apt-get install redis-server

# Install postfix
sudo apt-get install postfix

# Install git
sudo apt-get install git

# Install Node tools
sudo npm install -g coffee-script
sudo npm install -g supervisor
sudo npm install -g brunch
