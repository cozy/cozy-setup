from fabric.api import run

def install():
    update()
    install_tools()
    #restart...??
    install_nodejs()
    install_mongodb()

# Maintain Up to Date the system
def update():
    run('sudo apt-get update')
    run('sudo apt-get upgrade')

# Tools install
def install_tools():
    run('sudo apt-get install python openssl libssl-dev pkg-config g++ git')
    run('sudo apt-get install upstart')

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
    run('sudo cp /vagrant/6379.conf /etc/redis/')
    #todo importer la conf sudo cp cozy-setup/6379.conf /etc/redis/
    run('sudo update-rc.d redis_6379 defaults')
    run('sudo /etc/init.d/redis_6379 start')

# Preparing Cozy
def install_preinstall():
    run('sudo apt-get install postfix')
    run('sudo npm install -g coffee-script')
    run('sudo npm install -g haibu')
    #TODO vagrant a modofier par le repo
    run('sudo cp /vagrant/paas.conf /etc/init/')
    run('sudo service paas start')

    # setup certs
    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ./server.crt')
    run('sudo chmod 640 server.key')
    run('sudo chown root:ssl-cert server.key')

def install_cozy():
    run('sudo git clone https://github.com/mycozycloud/cozy-setup.git')
    run('cd cozy-setup ; sudo npm install eyes haibu@0.8.2')
    run('sudo mkdir /usr/local/lib/node_modules/haibu/local/')
    run('sudo coffee home.coffee')
    run('sudo coffee notes.coffee')
    run('sudo coffee proxy.coffee')
