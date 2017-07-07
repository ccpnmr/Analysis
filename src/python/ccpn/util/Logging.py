"""CCPN logger handling

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:06 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Wayne Boucher $"

__date__ = "$Date: 2017-03-17 12:22:34 +0000 (Fri, March 17, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
"""Logger and message handler"""


import datetime
import functools
import logging
import os
import time

DEBUG1 = logging.DEBUG  # = 10
DEBUG2 = 9
DEBUG3 = 8

defaultLogLevel = logging.INFO
# defaultLogLevel = logging.DEBUG

# this code assumes we only have one project open at a time
# when a new logger is created the handlers for the old one are closed

# note that cannot do logger = getLogger() at top of a module because it almost certainly
# will not be what one wants. instead one has to do it at runtime, e.g. in a constructor
# inside a class or in a non-class function

# in general the application should call createLogger() before anyone calls getLogger()
# but getLogger() can be called first for "short term", "setup" or "testing" use; it then returns
# the default logger

MAX_LOG_FILE_DAYS = 7

logger = None

#DEFAULT_LOGGER_NAME = 'defaultLogger'
defaultLogger = logging.getLogger('defaultLogger')
defaultLogger.propagate = False

def getLogger():

  global logger, defaultLogger

  if not logger:
    return defaultLogger

  return logger

def _debug2(logger, msg, *args, **kwargs):
  logger.log(DEBUG2, msg, *args, **kwargs)

def _debug3(logger, msg, *args, **kwargs):
  logger.log(DEBUG3, msg, *args, **kwargs)

def createLogger(loggerName, memopsRoot, stream=None, level=None, mode='a',
                 removeOldLogsDays=MAX_LOG_FILE_DAYS):
  """Return a (unique) logger for this memopsRoot and with given programName, if any.
     Puts log output into a log file but also optionally can have output go to
     another, specified, stream (e.g. a console)
  """

  global logger

  assert mode in ('a', 'w'), 'for now mode must be "a" or "w"'

  #TODO: remove Api calls
  from ccpnmodel.ccpncore.lib.Io import Api as apiIo
  repositoryPath = apiIo.getRepositoryPath(memopsRoot, 'userData')
  logDirectory = os.path.join(repositoryPath, 'logs')

  today = datetime.date.today()
  fileName = 'log_%s_%02d%02d%02d.txt' % (loggerName, today.year, today.month, today.day)

  logPath = os.path.join(logDirectory, fileName)

  if os.path.exists(logDirectory):
    if os.path.exists(logPath) and os.path.isdir(logPath):
      raise Exception('log file "%s" is a directory' % logPath)
  else:
    os.makedirs(logDirectory)

  _removeOldLogFiles(logPath, removeOldLogsDays)

  if logger:
    # there seems no way to close the logger itself
    # and just closing the handler does not work
    # (and certainly do not want to close stdout or stderr)
    for handler in logger.handlers:
      logger.removeHandler(handler)
  else:
    logger = logging.getLogger(loggerName)
    logger.propagate = False

  logger.logPath = logPath  # just for convenience
  logger.shutdown = logging.shutdown  # just for convenience but tricky

  if level is None:
    level = defaultLogLevel

  logger.setLevel(level)

  handler = logging.FileHandler(logPath, mode=mode)
  _setupHandler(handler, level)

  if stream:
    handler = logging.StreamHandler(stream)
    _setupHandler(handler, level)

  logger.debug1 = logger.debug
  logger.debug2 = functools.partial(_debug2, logger)
  logger.debug3 = functools.partial(_debug3, logger)

  logging.addLevelName(DEBUG2, 'DEBUG2')
  logging.addLevelName(DEBUG3, 'DEBUG3')

  return logger

def _setupHandler(handler, level):
  """Add a stream handler for this logger."""

  # handler = logging.StreamHandler(stream)
  handler.setLevel(level)

  #format = '%(levelname)s: %(module)s:%(funcName)s:%(asctime)s:%(message)s'
  format = '%(levelname)-7s: %(module)s.%(funcName)s : %(message)s'
  formatter = logging.Formatter(format)
  handler.setFormatter(formatter)

  logger.addHandler(handler)

# def _addStreamHandler(logger, stream, level=logging.WARNING):
#   """Add a stream handler for this logger."""
#
#   handler = logging.StreamHandler(stream)
#   handler.setLevel(level)
#
#   format = '%(levelname)s:%(module)s:%(funcName)s:%(asctime)s:%(message)s'
#   formatter = logging.Formatter(format)
#   handler.setFormatter(formatter)
#
#   logger.addHandler(handler)

def _removeOldLogFiles(logPath, removeOldLogsDays=MAX_LOG_FILE_DAYS):
  """Remove old log files."""

  logDirectory = os.path.dirname(logPath)
  logFiles = [os.path.join(logDirectory, x) for x in os.listdir(logDirectory)]
  logFiles = [logFile for logFile in logFiles if logFile != logPath and not os.path.isdir(logFile)]

  currentTime = time.time()
  removeTime = currentTime - removeOldLogsDays * 24 * 3600
  for logFile in logFiles:
    # print ('### checking', logFile)
    mtime = os.path.getmtime(logFile)
    if mtime < removeTime:
      os.remove(logFile)

def setLevel(logger, level=logging.INFO):
  """Set the logger level (including for the handlers)"""

  logger.setLevel(level)
  for handler in logger.handlers:
    handler.setLevel(level)
    
