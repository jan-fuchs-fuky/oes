OES
===

Examples import.py
------------------

Import night 2017-05-18 from remote computer:
```
$ ./import.py -y 2017 -m 5 -d 18 -r astronomer@example.edu
```

Import nights 2017-05 from remote computer:
```
$ ./import.py -y 2017 -m 5 -r astronomer@example.edu
```

Import nights 2017 from remote computer:
```
$ ./import.py -y 2017 -r astronomer@example.edu
```

Examples add_jd.py
------------------

Add JD to all \*.fit in INPUT_DIR:
```
$ ./add_jd.py -i /path/to/fits
```

License
-------

GNU General Public License version 3 or later.
