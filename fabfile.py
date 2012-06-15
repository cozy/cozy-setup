from fabric.api import run
"""
Script to set up a cozy cloud environnement from a fresh system
V0.0.1  14/06/12
Validate on a Debian squeeze 32 bits up to date and with upstart installed.
"""

def install():
    #update()
    install_tools()
    install_nodejs()
    install_mongodb()
    install_redis()
    install_preinstall()
    install_certif()
    install_cozy
   
# Maintain Up to Date the system
def update():
    run('sudo apt-get update')
    run('sudo apt-get upgrade')
    run('sudo apt-get install upstart')

# Tools install
def install_tools():
    run('sudo apt-get install python openssl libssl-dev pkg-config g++ git')
    run('git clone https://github.com/mycozycloud/cozy-setup.git')

# Installing Node 0.18
def install_nodejs():
    run('wget http://nodejs.org/dist/v0.6.18/node-v0.6.18.tar.gz')
    run('tar -xvzf node-v0.6.18.tar.gz')
    run('cd node-v0.6.18 ; ./configure ; make ; sudo make install')
    run('rm node-v0.6.18.tar.gz ; rm -rf node-v0.6.18')

# Installing Mongodb
def install_mongodb():
    run('sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    run('sudo echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee --append  /etc/apt/sources.list')
    run('sudo apt-get update')
    run('sudo apt-get install mongodb-10gen')

# Installing and Auto-starting Redis
def install_redis():
    run('wget http://redis.googlecode.com/files/redis-2.4.14.tar.gz')
    run('tar xvzf redis-2.4.14.tar.gz')
    run('cd redis-2.4.14 ; make')
    run('sudo cp redis-2.4.14/src/redis-server /usr/local/bin/')
    run('sudo cp redis-2.4.14/src/redis-cli /usr/local/bin/')
    run('sudo mkdir /etc/redis')
    run('sudo mkdir /var/redis ; sudo mkdir /var/redis/6379')
    run('sudo cp redis-2.4.14/utils/redis_init_script /etc/init.d/redis_6379')
    run('sudo cp cozy-setup/6379.conf /etc/redis/')
    run('sudo update-rc.d redis_6379 defaults')
    run('sudo /etc/init.d/redis_6379 start')
    run('rm redis-2.4.14.tar.gz')
    run('rm -rf redis-2.4.14/')


# Preparing Cozy
def install_preinstall():
    run('sudo apt-get install postfix')
    run('sudo npm install -g coffee-script')
    run('sudo npm install -g haibu')
    run('sudo cp cozy-setup/paas.conf /etc/init/')
    run('sudo service paas start')

# Creating SSL certificats
def install_certif():
    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ./server.crt')
    run('sudo chmod 640 server.key')
    run('sudo chown root:ssl-cert server.key')

# Deploying cozy proxy, cozy home, cozy note on port 80, 8001, 3000
def install_cozy():
    run('cd cozy-setup ; sudo npm install eyes haibu@0.8.2')
    #TODO verif si sudo obligatoire
    run('cd cozy-setup/ ; sudo coffee home.coffee')
    run('cd cozy-setup/ ; sudo coffee notes.coffee')
    run('cd cozy-setup/ ; sudo coffee proxy.coffee')
