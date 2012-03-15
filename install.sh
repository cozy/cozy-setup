
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
coffe home.coffee

## oldies

sudo apt-get install git
git clone https://gelnior@bitbucket.org/gelnior/cozy-home.git
cd cozy-home
npm install
sudo npm install -g coffee-script
echo """
start on startup
stop on shutdown
respawn
respawn limit 10 5

env PORT=3000
env NODE_ENV="production"

script
    export PORT
    export NODE_ENV

    cd /home/vagrant/cozy-home
    NODE_ENV=production coffee server.coffee
end script
"""  | sudo tee --append /etc/init/cozy-home.conf
sudo service cozy-home start


# Install Proxy
echo """
start on startup
stop on shutdown
respawn
respawn limit 10 5

script
    cd /home/vagrant/cozy-home
    coffee router.coffee
end script
"""  | sudo tee --append /etc/init/cozy-router.conf
sudo service cozy-router start


# Install Noty Plus
sudo npm install -g railway
mkdir apps
cd apps
npm install -l
railway init noty-plus --coffee && cd noty-plus
railway g scaffold note title content createdAt:date --coffee
echo """
start on startup
stop on shutdown
respawn
respawn limit 10 5

env PORT=8000
env NODE_ENV="production"

script
    export PORT
    export NODE_ENV

    cd /home/vagrant/apps/noty-plus
    PORT=8000 NODE_ENV=production coffee server.coffee
end script
"""  | sudo tee --append /etc/init/noty-plus.conf
sudo service noty-plus start



