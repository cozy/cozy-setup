import os

from fabric.api import local, lcd, task
from fabric.colors import green

'''
Script to set up a cozy cloud environnement from a fresh system
'''

# Helpers

def sudo(cmd, user=None):
    '''
    Run sudo shell command. Set user to execute command with him.
    '''
    if user is None:
        local("sudo %s" % cmd)
    else:
        local("sudo -u %s %s" % (user, cmd))

def cozydo(cmd):
    '''
    Execute cmd with cozy user.
    '''
    sudo(cmd, "cozy")

def mkdir(dirname, user):
    '''
    Create dir if it does not exist and give ownership to given user.
    '''
    if not os.path.exists(dirname):
        sudo("mkdir -p %s" % dirname)
    sudo("chown %s:%s %s" % (user, user, dirname))

def install_packages(packages):
    '''
    Install given packages through apt-get.
    '''
    local("sudo apt-get install %s" % ' '.join(x for x in packages))

def build_config_file(filename, params, supervisor_name=None, separator="="):
    '''
    Build config with given params while following this scheme:
    
        key1=value1
        key2=value2
        ...
        keyn=valuen
    '''
    lines = []
    if supervisor_name is not None:
        lines.append('[program:%(supervisor_name)s]' % locals())
    for key, value in sorted(params.items()):
        lines.append("%s%s%s" % (key, separator, value))
    file_content = '\n'.join(lines)

    with lcd("/tmp"):
        local('echo "%s" > conf.tmp' % file_content)
        local("sudo cp conf.tmp %s" % filename)
        local("rm conf.tmp")

def update_supervisor():
    '''
    Run supervisor update command
    '''
    local("sudo supervisorctl update")

def add_process(name, **kwargs):
    '''
    Add configuration file to supervisor for given process.
    '''
    params = {}
    params.update(kwargs)
    params.setdefault('autorestart', 'true')
    params.setdefault('redirect_stderr', 'true')
    
    filename = '/etc/supervisor/conf.d/%(name)s.conf' % locals()
    build_config_file(filename, params, name)
    update_supervisor()
     

# Tasks

@task
def install_dev():
    '''
    Install the whole stack required to build cozy application: CouchDB, Redis,
    Cozy Data System.
    '''
    install_tools()
    install_node08()
    install_couchdb()
    set_couchdb_process()
    install_redis()
    set_redis_process()
    create_cozy_user()
    install_indexer()
    set_indexer_process()
    install_data_system()
    set_data_system_process()

def install_light_dev():
    '''
    Install the minimum stack recquired to build apps that don't need to
    persist data. 
    '''
    install_tools()
    install_node08()

def install_medium_dev():
    '''
    Install the minimum stack recquired to build apps that don't need to
    persist data. 
    '''
    install_tools()
    install_node08()
    install_couchdb()
    set_couchdb_process()
    create_cozy_user()
    install_data_system()
    set_data_system_process()

@task
def install_tools():
    '''
    Tools install
    #local("sudo apt-get update")
    '''
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
    '''
    Install Node 0.8.9    
    '''
    local('wget http://nodejs.org/dist/v0.8.9/node-v0.8.9.tar.gz')
    local('tar -xvzf node-v0.8.9.tar.gz')
    local('cd node-v0.8.9 ; ./configure ; make ; sudo make install')
    local('rm node-v0.8.9.tar.gz ; rm -rf node-v0.8.9')
    local('sudo npm install coffee-script -g')
    local('sudo npm install stylus -g')
    local('sudo npm install brunch -g')
    local('sudo npm install railway -g')
    local('sudo npm install mocha -g')
    print(green("Node 0.8.9 installed successfully!"))

@task
def install_couchdb():
    '''
    Installing Couchdb.
    '''
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
        '"couchdb" couchdb')
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
    '''
    Daemonize CouchDB with supervisor.
    '''
    add_process('couchdb', user='couchdb', command='couchdb', autostart='true',
        environment='HOME=/usr/local/var/lib/couchdb')
    
