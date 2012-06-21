## Tests

To run tests you need to install dependencies first:

    pip install -r requirements.txt

Then run tests with :

    cd test/
    lettuce

Because tests suscribe to cozy, you should not run them on your final
installation. If you need to run test several time, run fabric reset_account
command before each test.

