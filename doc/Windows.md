#Running on Windows
The tool now also works experimentally on windows (1 known bug)

##Requirements: (tested with python3.6.1-amd64)
- install python3 with tk and pip enabled (from the python website), also enable the "put python in PATH variable" option
- download and install numpy+mkl, scikit-learn and scipy from http://www.lfd.uci.edu/~gohlke/pythonlibs/
  - run <pre>pip install %path-to-numpy.whl%</pre> in an administrator console
  - do the same for scipy and scikit-learn (in this order)
- run <pre>pip install matplotlib pandas</pre> from an administrator console
now all dependencies should be installed (other ways should be possible, but we haven't tested them yet, such as,
eg. installing another python distribution with scipy natively supported

##Running visana:
run <pre>prototype\start.bat</pre> from the project directory.


## Known Bugs:
- when pressing "calculate" on the left side mutiple windows are opened
  - Workaround: close these additional windows
  - no fix planned.