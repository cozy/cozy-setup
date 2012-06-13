from fabric.api import run

def install():
    update()
    install_tools()
    install_nodejs()
    #TODO reboot sinon ca merde
    install_mongodb()

# Maintain Up to Date the system
def update():
    run('sudo apt-get update')
    run('sudo apt-get upgrade')

# Tools install
def install_tools():
    run('sudo apt-get install python openssl libssl-dev pkg-config g++ ')
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

def install_redis():
    run('wget http://redis.googlecode.com/files/redis-2.4.14.tar.gz')
    run('tar xvzf redis-2.4.14.tar.gz')
    run('cd redis-2.4.14 ; make')
    run('sudo cp redis-2.4.14/src/redis-server /usr/local/bin/')
    run('sudo cp redis-2.4.14/src/redis-cli /usr/local/bin/')
    run('sudo mkdir /etc/redis')
    run('sudo mkdir /var/redis ; sudo mkdir /var/redis/6379')
    run('sudo cp redis-2.4.14/utils/redis_init_script /etc/init.d/redis_6379')
    ##todo importer la conf sudo cp 6379.conf /etc/redis/
    #run('sudo update-rc.d redis_6379 defaults')
    run('sudo /etc/init.d/redis_6379 start')
