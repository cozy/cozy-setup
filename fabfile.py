import string
import random
import time

from fabric import state
from fabric.api import run, sudo, cd, prompt, task, settings
from fabric.contrib import files
from fabric.colors import green, red
from fabric.context_managers import hide
from fabric.tasks import Task
from fabric.task_utils import crawl

from fabtools import require, python, supervisor, deb, system, nodejs, service
from fabtools.require import file as require_file


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


USERNAME = id_generator()
PASSWORD = id_generator()
TOKEN = simple_id_generator()


@task
def is_arm():
    result = run('lscpu', quiet=True)
    return 'arm' in result


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
    restart_cozy()
    print(green('Cozy installation finished. Now, enjoy !'))


def ask_for_confirmation(module):
    '''
    Simple function to ask for confirmation before uninstalling a module
    installed by this fabfile.
    '''
    confirm = prompt('Are you sure you want to definitely remove %s from your'
            ' computer? ' % module, default="no")
    return confirm == "yes"


@task
def uninstall_all():
    '''
    Uninstall the whole stack (work in progress)
    '''

    sudo('cozy-monitor uninstall-all')
    if ask_for_confirmation("Cozy"):
        uninstall_cozy()
    if ask_for_confirmation("Node.js"):
        uninstall_node08()
    if ask_for_confirmation("CouchDB"):
        uninstall_couchdb()
    if ask_for_confirmation("Postfix"):
        uninstall_postfix()
    if ask_for_confirmation("Cozy users"):
        sudo('userdel -r cozy')
        sudo('userdel -r cozy-data-system')
        sudo('userdel -r cozy-home')



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
        'python-dev',
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
        'imagemagick',
        'sqlite3'
    ])
    print(green('Tools successfully installed'))


@task
def install_node08():
    '''
    Install Node 0.8.18
    '''

    require.nodejs.installed_from_source('0.8.18')
    print(green('Node 0.8.18 successfully installed'))


@task
def uninstall_node08():
    '''
    Uninstall node 0.8.20
    '''

    sudo('npm uninstall npm')
    version = '0.8.20'
    folder = 'node-v%s' % version
    filename = folder + '.tar.gz'
    require_file(url='http://nodejs.org/dist/v%s/%s' % (version, filename))
    sudo('tar -xzf %s' % filename)

    with cd('%s' % folder):
        sudo('./configure')
        sudo('make uninstall')
        sudo('make distclean')
    su_delete('%s*' % folder)
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
                    USERNAME,
                    PASSWORD,
                ))
            # Delete old admin
            run('curl -X DELETE ' +
                'http://%s:%s@127.0.0.1:5984/_config/admins/%s' %
                (USERNAME, PASSWORD, logsCouchDB[0]))
            sudo('rm -rf /etc/cozy/couchdb.login')
    else:
        # CouchDB has not an admin
        # Create admin
        with hide('running', 'stdout'):
            couch_admin_path = '127.0.0.1:5984/_config/admins/'
            run('curl -X PUT http://%s%s -d \'\"%s\"\'' %
                (couch_admin_path, USERNAME, PASSWORD))
        sudo('mkdir -p /etc/cozy')

    # Create file to keep admin's password
    require.files.file(
        path='/etc/cozy/couchdb.login',
        contents=USERNAME + '\n' + PASSWORD,
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
    su_delete('/usr/local/cozy-indexer')
    su_delete('/usr/local/cozy')
    su_delete('/home/cozy*')
    su_delete('/etc/cozy')
    su_delete('/etc/nginx/conf.d/cozy.conf')
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
    require.nodejs.package('coffee-script')
    require.nodejs.package('cozy-monitor')
    require.nodejs.package('brunch', version='1.6.3')
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
        contents=TOKEN,
        use_sudo=True,
        owner='cozy-home'
    )
    path = '/usr/local/lib/node_modules/cozy-controller/bin/cozy-controller'
    require.supervisor.process(
        'cozy-controller',
        command="%s -u --auth --per 755" % path,
        environment='NODE_ENV="production"',
        user='root'
    )
    supervisor.stop_process('cozy-controller')
    ## In case where two cozy-controllers are started
    with settings(warn_only=True):
        sudo('pkill -9 node')
    supervisor.start_process('cozy-controller')
    if is_arm():
        time.sleep(20)
    else:
        time.sleep(10)
    with hide('running', 'stdout'):
        result = run('curl -X GET http://127.0.0.1:9002/')
    if result != '{"error":"Wrong auth token"}':
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

    time.sleep(10)
    result = run('curl -X GET http://127.0.0.1:9102/')
    is_installed = result.find("Cozy Data Indexer")

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
    with cd('ls /usr/local/cozy/apps/home/home/cozy-home/'):
        cozydo('coffee commands setdomain %s' % domain)
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


def reset_cert():
    '''
    Reset SSL certificates
    '''

    delete_if_exists('/etc/cozy/server.crt')
    delete_if_exists('/etc/cozy/server.key')
    print(green('Previous certificates successfully deleted.'))
    create_cert()


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
    client_max_body_size 1024M;

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


@task
def restart_cozy():
    sudo('cozy-monitor restart data-system')
    sudo('cozy-monitor restart home')
    sudo('cozy-monitor restart proxy')
    print(green('Stack restarted successfully.'))


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
    sudo('cozy-monitor update data-system')
    sudo('cozy-monitor update home')
    sudo('cozy-monitor update proxy')
    update_indexer()
    print(green('Stack updated successfully.'))


@task
def update_all_apps():
    sudo('cozy-monitor update-all')
    print(green('All apps successfully updated.'))


@task
def update_indexer():
    '''
    Update Cozy indexer module.
    '''
    home = '/usr/local/cozy-indexer'
    indexer_dir = '%s/cozy-data-indexer' % home
    indexer_env_dir = '%s/virtualenv' % indexer_dir

    with cd(indexer_dir):
        sudo('git pull origin master')

    with python.virtualenv(indexer_env_dir):
        sudo(
            'pip install --use-mirrors --upgrade -r %s/requirements/common.txt' %
            indexer_dir)
    supervisor.restart_process('cozy-indexer')


@task
def reset_account():
    '''
    Delete current user account
    '''
    with cd('ls /usr/local/cozy/apps/home/home/cozy-home/'):
        sudo('coffee commands cleanuser')
    print(green('Current account deleted.'))


@task
def reset_controller_token():
    '''
    Reset controller token
    '''

    file_path = '/etc/cozy/controller.token'
    delete_if_exists(file_path)
    print(green('Controller token successfully deleted.'))

    require.files.file(
        path=file_path,
        mode='700',
        contents=TOKEN,
        use_sudo=True,
        owner='cozy-home'
    )
    print(green('Controller token successfully generated.'))


@task
def reset_security_tokens():
    '''
    Reset all the security tokens for the Cozy (SSL certificates,
    Controller token, CouchDB superuser)
    '''

    reset_cert()
    reset_controller_token()
    config_couchdb()
    print(green('All the tokens have been reset.'))


"""Help tasks"""


@task
def help(name=None):
    """Display help for a given task

    Options:
        name    - The task to display help on.

    To display a list of available tasks type:

        $ fab -l

    To display help on a specific task type:

        $ fab help:<name>
    """

    if name is None:
        name = "help"

    task = crawl(name, state.commands)
    if isinstance(task, Task):
        doc = getattr(task, "__doc__", None)
        if doc is not None:
            print("Help on {0:s}:".format(name))
            print(doc)
        else:
            print("No help available for {0:s}".format(name))
    else:
        print("No such task {0:s}".format(name))
        print("For a list of tasks type: fab -l")
