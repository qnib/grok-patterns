=====
Install
=====
python
--------

In order to run the script you need to install docopt and envoy and simplejson
One could use pip, <pkg-manager> easy_install or plein git repos:

Clone the following...
```
 git clone https://github.com/simplejson/simplejson
 git clone https://github.com/kennethreitz/envoy
 git clone https://github.com/docopt/docopt
... and execute the installer within the repositories:
 python setup.py install
```

--------
Usage
--------

Within the directory 'patterns' are standard grok patterns.

```
GRAPHITE_METRIC [a-z0-9A-F\.\-]*
```

Tests are located in 'tests' and contain ConfigParser style test definitions:

```
[singlular_metric]
comp_line=%{GRAPHITE_METRIC:val1}
input=metric
result={"GRAPHITE_METRIC:val1":["metric"]}
```

- comp_line defines the GROK pattern to apply.
- input sets the input line to parse
- result will be compared against the json result returned by the grok-parsing
