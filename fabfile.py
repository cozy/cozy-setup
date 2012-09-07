from fabric.api import run, sudo, cd
from fabtools import deb,require,user
from fabtools.openvz import guest

"""
Script to set up a cozy cloud environnement from a fresh system
V0.0.1  14/06/12
Validated on a Debian squeeze 64 bits up to date.

Once your system is updated, launch 
$ fab -H user@Ip.Ip.Ip.Ip:Port install
to install the full Cozy stack.

"""

def install():
    install_tools()
    install_nodejs()
    install_mongodb()
    install_redis()
    pre_install()
    #create_certif()
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
        'git',
        'sudo',
        'make'
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

    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    require.deb.source("mongo", "http://downloads-distro.mongodb.org" + \
                           "/repo/ubuntu-upstart", "dist 10gen")
    deb.update_index()
    require.deb.packages(['mongodb'])
    
def install_couchdb():
    """
    Installing Couchdb
    """
    require.deb.packages(['build-essential'])
    require.deb.packages(['erlang', 'libicu-dev', 'libmozjs-dev',
       'libcurl4-openssl-dev'])

    with cd('/tmp'): 
        run('wget http://apache.mirrors.multidist.eu/couchdb/'+
            'releases/1.2.0/apache-couchdb-1.2.0.tar.gz')
        run('tar -xzvf apache-couchdb-1.2.0.tar.gz')
        run('cd apache-couchdb-1.2.0; ./configure; make')
        sudo('cd apache-couchdb-1.2.0; make install')
    print("not Implemented")

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
    require.postfix.server('myinstance.mycozycloud.com')

    sudo ('mkdir -p /home/cozy/')
    user.create('cozy', '/home/cozy/','/bin/sh')
    sudo ('chown cozy:cozy /home/cozy/')

    sudo ('git clone git://github.com/mycozycloud/cozy-setup.git' \
        + ' /home/cozy/cozy-setup', user = 'cozy') 
    sudo ('npm install -g coffee-script')

    with cd('/home/cozy/cozy-setup'):
        sudo ('npm install', user = 'cozy')
        sudo ('cp paas.conf /etc/init/')
    sudo ('service paas start')

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
        sudo('coffee home.coffee', user = 'cozy')
        sudo('coffee notes.coffee', user = 'cozy')
        sudo('coffee proxy.coffee', user= 'cozy')

def init_data():
    """
    Data initialisation
    """

    with cd('/home/cozy/cozy-setup/node_modules/haibu/' \
                + 'local/cozy/home/cozy-home'):
        sudo('coffee init.coffee', 'cozy')

def update():
    """
    Updating applications
    """

    with cd('/home/cozy/cozy-setup/'):
        sudo('git pull', user='cozy')
        sudo('coffee home.coffee', 'cozy')
        sudo('coffee notes.coffee', 'cozy')
        sudo('coffee proxy.coffee', 'cozy')

def reset_account():
    """
    Delete current accountc 
    """

    with cd('/home/cozy/cozy-setup/node_modules/haibu/' \
                + 'local/cozy/home/cozy-home'):
        sudo('coffee cleandb.coffee','cozy')
        sudo('coffee init.coffee','cozy')
