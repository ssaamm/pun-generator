=============
Pun Generator
=============

Trying to score fake internet points on Reddit? Want to make everyone groan with
your bad puns? Need a new Instagram handle? We've got just the thing for you!

Type in a word and see what puns you get!

Running it
----------

.. code:: bash

    virtualenv -p python3.5 env
    . env/bin/activate
    pip3 install -r requirements.txt

    mkdir data
    cd util
    python build_db.py

    cd ..
    python app.py