@task
def install_redis():
    '''
    Installing and Auto-starting Redis 2.4.14. Use supervisord to daemonize it.
    '''
    BINARIES = [
            'redis-benchmark',
        'redis-check-aof',
        'redis-check-dump',
        'redis-cli',
        'redis-server',
    ]
    name = "cozy"
    dest_dir = '/opt/redis-2.4.14'

    mkdir('/opt/redis-2.4.14', 'redis')
    sudo('adduser --system --home /usr/local/var/lib/redis '+
        '--no-create-home --shell /bin/bash --group --gecos '+
        '"redis" redis')
    
    with lcd('/tmp'):
        local('wget http://redis.googlecode.com/files/redis-2.4.14.tar.gz')
        local('tar xzf redis-2.4.14.tar.gz')

    with lcd('/tmp/redis-2.4.14'):
        local('make')

        for filename in BINARIES:
            sudo('cp -pf src/%(filename)s %(dest_dir)s/' % locals())
            sudo('chown redis: %(dest_dir)s/%(filename)s' % locals())

    mkdir('/etc/redis', 'redis')
    mkdir('/var/db/redis', 'redis')
    mkdir('/var/log/redis', 'redis')
    mkdir('/var/run/redis', 'redis')

    params = {}
    params.setdefault('bind', '127.0.0.1')
    params.setdefault('port', '6379')
    params.setdefault('logfile', '/var/log/redis/redis-%(name)s.log' % locals())
    params.setdefault('loglevel', 'verbose')
    params.setdefault('dbfilename', '/var/db/redis/redis-%(name)s-dump.rdb' % locals())
    params.setdefault('save', '900 1')
    params.setdefault('save', '300 10')
    params.setdefault('save', '60 10000')
    build_config_file("/etc/redis/cozy.conf", params, supervisor_name= None,
                      separator=" ")

@task
def set_redis_process():
    '''
    Daemonize Data Indexer with supervisor.
    '''
    redis_bin = '/opt/redis-2.4.14/redis-server'
    redis_config = '/etc/redis/cozy.conf'

    add_process('redis', user='redis', 
        command='%s %s' % (redis_bin, redis_config),
        directory='/var/run/redis',
        autostart='true')

@task
def create_cozy_user():
    sudo('adduser --system --shell /bin/bash --group --gecos '+
        '"cozy" cozy')

@task
def install_indexer():
    '''
    Deploy Cozy Data Indexer.
    '''
    sudo("pip install virtualenv")

    with lcd("/home/cozy"):
        cozydo("git clone https://github.com/mycozycloud/cozy-data-indexer.git")

    data_indexer_home = "/home/cozy/cozy-data-indexer"
    with lcd(data_indexer_home):
        cozydo("virtualenv virtualenv")
        prefix = ". ./virtualenv/bin/activate && sudo -u cozy "
        local("%s pip install -r requirements/common.txt" % prefix)
        local("%s pip install -r requirements/production.txt" % prefix)

@task
def set_indexer_process():
    '''
    Daemonize Data Indexer with supervisor.
    '''
    data_indexer_home = "/home/cozy/cozy-data-indexer"
    python_bin = '%s/virtualenv/bin/python' % data_indexer_home
    add_process('cozy-data-indexer', user='cozy', 
        command='%s %s/server.py' % (python_bin, data_indexer_home),
        autostart='true')

@task
def install_data_system():
    '''
    Installing and deploying cozy-data-system.
    '''
    with lcd("/home/cozy"):
        cozydo("git clone https://github.com/mycozycloud/cozy-data-system.git")

    data_system_home = "/home/cozy/cozy-data-system"
    with lcd(data_system_home):
        cozydo("npm install")
        
@task
def set_data_system_process():
    '''
    Daemonize Data System with supervisor.
    '''
    data_system_home = "/home/cozy/cozy-data-system"
    coffee_bin = '%s/node_modules/coffee-script/bin/coffee' % data_system_home
    add_process('cozy-data-system', user='cozy', 
        command='%s %s/server.coffee' % (coffee_bin, data_system_home),
        autostart='true',
        environment='NODE_ENV="production"')
