import string
import random
import time

from fabric.api import run, sudo, cd, prompt, task, settings
from fabtools import require, python, supervisor, deb, system, nodejs, service
from fabtools.require import file as require_file
from fabric.contrib import files
from fabric.colors import green, red
from fabric.context_managers import hide

'''
Script to set up a cozy cloud environnement from a fresh system
Validated on a Debian squeeze 64 bits up to date.

Once your system is updated, launch
$ fab -H user@Ip.Ip.Ip.Ip:Port install
to install the full Cozy stack.
'''


# Helpers
def id_generator(
        size=32,
        chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))


def simple_id_generator(size=40, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


@task
def is_arm():
    result = run('lscpu', quiet=True)
    return 'arm' in result

username = id_generator()
password = id_generator()
token = simple_id_generator()


def print_failed(module):
    print(red('Installation of %s failed.\n' +
              'You can join us on our IRC channel: '
              + '#cozycloud on freenode.net to ask for assistance.') % module)
    exit()


def cozydo(cmd):
    '''Run a command as a cozy user'''
    sudo(cmd, user='cozy')


def delete_if_exists(filename):
    '''Delete given file if it already exists'''
    if files.exists(filename):
        sudo('rm -rf %s' % filename)


def su_delete(filename):
    '''Delete given file with root permission'''
    sudo('rm -rf %s' % filename)


# Tasks


@task
def install():
    '''
    Install the full cozy stack.
    '''
    install_tools()
    install_node08()
    install_couchdb()
    install_postfix()
    create_cozy_user()
    config_couchdb()
    install_monitor()
    install_controller()
    install_indexer()
    install_data_system()
    install_home()
    install_proxy()
    #init_domain()
    create_cert()
    install_nginx()
    print(green('Cozy installation finished. Now, enjoy !'))


@task
def uninstall_all():
    '''
    Uninstall the whole stack (work in progress)
    '''
    uninstall_cozy()
    uninstall_node08()
    uninstall_couchdb()
    uninstall_redis()
    uninstall_postfix()


@task
def install_dev():
    '''
    Install stuff to prepare a virtual machine dedicated to development.
    '''
    install_tools()
    install_node08()
    install_couchdb()
    install_postfix()
    create_cozy_user()
    install_monitor()
    install_controller_dev()
    install_indexer()
    install_data_system()
    install_home()
    install_proxy()
    #init_domain()
    print(green('The Cozy development environment has been installed.'))


@task
def install_tools():
    '''
    Install build tools
    '''
    deb.update_index()
    deb.upgrade()
    require.deb.packages([
        'python',
        'python-setuptools',
        'python-pip',
        'openssl',
        'libssl-dev',
        'libxml2-dev',
        'libxslt1-dev',
        'build-essential',
        'git',
        'sudo',
        'lsb-release',
    ])
    print(green('Tools successfully installed'))


@task
def install_node08():
    '''
    Install Node 0.8.18 (0.18.21 for ARM hardwares)
    '''

    if not is_arm():
        require.nodejs.installed_from_source('0.8.18')
        print(green('Node 0.8.18 successfully installed'))
    else:
        version = '0.8.21'
        folder = 'node-v%s-linux-arm-pi' % version
        filename = folder + '.tar.gz'
        require.files.directory('/opt/node', use_sudo=True)
        archive_path = 'http://nodejs.org/dist/v%s/%s' % (version, filename)
        require_file(url=archive_path)
        run('tar -xzf %s' % filename)
        sudo('cp -r %s/* /opt/node' % folder)
        sudo('ln -s /opt/node/bin/node  /usr/local/bin/node')
        sudo('ln -s /opt/node/bin/npm  /usr/local/bin/npm')
        su_delete(folder)
        su_delete(filename)
        result = run('node -v')
        if '0.8.21' in result:
            print(green('Node 0.8.21 successfully installed'))
        else:
            print(red('Something went wrong while installing Node 0.8.21'))


@task
def uninstall_node08():
    '''
    Uninstall node 0.8.18
    '''

    sudo('npm uninstall npm')
    require_file(url='http://nodejs.org/dist/v0.8.9/node-v0.8.18.tar.gz')
    sudo('tar -xzf node-v0.8.18.tar.gz')
    with cd('node-v0.8.18'):
        sudo('./configure')
        sudo('make uninstall')
        sudo('make distclean')
    su_delete('node-v0.8.18*')
    print(green('Node 0.8.18 successfully uninstalled'))


@task
def install_couchdb():
    '''
    Install CouchDB 1.3.0
    '''
    packages = [
        'erlang',
        'libicu-dev',
        'libcurl4-openssl-dev',
        'curl'
    ]

    if system.distrib_id() == 'Debian' \
            and system.distrib_release().startswith('6'):
        packages.append('libmozjs-dev')
    else:
        packages.append('libmozjs185-dev')
    require.deb.packages(packages)

    require_file(
        url='http://apache.crihan.fr/dist/couchdb/source/' +
        '1.3.0/apache-couchdb-1.3.0.tar.gz')
    run('tar -xzvf apache-couchdb-1.3.0.tar.gz')
    with cd('apache-couchdb-1.3.0'):
        run('./configure; make')
        result = sudo('make install')
        installed = result.find('You have installed Apache CouchDB,' +
                                ' time to relax.')
        if installed == -1:
            print_failed('couchdb')
    su_delete('apache-couchdb-1.3.0')
    su_delete('rm -rf apache-couchdb-1.3.0.tar.gz')

    require.users.user('couchdb', home='/usr/local/var/lib/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/etc/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/lib/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/log/couchdb')
    sudo('chown -R couchdb:couchdb /usr/local/var/run/couchdb')
    sudo('chmod 0770 /usr/local/etc/couchdb')
    sudo('chmod 0770 /usr/local/var/lib/couchdb')
    sudo('chmod 0770 /usr/local/var/log/couchdb')
    sudo('chmod 0770 /usr/local/var/run/couchdb')

    require.supervisor.process(
        'couchdb', user='couchdb',
        command='couchdb', autostart='true',
        environment='HOME=/usr/local/var/lib/couchdb')
    print(green('CouchDB 1.3.0 successfully installed'))


@task
def config_couchdb():
    if files.exists('/etc/cozy/couchdb.login'):
        # CouchDB has an old admin
        with hide('running', 'stdout'):
            # Recover old password
            logins = sudo('cat /etc/cozy/couchdb.login')
            logsCouchDB = logins.split('\r\n')
            # Add new admin
            couch_admin_path = '@127.0.0.1:5984/_config/admins/'
            run('curl -X PUT http://%s:%s%s%s -d \'\"%s\"\'' %
                (
                    logsCouchDB[0],
                    logsCouchDB[1],
                    couch_admin_path,
                    username,
                    password,
                ))
            # Delete old admin
            run('curl -X DELETE ' +
                'http://%s:%s@127.0.0.1:5984/_config/admins/%s' %
                (username, password, logsCouchDB[0]))
            sudo('rm -rf /etc/cozy/couchdb.login')
    else:
        # CouchDB has not an admin
        # Create admin
        with hide('running', 'stdout'):
            couch_admin_path = '127.0.0.1:5984/_config/admins/'
            run('curl -X PUT http://%s%s -d \'\"%s\"\'' %
                (couch_admin_path, username, password))
        sudo('mkdir -p /etc/cozy')
    # Create file to keep admin's password
    require.files.file(
        path='/etc/cozy/couchdb.login',
        contents=username + '\n' + password,
        use_sudo=True,
        owner='cozy-data-system',
        mode='700'
    )
    print(green('CouchDB 1.3.0 successfully configured'))


@task
def uninstall_couchdb():
    '''
    Install CouchDB 1.3.0
    '''
    require_file(
        url='http://apache.crihan.fr/dist/couchdb/source/' +
        '1.3.0/apache-couchdb-1.3.0.tar.gz')
    run('tar -xzvf apache-couchdb-1.3.0.tar.gz')
    with cd('apache-couchdb-1.3.0'):
        sudo('./configure')
        sudo('make uninstall')
        sudo('make distclean')
    su_delete('/usr/local/share/couchdb')
    su_delete('/usr/local/lib/couchdb')
    su_delete('/usr/local/var/lib/couchdb')
    su_delete('/usr/local/var/log/couchdb')
    su_delete('/usr/local/var/run/couchdb')
    su_delete('/usr/local/share/doc/couchdb')
    su_delete('/usr/local/bin/couchjs')
    su_delete('/usr/local/bin/couchdb')
    su_delete('apache-couchdb-1.3.0')
    su_delete('apache-couchdb-1.3.0.tar.gz')
    su_delete('/etc/supervisor/conf.d/couchdb.conf')
    su_delete('/etc/cozy/couchdb.login')
    supervisor.update_config()
    print(green('CouchDB 1.3.0 successfully uninstalled'))


@task
def uninstall_redis():
    '''
    Uninstall Redis 2.4.14
    '''
    su_delete('/var/lib/redis')
    su_delete('/var/db/redis')
    su_delete('/var/log/redis')
    su_delete('/var/run/redis')
    su_delete('/opt/redis-2.4.14')
    su_delete('/etc/redis')
    su_delete('/etc/supervisor/conf.d/redis_cozy.conf')
    supervisor.update_config()
    print(green('Redis 2.4.14 successfully uninstalled'))


@task
def install_postfix():
    '''
    Install a postfix instance (required for mail sending).
    '''
    #domain = prompt('Enter your domain name:',
    #                default='myinstance.cozycloud.cc')
    require.postfix.server('cozycloud.cc')
    print(green('Postfix successfully installed'))


@task
def uninstall_postfix():
    '''
    Uninstall postfix.
    '''
    require.deb.uninstall('postfix')
    print(green('Postfix successfully uninstalled'))


@task
def uninstall_cozy():
    '''
    Uninstall postfix.
    '''
    supervisor.stop_process('cozy-controller')
    supervisor.stop_process('cozy-indexer')
    su_delete('/usr/local/var/cozy-indexer')
    su_delete('/etc/supervisor/conf.d/cozy-controller.conf')
    su_delete('/etc/supervisor/conf.d/cozy-indexer.conf')
    supervisor.update_config()
    print(green('Cozy successfully uninstalled'))


@task
def create_cozy_user():
    '''
    Add Cozy user with no home directory.
    '''
    require.user('cozy', home=False, create_home=False)
    require.user('cozy-data-system', create_home=True)
    require.user('cozy-home', create_home=True)
    print(green('Cozy users successfully added'))


@task
def install_monitor():
    '''
    Install Coffeescript, Compound and Cozy Monitor.
    '''
    if is_arm():
        sudo('npm install coffee-script -g')
        sudo('ln -s /usr/local/bin/coffee /opt/node/bin/coffee')
    else:
        require.nodejs.package('coffee-script')
    require.nodejs.package('cozy-monitor')
    require.nodejs.package('compound')
    require.nodejs.package('brunch')
    print(green('Monitor, compound, brunch and coffee script ' +
                'successfully installed'))


@task
def install_controller():
    '''
    Install Cozy Controller Application Manager. Daemonize with supervisor.
    '''
    require.nodejs.package('cozy-controller')
    sudo('mkdir -p /etc/cozy')
    sudo('mkdir -p /etc/cozy/pids')
    require.files.file(
        path='/etc/cozy/controller.token',
        mode='700',
        contents=token,
        use_sudo=True,
        owner='cozy-home'
    )
    path = '/usr/local/lib/node_modules/cozy-controller/bin/cozy-controller'
    require.supervisor.process(
        'cozy-controller',
        command=''.join([
            '/usr/bin/pidproxy ',
            '/etc/cozy/pids/controller.pid ',
            '%s -u --auth --per 755',
        ]) % path,
        environment='NODE_ENV="production"',
        user='root'
    )
    supervisor.stop_process('cozy-controller')
    ## In case where two cozy-controllers are started
    with settings(warn_only=True):
        sudo('pkill -9 node')
    supervisor.start_process('cozy-controller')
    if is_arm():
        time.sleep(15)
    else:
        time.sleep(5)
    with hide('running', 'stdout'):
        result = run('curl -X GET http://127.0.0.1:9002/ ' +
                     '-H "x-auth-token: %s"' % token)
    if result != '{"message":"No drones specified"}':
        print_failed('cozy-controller')
    print(green('Cozy Controller successfully started'))


@task
def install_controller_dev():
    '''
    Install Cozy Controller Application Manager. Daemonize with supervisor.
    '''
    require.nodejs.package('cozy-controller')
    require.supervisor.process(
        'cozy-controller',
        command='cozy-controller -c -u --per 755',
        environment='NODE_ENV="development"',
        user='root'
    )
    supervisor.restart_process('cozy-controller')
    import time
    time.sleep(5)
    with hide('running', 'stdout'):
        result = run('curl -X GET http://127.0.0.1:9002/')
    if result != '{"message":"No drones specified"}':
        print_failed("cozy-controller")
    print(green('Cozy Controller successfully started'))


@task
def install_indexer():
    '''
    Install Cozy Data Indexer. Use supervisord to daemonize it.
    '''
    home = '/usr/local/cozy-indexer'
    indexer_dir = '%s/cozy-data-indexer' % home
    indexer_env_dir = '%s/virtualenv' % indexer_dir
    python_exe = indexer_dir + '/virtualenv/bin/python'
    indexer_exe = 'server.py'
    process_name = 'cozy-indexer'

    require.files.directory(home, use_sudo=True)

    with cd(home):
        if files.exists('cozy-data-indexer'):
            su_delete('cozy-data-indexer')
        sudo('git clone https://github.com/mycozycloud/cozy-data-indexer.git')

    require.python.virtualenv(indexer_env_dir, use_sudo=True)
    with python.virtualenv(indexer_env_dir):
        sudo(
            'pip install --use-mirrors -r %s/requirements/common.txt' %
            indexer_dir)

    sudo('chown -R cozy:cozy %s' % home)

    require.supervisor.process(
        process_name,
        command='%s %s' % (python_exe, indexer_exe),
        directory=indexer_dir,
        user='cozy'
    )
    supervisor.restart_process(process_name)
    result = run('curl -X GET http://127.0.0.1:9102/')
    is_installed = result.find("Cozy Data Indexer")
    if is_arm():
        time.sleep(10)
    if is_installed == -1:
        print_failed("cozy-data-indexer")
    print(green("Data Indexer successfully started"))


@task
def install_data_system():
    '''
    Install Cozy Data System. Daemonize with Haibu.
    '''
    result = sudo('cozy-monitor install data-system')
    installedApp = result.find('successfully installed')
    if installedApp == -1:
        print_failed('data-system')
    else:
        print(green('Data-system successfully installed'))


@task
def install_home():
    '''
    Install Cozy Home
    '''
    result = sudo('cozy-monitor install home')
    installedApp = result.find('successfully installed')
    if installedApp == -1:
        print_failed('home')
    else:
        print(green('Home successfully installed'))


@task
def install_proxy():
    '''
    Install Cozy Proxy
    '''
    result = sudo('cozy-monitor install proxy')
    installedApp = result.find('successfully installed')
    if installedApp == -1:
        print_failed('proxy')
    else:
        print(green('Proxy successfully installed'))


@task
def init_domain():
    '''
    Register domain name inside Cozy Home.
    '''
    domain = prompt('What is your domain name (ex: cozycloud.cc)?')
    cozydo('cozy-monitor script home setdomain %s' % domain)
    print(green('Domain set to: %s' % domain))


@task
def create_cert():
    '''
    Create SSL certificates.
    '''

    etc_dir = '/etc/cozy'
    require.files.directory(etc_dir, use_sudo=True, owner='cozy')
    with cd(etc_dir):
        sudo('openssl genrsa -out ./server.key 1024')
        sudo(
            'openssl req -new -x509 -days 3650 -key ' +
            './server.key -out ./server.crt  -batch')
        sudo('chmod 640 server.key')
        require.group('ssl-cert')
        sudo('chown cozy:ssl-cert ./server.key')
    print(green('Certificates successfully created.'))


PROXIED_SITE_TEMPLATE = '''
server {
    listen %(port)s;
    server_name %(server_name)s;

    ssl_certificate /etc/cozy/server.crt;
    ssl_certificate_key /etc/cozy/server.key;
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
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    access_log /var/log/nginx/%(server_name)s.log;
}
'''


@task
def install_nginx():
    '''
    Install NGINX and make it use certs.
    '''
    if system.distrib_id() == 'Debian':
        require_file(url='http://nginx.org/packages/keys/nginx_signing.key')
        deb.add_apt_key('nginx_signing.key')
        su_delete('nginx_signing.key')

        url = 'http://nginx.org/packages/debian/'
        distrib = 'squeeze'
        if system.distrib_release().startswith('7'):
            distrib = 'wheezy'
        require.deb.source('nginx', url, distrib, 'nginx')

        require.deb.package('nginx')
        contents = PROXIED_SITE_TEMPLATE % {
            'server_name': 'cozy',
            'port': 443,
            'proxy_url': 'http://127.0.0.1:9104'
        }
        require.files.file(
            '/etc/nginx/conf.d/cozy.conf',
            contents=contents,
            use_sudo=True)

    else:
        require.deb.ppa('ppa:nginx/stable')

        require.nginx.site(
            'cozy',
            template_contents=PROXIED_SITE_TEMPLATE,
            enabled=True,
            port=443,
            proxy_url='http://127.0.0.1:9104'
        )
    if files.exists('/etc/nginx/conf.d/default.conf'):
        su_delete('/etc/nginx/conf.d/default.conf')
    if files.exists('/etc/nginx/conf.d/example_ssl.conf'):
        su_delete('/etc/nginx/conf.d/example_ssl.conf')
    service.restart('nginx')
    print(green('Nginx successfully installed.'))


## No setup tasks

@task
def update_stack():
    '''
    Update applications
    '''
    supervisor.stop_process('cozy-controller')
    nodejs.update_package('cozy-controller')
    supervisor.start_process('cozy-controller')
    nodejs.update_package('cozy-monitor')
    sudo('cozy-monitor install data-system')
    sudo('cozy-monitor install home')
    sudo('cozy-monitor token')
    sudo('cozy-monitor install proxy')
    print(green('Stack updated successfully.'))


@task
def update_all_apps():
    sudo('cozy-monitor reinstall-all')
    print(green('All apps successfully updated.'))


@task
def reset_account():
    '''
    Delete current user account
    '''
    with cd('/home/cozy/cozy-setup'):
        cozydo('cozy-monitor script home cleanuser')
    print(green('Current account deleted.'))
