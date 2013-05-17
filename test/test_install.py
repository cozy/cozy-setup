from __future__ import with_statement

import os
import unittest
import mock

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from fabric.api import env, hide, lcd, local, settings, shell_env, sudo
from fabric.state import connections
from fabtools.files import watch
from fabric.contrib.files import comment, uncomment

import fabtools
from fabtools import require

#from ..cozy-setup.fabfile import install

## Version
#  Send vagrant version
def version():
    """
	Get the vagrant version as a tuple
	"""
    with settings(hide('running')):
        res = local('vagrant --version', capture=True)
    ver = res.split()[2]
    return tuple(map(int, ver.split('.')))


## Halt and destroy
#  Stopped and destroy vagrant box
def halt_and_destroy():
    """
	Halt and destoy virtual machine
	"""
    with lcd(os.path.dirname(__file__)):
        if os.path.exists(os.path.join(env['lcwd'], 'Vagrantfile')):
            local('vagrant halt')
            if version() >= (0, 9, 99):
                local('vagrant destroy -f')
            else:
                local('vagrant destroy')

## Start box
def start_box():
    """
    Spin up a new vagrant box
    """
    # Create a fresh vagrant config file
    local('rm -f Vagrantfile')
    local('vagrant init unbuntu_12.04 http://files/.vagrantup.com/lucid64.box')

    halt_and_destroy()

    # Modify Vagrantfile
    local('rm -f Vagrantfile')
    local('cp ./helpers/Vagrantfile .')

    # Spin up the box
    # (retry as it sometimes fails for no good reason)
    cmd = 'vagrant up'
    local('%s || %s' % (cmd, cmd))

## Install cozy :
#  Install cozy on box thanks to fabfile.py
def install_cozy():
    """
    Install cozy on VM thanks to fabfile
    """
    local('fab --fabfile="../fabfile.py" -H vagrant@192.168.33.10 install')

## Test status :
#  Check status
#  All applications should be up
def test_status(app):
    """
    Test if all modules are started
    """    
    result = sudo('cozy-monitor status')
    startedApps = result.count("up")
    brokenApps = result.count("down")
    # Check number of started application
    print("Expect %s started applications and %s applications are started" %app %startedApps)
    assert startedApps == app
    # Check number of broken application
    print("Expect 0 broken applications and %s applications are broken" %brokenApps)
    assert brokenApps == 0

## Test register :
#  Send register request to proxy
#  Answer should be 'Login succeded' 
def test_register(): 
    """
    Test if login works
    """        
    print("Test register")
    result = sudo('curl  -H "Accept: application/json" -H "Content-type: application/json"'
            ' -X POST http://localhost:9104/register -d \'{"email": "test@cozycloud.cc", '
            '"password": "password"}\'')
    assert result == '{"success":true,"msg":"Login succeeded"}'

## Test bad register :
#  Send register request to proxy when user is already registered
#  Answer should be 'User already registered' 
def test_bad_register():
    print("Test register with a user already registered")
    result = sudo('curl  -H "Accept: application/json" -H "Content-type: application/json"'
            ' -X POST http://localhost:9104/register -d \'{"email": "test@cozycloud.cc", '
            '"password": "password"}\'')
    assert result == '{"error":true,"msg":"User already registered."}'

## Test install app :
#  Install an application via home
#  Answer should be Install successfully
def test_install_app():
    print("Test installation of application mails")
    result = sudo('cozy-monitor install_home mails');
    installedApp = result.count("successfully installed")
    assert installedApp == 1

## Test uninstall app :
#  Uninstall an application via home
#  Answer should be uninstall successfully
def test_uninstall_app():
    print("Test installation of application mails")
    result = sudo('cozy-monitor uninstall_home mails');
    uninstalledApp = result.count("successfully uninstalled")
    assert uninstalledApp == 1

 
## Test installation of cozy
#  Start vagrant box
#  Install cozy on this box
#  Test if cozy is well installed
def test_install_cozy():
    #start_box()
    install_cozy()
    test_status(7)
    test_register()
    test_bad_register()
    test_install_app()
    test_status(8)
    test_uninstall_app()