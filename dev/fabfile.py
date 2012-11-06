from fabric.api import local, lcd
from fabric.contrib import files
from fabric.colors import green

"""
Script to set up a cozy cloud environnement from a fresh system
"""

def sudo(cmd, user=None):
    if user:
        local("sudo %s" % cmd)
    else:
        local("sudo --user %s %s" % (user, cmd))

def cozydo(cmd):
    sudo(cmd, "cozy")

def install_packages(packages):
    local("sudo apt-get install %s" % ' '.join(x for x in packages))

def update_supervisor():
    local("sudo supervisorctl update")

def add_process(name, **kwargs):
    # Set default parameters
    params = {}
    params.update(kwargs)
    params.setdefault('autorestart', 'true')
    params.setdefault('redirect_stderr', 'true')

    # Build config file from parameters
    lines = []
    lines.append('[program:%(name)s]' % locals())
    for key, value in sorted(params.items()):
        lines.append("%s=%s" % (key, value))

    # Upload config file
    filename = '/etc/supervisor/conf.d/%(name)s.conf' % locals()
    file_content = '\n'.join(lines)
    local('echo "%s" > conf.tmp' % file_content)
    local("sudo cp conf.tmp %s" % filename)
    local("rm conf.tmp")
    update_supervisor()
     

# Tasks

def install_dev():
    install_tools()

def install_tools():
    """
    Tools install
    #local("sudo apt-get update")
    """
    #local("sudo apt-get upgrade")
    dependencies = [
        'python',
        'python-setuptools',
        'python-pip',
        'git',
        'build-essential',
    ]
    install_packages(dependencies)
    print(green("Tools installed successfully!"))

def install_node08():
    """
    Installing Node 0.8.9    
    """
    local('wget http://nodejs.org/dist/v0.8.9/node-v0.8.9.tar.gz')
    local('tar -xvzf node-v0.8.9.tar.gz')
    local('cd node-v0.8.9 ; ./configure ; make ; sudo make install')
    local('rm node-v0.8.9.tar.gz ; rm -rf node-v0.8.9')
    print(green("Node 0.8.9 installed successfully!"))

def install_couchdb():
    """
    Installing Couchdb. Use supervisord to daemonize it.
    """
    dependencies = [
        'erlang', 'libicu-dev', 'libmozjs-dev','libcurl4-openssl-dev',
        'supervisor'
    ]
    install_packages(dependencies)

    with lcd('/tmp'):
        local('wget http://apache.mirrors.multidist.eu/couchdb/'+
            'releases/1.2.0/apache-couchdb-1.2.0.tar.gz')
        local('tar -xzvf apache-couchdb-1.2.0.tar.gz')
        local('cd apache-couchdb-1.2.0; ./configure; make')
        local('cd apache-couchdb-1.2.0; sudo make install')
        local('rm -rf apache-couchdb-1.2.0')
        local('rm -rf apache-couchdb-1.2.0.tar.gz')

    local('sudo adduser --system --home /usr/local/var/lib/couchdb '+
        '--no-create-home --shell /bin/bash --group --gecos '+
        '"CouchDB_Administrator" couchdb')
    local('sudo chown -R couchdb:couchdb /usr/local/etc/couchdb')
    local('sudo chown -R couchdb:couchdb /usr/local/var/lib/couchdb')
    local('sudo chown -R couchdb:couchdb /usr/local/var/log/couchdb')
    local('sudo chown -R couchdb:couchdb /usr/local/var/run/couchdb')
    local('sudo chmod 0770 /usr/local/etc/couchdb')
    local('sudo chmod 0770 /usr/local/var/lib/couchdb')
    local('sudo chmod 0770 /usr/local/var/log/couchdb')
    local('sudo chmod 0770 /usr/local/var/run/couchdb')

def set_couchdb_process():
    add_process('couchdb', user='couchdb', command='couchdb', autostart='true',
        environment='HOME=/usr/local/var/lib/couchdb')
    
def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14. Use supervisord to daemonize it.
    """
    pass

def create_cozy_user():
    sudo('adduser --system --shell /bin/bash --group --gecos '+
        '"cozy" cozy')

def install_indexer():
    """
    Deploy Cozy Data Indexer. Use supervisord to daemonize it.
    """
    pass

def install_data_system():
    """
    Installing and deploying cozy-data-system. Use supervisord to daemonize it.
    """

    with lcd("/home/cozy"):
        cozydo("git clone https://github.com/mycozycloud/cozy-data-system.git")

    data_system_home = "/home/cozy/cozy-data-system"
    with lcd(data_system_home):
        cozydo("npm install")

def set_data_system_process():
    data_system_home = "/home/cozy/cozy-data-system"
    coffee_bin = '%s/node_modules/coffee-script/bin/coffee' % data_system_home,
    add_process('cozy-data-system', user='cozy', 
        command='%s server.coffee' % coffee_bin,
        autostart='true',
        environment='NODE_ENV="production"')
