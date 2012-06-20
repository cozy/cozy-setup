from fabric.api import run
from fabtools import *
import fabtools
"""
Script to set up a cozy cloud environnement from a fresh system
V0.0.1  14/06/12
Validate on a Debian squeeze 32 bits up to date and with upstart installed.

Update your system and
Launch $ fab -H user@Ip.Ip.Ip.Ip:Port install

"""

def install():
    install_tools()
    install_nodejs()
    install_mongodb()
    install_redis()
    #pre_install()
    #create_certif()
    #install_cozy()
    #init_data()

"""
Tools install
"""
def install_tools():
    require.deb.packages([
            'python',
            'openssl',
            'libssl-dev',
            'pkg-config',
            'g++',
            'git'
    ])
 
"""
Installing Node 0.6.18
"""
def install_nodejs():
    run('wget http://nodejs.org/dist/v0.6.18/node-v0.6.18.tar.gz')
    run('tar -xvzf node-v0.6.18.tar.gz')
    run('cd node-v0.6.18 ; ./configure ; make ; sudo make install')
    run('rm node-v0.6.18.tar.gz ; rm -rf node-v0.6.18')

"""
Installing Mongodb
"""
def install_mongodb():
    run('sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    run(' sudo echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee --append  /etc/apt/sources.list')
    run('sudo apt-get update')
    run('sudo apt-get install mongodb-10gen')

"""
Installing and Auto-starting Redis 2.4.14
"""
def install_redis():
    require.redis.installed_from_source('2.4.14')
    require.redis.instance('Server_redis','2.4.14',)

"""
Preparing Cozy
"""
def pre_install():
    run('sudo mkdir -p /home/cozy/')
    user.create('cozy', '/home/cozy/','/bin/sh')
    run('sudo chown cozy:cozy /home/cozy/')
    run('sudo -u cozy git clone git://github.com/LucsT/cozy-setup.git /home/cozy/cozy-setup')
    require.postfix.server('BidonCozy.com')
    run('sudo npm install -g coffee-script')
    run('sudo npm install -g haibu@0.8.2')
    run('sudo cp /home/cozy/cozy-setup/paas.conf /etc/init/')
    run('sudo service paas start')

"""
Creating SSL certificats
"""
def create_certif():
    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ./server.crt')
    run('sudo chmod 640 server.key')
    run('sudo cp server.key /home/cozy/server.key')
    run('sudo cp server.crt /home/cozy/server.crt')
    run('sudo chown root:ssl-cert /home/cozy/server.key')
    run('sudo rm server.key; sudo rm server.crt')

"""
Deploying cozy proxy, cozy home, cozy note on port 80, 8001, 3000
"""
def install_cozy():
    run('cd /home/cozy/cozy-setup ; sudo npm install eyes haibu@0.8.2')
    run('cd /home/cozy/cozy-setup/ ; coffee home.coffee')
    run('cd /home/cozy/cozy-setup/ ; coffee notes.coffee')
    run('cd /home/cozy/cozy-setup/ ; coffee proxy.coffee')

"""
Data initialisation
"""
def init_data():
    #run('cd /usr/local/lib/node_modules/haibu/local/cozy/home/cozy-home ; coffee init.coffee')
    run('sudo -u cozy cp /home/cozy/cozy-setup/node_mailer.js /home/cozy/cozy-setup/node_modules/mailer/lib/')

"""
Updating applications
"""
def update():
    run('cd /home/cozy/cozy-setup/ ; sudo -u cozy git pull')
    run('cd /home/cozy/cozy-setup/ ; coffee home.coffee')
    run('cd /home/cozy/cozy-setup/ ; coffee notes.coffee')
    run('cd /home/cozy/cozy-setup/ ; coffee proxy.coffee')
