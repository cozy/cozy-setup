
# prepare vm
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python openssl libssl-dev pkg-config

# Install node js
apt-get install g++ make
wget http://nodejs.org/dist/v0.6.15/node-v0.6.15.tar.gz
tar -xvzf node-v0.6.15.tar.gz 
cd node-v0.6.15
./configure
make
sudo make install
cd ..
rm node-v0.6.15.tar.gz
rm -rf node-v0.6.15

# Install Upstart 
sudo apt-get install upstart
sudo reboot 
