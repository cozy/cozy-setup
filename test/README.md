## Tests

Test Cozy setup on the currently supported platforms in Vagrant virtual machines.

To run the tests you need :
- `Vagrant` (version >= 1.5)
- `pytest` (disponible via pip: `pip install pytest`)

Once these requirements are fullfilled, simply change into the `test` directory and run `py.test`:

it will run the four tests, downloading vagrant boxes if necessary (It may take some time on the first run).
