## Tests

Setup Cozy in a Vagrant virtual machine (we assume you have a box named 
"test\_box" available):

    vagrant init test_box
    # uncomment network line in your vagrant file
            
    fab -f test_install.py start_box
    fab -f test_install.py install_cozy
    fab -f test_install.py test_status -H vagrant@192.168.33.10
    fab -f test_install.py test_register -H vagrant@192.168.33.10
    fab -f test_install.py test_install_app -H vagrant@192.168.33.10

Because tests suscribe to cozy, you should not run them on your final
installation. 
