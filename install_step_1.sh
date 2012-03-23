
# prepare vm
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python openssl libssl-dev pkg-config

# Install node js
apt-get install g++ make
wget http://nodejs.org/dist/v0.6.12/node-v0.6.12.tar.gz
tar -xvzf node-v0.6.12.tar.gz 
cd node-v0.6.12
./configure
make
sudo make install
cd ..
rm node-v0.6.12.tar.gz
rm -rf node-v0.6.12

# Install Upstart 
sudo apt-get install upstart
sudo reboot 
