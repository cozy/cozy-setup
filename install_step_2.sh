
# Install Mongodb
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
sudo echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee --append /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install mongodb-10gen

# Install redis
sudo apt-get install redis-server

# Install postfix
sudo apt-get install postfix

# Install git
sudo apt-get install git

# Install Haibu
sudo npm install -g coffee-script
sudo npm install -g haibu

echo """
start on startup
stop on shutdown
respawn
respawn limit 10 5

script
    NODE_ENV="production" haibu --coffee
end script
"""  | sudo tee --append /etc/init/paas.conf
sudo service paas start

# setup certs

sudo mkdir /home/cozy/
cd /home/cozy/
sudo openssl genrsa -out ./server.key 1024
sudo openssl req -new -x509 -days 3650 -key ./server.key -out ./server.crt
sudo chmod 640 server.key
sudo chown root:ssl-cert server.key


# install home

sudo git clone https://github.com/mycozycloud/cozy-setup.git
cd cozy-setup
sudo npm install eyes
sudo npm install haibu
sudo coffee home.coffee
sudo coffee notes.coffee
sudo coffee proxy.coffee



