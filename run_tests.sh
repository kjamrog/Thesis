printf 'Element tests:\n\n'
nosetests --verbosity=2 tests/element.py

printf '\n\n'

printf 'Utils tests:\n\n'
nosetests --verbosity=2 tests/utils.py