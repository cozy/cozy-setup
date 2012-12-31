from fabric.api import run, sudo, cd, prompt, task
from fabtools import require, python, supervisor, service
from fabric.contrib import files
from fabric.colors import green

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

@task
def install():
    install_tools()
    install_node08()
    install_couchdb()
    install_redis()
    pre_install()
    install_haibu()
    install_data_system()
    install_indexer()
    install_apps()
    init_data()
    init_domain()
    create_cert()
    install_nginx()
    print(green("Cozy installation finished. Now, enjoy !"))
    
@task
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
        'libxml2-dev',
        'libxslt-dev',
        'build-essential',
        'git',
        'sudo',
    ])
    print(green("Tools successfully installed"))

@task
def install_node08():
    """
    Installing Node 0.8.9    
    """
    require.nodejs.installed_from_source("0.8.9")
    print(green("Node 0.8.9 successfully installed"))

@task
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
    print(green("CouchDB 1.2.0 successfully installed"))
    
@task
def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14
    """

    require.redis.installed_from_source('2.4.14')
    require.redis.instance('cozy','2.4.14',)
    print(green("Redis 2.4.14 successfully installed"))

@task
def pre_install():
    """
    Preparing Cozy Launching
    """
    require.postfix.server('myinstance.cozycloud.cc')

    # Create cozy user
    require.user("cozy", "/home/cozy")

    # Get cozy repo
    delete_if_exists('/home/cozy/cozy-setup')
    sudo('git clone git://github.com/mycozycloud/cozy-setup.git' \
        + ' /home/cozy/cozy-setup', user='cozy') 
    require.files.directory("/root")
    require.nodejs.package('coffee-script')

@task
def install_haibu():
    """
    Setup Haibu Application Manager.
    """

    with cd('/home/cozy/cozy-setup'):
        cozydo('HOME=/home/cozy npm install')
        sudo('cp paas.conf /etc/init/')

    if not service.is_running("paas"):
        service.start('paas')
    else:
        service.restart('paas')

    print(green("Haibu successfully started"))

@task
def install_data_system():
    """
    Installing and deploying cozy-data-system.
    """
    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor install data-system', user='cozy')
    print(green("Data System successfully started"))

@task
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
    print(green("Data Indexer successfully started"))

@task
def install_apps():
    """
    Deploying cozy proxy, home and default application (notes and todos).
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor install home', user='cozy')
        sudo('coffee monitor install_home notes', user='cozy')
        sudo('coffee monitor install_home todos', user='cozy')
        sudo('coffee monitor install proxy', user='cozy')
    print(green("Apps successfully started"))

@task
def init_data():
    """
    Data initialization
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor script notes init', 'cozy')
        sudo('coffee monitor script todos init', 'cozy')
    print(green("Data successfully initialized"))

@task
def init_domain():
    domain = prompt("What is your domain name (ex: cozycloud.cc)?")
    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor script_arg home setdomain %s' % domain, 'cozy')
    print(green("Domain set to: %s" % domain))
    
@task
def create_cert():
    """
    Create SSL certificates.
    """

    run('sudo openssl genrsa -out ./server.key 1024')
    run('sudo openssl req -new -x509 -days 3650 -key ./server.key -out ' + \
        './server.crt')
    run('sudo chmod 640 server.key')
    run('sudo mv server.key /home/cozy/server.key')
    run('sudo mv server.crt /home/cozy/server.crt')
    require.deb.package("nginx")

    run('sudo chown cozy:ssl-cert /home/cozy/server.key')


PROXIED_SITE_TEMPLATE = """\
server {
    listen %(port)s;
    server_name %(server_name)s;

    ssl_certificate /home/cozy/server.crt;
    ssl_certificate_key /home/cozy/server.key;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout  10m;
    ssl_protocols  SSLv3 TLSv1;
    ssl_ciphers  ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv3:+EXP;
    ssl_prefer_server_ciphers   on;
    ssl on;

    gzip_vary on;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect http:// https://; 
        proxy_pass %(proxy_url)s;
    }

    access_log /var/log/nginx/%(server_name)s.log;
}
"""

@task
def install_nginx():
    """
    Install NGINX and make it use certs.
    """
    
    require.nginx.site("cozy",
            template_contents=PROXIED_SITE_TEMPLATE, 
            enabled=True,
            port=443,
            proxy_url='http://127.0.0.1:9104'
    )

## No setup tasks

@task
def update():
    """
    Updating applications
    """

    with cd('/home/cozy/cozy-setup/'):
        sudo('git pull', user='cozy')
        sudo('coffee monitor install data-system', user='cozy')
        sudo('coffee monitor install home', user='cozy')
        sudo('coffee monitor install notes', user='cozy')
        sudo('coffee monitor install todos', user='cozy')
        sudo('coffee monitor install proxy', user='cozy')
    print(green("Applications updated successfully."))

@task
def reset_account():
    """
    Delete current account 
    """

    with cd('/home/cozy/cozy-setup'):
        sudo('coffee monitor.coffee script home cleanuser', 'cozy')
    print(green("Current account deleted."))
