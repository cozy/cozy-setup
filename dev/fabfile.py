from fabric.api import local, lcd
from fabric.contrib import files
from fabric.colors import green

"""
Script to set up a cozy cloud environnement from a fresh system
"""


# Tasks

def install():
    install_tools()

def install_tools():
    """
    Tools install
    """
    local("sudo apt-get update")
    local("sudo apt-get upgrade")
    dependencies = [
        'python',
        'python-setuptools',
        'python-pip',
        'git',
        'build-essentials',
    ]
    local("sudo apt-get install %s" % dependencies.join(" "))

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
    Installing Couchdb
    """
    dependencies = [
        'erlang', 'libicu-dev', 'libmozjs-dev','libcurl4-openssl-dev'
    ]
    
def install_redis():
    """
    Installing and Auto-starting Redis 2.4.14
    """
    pass

def install_indexer():
    """
    Deploy Cozy Data Indexer. Use supervisord to daemonize it.
    """
    pass

def install_data_system():
    """
    Installing and deploying cozy-data-system
    """

    pass
