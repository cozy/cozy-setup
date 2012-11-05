from fabric.api import run, sudo, cd
from fabtools import require, python, supervisor
from fabric.contrib import files

"""
Script to set up a cozy cloud environnement from a fresh system
Validated on a Debian squeeze 64 bits up to date.

Once your system is updated, launch 
$ fab -H user@Ip.Ip.Ip.Ip:Port install
to install the full Cozy stack.
"""

# Helpers

cozy_home = "/home/cozy"
cozy_user = "user"

def cozydo(cmd):
    """Run a commande as a newebe user"""

    sudo(cmd, user="cozy")

def delete_if_exists(filename):
    """Delete given file if it already exists"""

    if files.exists(filename):
        cozydo("rm -rf %s" % filename)

# Tasks

def install():
    install_tools()
    install_node08()
    install_couchdb()
    install_redis()
    pre_install()
    install_haibu()
    install_data_system()
    install_indexer()
    #create_certif()
    install_apps()
    init_data()
    
    #Post install
    #Setdomain.coffee, initproxy.coffee
    #SetNginx behind https

def install_tools():
    """
    Tools install
    """
    require.deb.update_index()
    require.deb.upgrade()
    require.deb.packages([
        'python',
        'python-setuptools',
        'python-pip',
        'openssl',
        'libssl-dev',
        'build-essential',
        'git',
        'sudo',
    ])

def install_node08():
    """
    Installing Node 0.8.9    
    """
    require.nodejs.installed_from_source("0.8.9")

def install_couchdb():
    """
    Installing Couchdb
    """
    require.deb.packages([
        'erlang', 
        'libicu-dev', 
        'libmozjs-dev',
        'libcurl4-openssl-dev'
    ])

    with cd('/tmp'): 
        run('wget http://apache.mirrors.multidist.eu/couchdb/'+
            'releases/1.2.0/apache-couchdb-1.2.0.tar.gz')
        run('tar -xzvf apache-couchdb-1.2.0.tar.gz')
        run('cd apache-couchdb-1.2.0; ./configure; make')
        sudo('cd apache-couchdb-1.2.0; make install')
        run('rm -rf apache-couchdb-1.2.0')
        run('rm -rf apache-couchdb-1.2.0.tar.gz')

    require.users.user("couchdb", home='/usr/local/var/lib/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/etc/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/lib/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/log/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/run/couchdb')
    sudo('chmod 0770 /usr/local/etc/couchdb')
    sudo('chmod 0770 /usr/local/var/lib/couchdb')
    sudo('chmod 0770 /usr/local/var/log/couchdb')
    sudo('chmod 0770 /usr/local/var/run/couchdb')
    
    require.supervisor.process('couchdb', user = 'couchdb', 
        command = 'couchdb', autostart='true',
        environment ='HOME=/usr/local/var/lib/couchdb')
    
def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14
    """

    require.redis.installed_from_source('2.4.14')
    require.redis.instance('cozy','2.4.14',)

def pre_install():
    """
    Preparing Cozy Launching
    """
    require.postfix.server('myinstance.cozycloud.cc')

    # Create cozy user
    require.user("cozy", "/home/cozy")

    # Get cozy repo
    sudo('git clone git://github.com/mycozycloud/cozy-setup.git' \
        + ' /home/cozy/cozy-setup', user='cozy') 
    require.nodejs.package('coffee-script')

def install_haibu():
    """
    Setup Haibu Application Manager.
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('npm install', user='cozy')
        sudo('cp paas.conf /etc/init/')
    sudo('service paas start')

def install_data_system():
    """
    Installing and deploying cozy-data-system.
    """
    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor install data-system', user='cozy')

def install_indexer():
    """
    Deploy Cozy Data Indexer. Use supervisord to daemonize it.
    """

    indexer_dir = "%s/cozy-data-indexer" % cozy_home
    indexer_env_dir = "%s/virtualenv" % indexer_dir
    python_exe = indexer_dir + "/virtualenv/bin/python"
    indexer_exe = "server.py"
    process_name = "cozy-indexer"

    with cd(cozy_home):
        delete_if_exists("cozy-data-indexer")
        cozydo('git clone git://github.com/mycozycloud/cozy-data-indexer.git')

    require.python.virtualenv(indexer_env_dir, use_sudo=True, user="cozy")

    with python.virtualenv(indexer_env_dir):
        cozydo("pip install --use-mirrors -r %s/requirements/common.txt" % \
                indexer_dir)

    require.supervisor.process(process_name,
        command='%s %s' % (python_exe, indexer_exe),
        directory=indexer_dir,
        user=cozy_user
    )
    supervisor.restart_process(process_name)

def create_certif():
    """
    Creating SSL certificats.
    """

    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ' + \
        './server.crt')
    run('sudo chmod 640 server.key')
    run('sudo mv server.key /home/cozy/server.key')
    run('sudo mv server.crt /home/cozy/server.crt')
    run('sudo chown cozy:ssl-cert /home/cozy/server.key')

def install_apps():
    """
    Deploying cozy proxy, home and default application (notes and todos).
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor install home', user='cozy')
        sudo('coffee monitor install notes', user='cozy')
        sudo('coffee monitor install todos', user='cozy')
        sudo('coffee monitor install proxy', user='cozy')

def init_data():
    """
    Data initialisation
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor script home init', 'cozy')
        sudo('coffee monitor script notes init', 'cozy')
        sudo('coffee monitor script todos init', 'cozy')

def update():
    """
    Updating applications
    """

    with cd('/home/cozy/cozy-setup/'):
        sudo('git pull', user='cozy')
        sudo('coffee monitor install home', user='cozy')
        sudo('coffee monitor install notes', user='cozy')
        sudo('coffee monitor install todos', user='cozy')

def reset_account():
    """
    Delete current account 
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor.coffee script home init', 'cozy')
        sudo('coffee monitor.coffee script home cleandb', 'cozy')

def test_supervisor():
    command = '/home/cozy/cozy-setup/node_modules/haibu/bin' \
        + '/haibu --coffee'
    env = 'NODE_ENV=production'
    require.supervisor.process('cozy_paas', user = 'cozy', 
      command = command, environment = env, autostart = 'true',)
