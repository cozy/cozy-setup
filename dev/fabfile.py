from fabric.api import local, lcd, task
from fabric.colors import green

"""
Script to set up a cozy cloud environnement from a fresh system
"""

# Helpers

def sudo(cmd, user=None):
    """
    Run sudo shell command. Set user to execute command with him.
    """
    if user is None:
        local("sudo %s" % cmd)
    else:
        local("sudo --user %s %s" % (user, cmd))

def cozydo(cmd):
    """
    Execute cmd with cozy user.
    """
    sudo(cmd, "cozy")

def install_packages(packages):
    """
    Install given packages through apt-get.
    """
    local("sudo apt-get install %s" % ' '.join(x for x in packages))

def update_supervisor():
    """
    Run supervisor update command
    """
    local("sudo supervisorctl update")

def add_process(name, **kwargs):
    """
    Add configuration file to supervisor for given process.
    """
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

@task
def install_dev():
    """
    Install the whole stack required to build cozy application: CouchDB, Redis,
    Cozy Data System.
    """
    install_tools()

@task
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

@task
def install_node08():
    """
    Install Node 0.8.9    
    """
    local('wget http://nodejs.org/dist/v0.8.9/node-v0.8.9.tar.gz')
    local('tar -xvzf node-v0.8.9.tar.gz')
    local('cd node-v0.8.9 ; ./configure ; make ; sudo make install')
    local('rm node-v0.8.9.tar.gz ; rm -rf node-v0.8.9')
    print(green("Node 0.8.9 installed successfully!"))

@task
def install_couchdb():
    """
    Installing Couchdb.
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

    sudo('adduser --system --home /usr/local/var/lib/couchdb '+
        '--no-create-home --shell /bin/bash --group --gecos '+
        '"CouchDB_Administrator" couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/etc/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/lib/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/log/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/run/couchdb')
    sudo('chmod 0770 /usr/local/etc/couchdb')
    sudo('chmod 0770 /usr/local/var/lib/couchdb')
    sudo('chmod 0770 /usr/local/var/log/couchdb')
    sudo('chmod 0770 /usr/local/var/run/couchdb')

@task
def set_couchdb_process():
    """
    Daemonize CouchDB with supervisor.
    """
    add_process('couchdb', user='couchdb', command='couchdb', autostart='true',
        environment='HOME=/usr/local/var/lib/couchdb')
    
@task
def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14. Use supervisord to daemonize it.
    """
    pass

@task
def create_cozy_user():
    sudo('adduser --system --shell /bin/bash --group --gecos '+
        '"cozy" cozy')

@task
def install_indexer():
    """
    Deploy Cozy Data Indexer.
    """
    sudo("pip install virtualenv")

    with lcd("/home/cozy"):
        cozydo("git clone https://github.com/mycozycloud/cozy-data-indexer.git")

    data_indexer_home = "/home/cozy/cozy-data-indexer"
    with lcd(data_indexer_home):
        cozydo("virtualenv virtualenv")
        cozydo(". ./virtualenv/bin/activate")
        cozydo("pip install -r requirements/common.txt")
        cozydo("pip install -r requirements/production.txt")

@task
def set_data_indexer_process():
    """
    Daemonize Data Indexer with supervisor.
    """
    data_indexer_home = "/home/cozy/cozy-data-indexer"
    python_bin = '%s/virtualenv/bin/python' % data_indexer_home
    add_process('cozy-data-indexer', user='cozy', 
        command='%s %s/server.py' % (python_bin, data_indexer_home),
        autostart='true')

@task
def install_data_system():
    """
    Installing and deploying cozy-data-system.
    """
    with lcd("/home/cozy"):
        cozydo("git clone https://github.com/mycozycloud/cozy-data-indexer.git")

    data_system_home = "/home/cozy/cozy-data-indexer"
    with lcd(data_system_home):
        cozydo("npm install")
        
@task
def set_data_system_process():
    """
    Daemonize Data System with supervisor.
    """
    data_system_home = "/home/cozy/cozy-data-system"
    coffee_bin = '%s/node_modules/coffee-script/bin/coffee' % data_system_home
    add_process('cozy-data-system', user='cozy', 
        command='%s %s/server.coffee' % (coffee_bin, data_system_home),
        autostart='true',
        environment='NODE_ENV="production"')
