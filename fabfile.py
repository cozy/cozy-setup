from fabric.api import run, sudo, cd
from fabtools import *

"""
Script to set up a cozy cloud environnement from a fresh system
V0.0.1  14/06/12
Validated on a Debian squeeze 32 bits up to date, with upstart installed.

Once your system is updated, launch $ fab -H user@Ip.Ip.Ip.Ip:Port install
to install the full Cozy stack.

"""

def install():
    install_tools()
    install_nodejs()
    install_mongodb()
    install_redis()
    pre_install()
    create_certif()
    install_cozy()
    init_data()

def install_tools():
    """
    Tools install
    """

    require.deb.packages([
        'python',
        'openssl',
        'libssl-dev',
        'pkg-config',
        'g++',
        'git'
    ])

def install_nodejs():
 
    """
    Installing Node 0.6.18
    """

    run('wget http://nodejs.org/dist/v0.6.18/node-v0.6.18.tar.gz')
    run('tar -xvzf node-v0.6.18.tar.gz')
    run('cd node-v0.6.18 ; ./configure ; make ; sudo make install')
    run('rm node-v0.6.18.tar.gz ; rm -rf node-v0.6.18')

def install_mongodb():
    """
    Installing Mongodb
    """

    run('sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    run('sudo echo "deb http://downloads-distro.mongodb.org/' + \
         'repo/ubuntu-upstart dist 10gen" | sudo tee --append  ' + \
         '/etc/apt/sources.list')
    run('sudo apt-get update')
    run('sudo apt-get install mongodb')

def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14
    """

    require.redis.installed_from_source('2.4.14')
    require.redis.instance('Server_redis','2.4.14',)

def pre_install():
    """
    Preparing Cozy
    """

    run('sudo mkdir -p /home/cozy/')
    user.create('cozy', '/home/cozy/','/bin/sh')
    run('sudo chown cozy:cozy /home/cozy/')
    run('sudo -u cozy git clone git://github.com/mycozycloud/cozy-setup.git' \
        + ' /home/cozy/cozy-setup')
    require.postfix.server('mycozycloud.com')
    run('sudo npm install -g coffee-script')
    run('sudo npm install -g haibu@0.8.2')
    run('sudo cp /home/cozy/cozy-setup/paas.conf /etc/init/')
    run('sudo service paas start')

def create_certif():
    """
    Creating SSL certificats
    """

    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ' + \
        './server.crt')
    run('sudo chmod 640 server.key')
    run('sudo mv server.key /home/cozy/server.key')
    run('sudo mv server.crt /home/cozy/server.crt')
    run('sudo chown cozy:ssl-cert /home/cozy/server.key')

def install_cozy():
    """
    Deploying cozy proxy, cozy home, cozy note on port 80, 8001, 3000
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('npm install eyes haibu@0.8.2', user="cozy")
        run('coffee home.coffee')
        run('coffee notes.coffee')
        run('coffee proxy.coffee')

def init_data():
    """
    Data initialisation
    """

    with cd('/usr/local/lib/node_modules/haibu/local/cozy/home/cozy-home'):
        run('coffee init.coffee')

def update():
    """
    Updating applications
    """

    with cd('/home/cozy/cozy-setup/'):
        sudo('git pull', user='cozy')
        run('coffee home.coffee')
        run('coffee notes.coffee')
        run('coffee proxy.coffee')

def reset_account():
    """
    Delete current accountc 
    """

    with cd('/usr/local/lib/node_modules/haibu/local/cozy/home/cozy-home'):
        run('coffee clean.coffee')
        run('coffee init.coffee')
