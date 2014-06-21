# -*- coding: utf-8 -*- #
"""
Tests for cozy-setup
"""
import os

from fabric.api import env, hide, lcd, local, settings, abort, sudo
from fabtools import require


# ------------ Vagrant

def vagrant_version():
    """
    Get the vagrant version as a tuple
    """
    with settings(hide('running')):
        result = local('vagrant --version', capture=True)
    version = result.split()[1]
    return tuple([int(x) for x in version.split('.')])


def halt_and_destroy():
    """
    Halt and destoy virtual machine
    """
    if os.path.exists(os.path.join(env['lcwd'], 'Vagrantfile')):
        local('vagrant halt')
        local('vagrant destroy -f')


def start_box(box):
    """
    Spin up a new vagrant box
    """
    if not box or not isinstance(box, basestring):
        abort('No box provided')

    # Require at least vagrant 1.5.00
    if vagrant_version() <= (1, 5, 00):
        abort('You need a vagrant version >= 1.5.00')

    halt_and_destroy()

    # Remove Vagrantfile
    local('rm -f Vagrantfile')

    # Init box
    local('vagrant init ' + box)

    # Modify Vagrantfile to enable private network
    local("sed -i 's/^  # config.vm.network \"private_network\"/  "
          "config.vm.network \"private_network\"/' Vagrantfile")

    local('vagrant up')


# ------------ Cozy

def install_cozy():
    """
    Install cozy on VM thanks to fabfile
    """
    local('fab --fabfile="../../fabfile.py" '
          '-H vagrant@192.168.33.10 install -p vagrant')


# ------------ Utils

def is_dir(path):
    """
    Check if a directory exists
    """
    if path:
        with settings(hide('running', 'warnings'), warn_only=True):
            return local(r'[ -d {0} ]'.format(path)).succeeded
    return False


def _test_install(folder, box):
    """
    Test installation of cozy
    Start vagrant box
    Install cozy on this box
    Test if cozy is well installed
    """
    if not folder or not box:
        abort('_test_install : both parameters are needed')

    if not is_dir(folder):
        local('mkdir ' + folder)

    with lcd(folder):
        start_box(box)
        install_cozy()

        local('vagrant halt -f')


# ------------ Tests

def _test_status(app=5):
    """
Test if all modules are started
All applications should be up
"""
    result = sudo('cozy-monitor status')
    startedApps = result.count("up")
    brokenApps = result.count("down")
    # Check number of started application
    print("Expect %s started applications and %s applications are started" %
          (app, startedApps))
    assert startedApps == app
    # Check number of broken application
    print("Expect 0 broken applications and %s applications are broken" %
          brokenApps)
    assert brokenApps == 0


def _test_pid():
    """
    Test if the PID file exists
    """
    require.files.file(path='/etc/cozy/pids/controller.pid',
                       contents="15042",
                       use_sudo=True,
                       mode='700')


def _test_register():
    """
    Test if login works
    Send register request to proxy
    Answer should be 'Login succeded'
    """

    print("Test register")
    result = sudo('curl -H "Accept: application/json" -H "Content-type: application/json"'
                  ' -X POST http://localhost:9104/register -d \'{"email": "test@cozycloud.cc", '
                  '"password": "password"}\'')
    assert result == '{"success":true,"msg":"Login succeeded"}'


def _test_bad_register():
    """
    Test if login works
    Send register request to proxy when user is already registered
    Answer should be 'User already registered'
    """
    print("Test register with a user already registered")
    result = sudo('curl -H "Accept: application/json" -H "Content-type: application/json"'
                  ' -X POST http://localhost:9104/register -d \'{"email": "test@cozycloud.cc", '
                  '"password": "password"}\'')
    assert result == '{"error":true,"msg":"User already registered."}'


def _test_install_app():
    """
    Test install app
    Install an application via home
    Answer should be 'Install successfully'
    """
    print("Test installation of application mails")
    result = sudo('cozy-monitor install_home mails')
    installed_app = result.count("successfully installed")
    assert installed_app == 1


def _test_uninstall_app():
    """
    Test uninstall app
    Uninstall an application via home
    Answer should be 'Uninstall successfully'
    """
    print("Test installation of application mails")
    result = sudo('cozy-monitor uninstall_home mails')
    uninstalled_app = result.count("successfully uninstalled")
    assert uninstalled_app == 1


#------------ Test Cases

def test_install_cozy_ubuntu_14_04():
    """
    Test installation of cozy on ubuntu 14.04
    """
    box = 'chef/ubuntu-14.04'
    folder = 'ubuntu_14.04'
    _test_install(folder, box)


def test_install_cozy_ubuntu_12_04():
    """
    Test installation of cozy on ubuntu 12.04
    """
    box = 'hashicorp/precise64'
    folder = 'ubuntu_12.04'
    _test_install(folder, box)


def test_install_cozy_debian_6():
    """
    Test installation of cozy on debian 6
    """
    box = 'chef/debian-6.0.8'
    folder = 'debian_6'
    _test_install(folder, box)


def test_install_cozy_debian_7():
    """
    Test installation of cozy on debian 7
    """
    box = 'chef/debian-7.4'
    folder = 'debian_7'
    _test_install(folder, box)
