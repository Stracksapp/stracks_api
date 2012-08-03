import logging

##
## re-use standard logging levels. This way the logging levels will
## map to ours directly
CRITICAL = logging.CRITICAL
FATAL = CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

##
## Add an extra logginglevel for intercepted crashes/exceptions
EXCEPTION = 100

