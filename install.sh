
# prepare vm
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python openssl libssl-dev pkg-config

# Install node js
wget http://nodejs.org/dist/v0.6.12/node-v0.6.12.tar.gz
tar -xvzf node-v0.6.12.tar.gz 
cd node-v0.6.12
./configure
make
sudo make install
cd ..
rm node-v0.6.12.tar.gz
rm -rf node-v0.6.12

# Install Mongodb
sudo apt-get install upstart
sudo reboot 
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee --append /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install mongodb-10gen

# Install Haibu
npm install -g coffee
npm install -g haibu

echo """
start on startup
stop on shutdown
respawn
respawn limit 10 5

script
    NODE_ENV="production" haibu --coffee
end script
"""  | sudo tee --append /etc/init/paas.conf
sudo service pass start

# install home

git clone https://bitbucket.org/gelnior/cozy-setup.git
cd cozy-setup
npm install eyes
npm install haibu
coffee home.coffee
coffee notes.coffee
coffee proxy.coffee


