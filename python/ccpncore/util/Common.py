"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = "$Revision: 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================
"""Common utilities

NB Must conform to PYthon 2.1. Imported in ObjectDomain.
"""

__author__ = 'rhf22'

import os
import sys
import json

from ccpncore.util import Path
from ccpncore.memops.metamodel import Constants as metaConstants

# valid characters for file names
# NB string.ascii_letters and string.digits are not compatible
# with Python 2.1 (used in ObjectDomain)
defaultFileNameChar = '_'
separatorFileNameChar = '+'
validFileNamePartChars = ('abcdefghijklmnopqrstuvwxyz'
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                          + defaultFileNameChar)
validCcpnFileNameChars  = validFileNamePartChars + '-.' + separatorFileNameChar

apiTopModule = 'ccpncore.api'


def getClassFromFullName(qualifiedName):
  """ Get Api class from fully qualified (dot-separated) name
  """
  pathList = qualifiedName.split('.')
  mod = __import__('.'.join([apiTopModule] + pathList[:-1]),{},{},[pathList[-1]])
  return getattr(mod,pathList[-1])


def convertStringToFileName(fileNameString, validChars=validCcpnFileNameChars,
                            defaultChar=defaultFileNameChar):

  ll = [x for x in fileNameString]
  for ii,char in enumerate(ll):
    if char not in validChars:
      ll[ii] = defaultChar
  #
  return ''.join(ll)

def getCcpFileString(fileNameString):
  """
  Changes an input string to the one used for a component of file names.
  """

  return convertStringToFileName(fileNameString, validFileNamePartChars,
                                   defaultFileNameChar)

def incrementName(name:str) -> str:
  """Add '_1' to name or change suffix '_n' to '_(n+1) """
  ll = name.rsplit('_',1)
  if len(ll) == 2:
    try:
      ll[1] = int(ll[1]) + 1
      return '_'.join(ll)

    except ValueError:
      pass

  return name + '_1'


def splitIntFromChars(value:str):
  """convert a string with a leading integer optionally followed by characters
  into an (integer,string) tuple"""

  value = value.strip()

  for ii in reversed(range(1,len(value)+1)):
    try:
      number = int(value[:ii])
      chars = value[ii:]
      break
    except ValueError:
      continue
  else:
    number = None
    chars = value

  return number,chars

def recursiveImport(dirname, modname=None, ignoreModules = None, force=False):
  """ recursively import all .py files
  (not starting with '__' and not containing internal '.' in their name)
  from directory dirname and all its subdirectories, provided they
  contain '__init__.py'
  Serves to check that files compile without error

  modname is the module name (dot-separated) corresponding to the directory
  dirName.
  If modname is None, dirname must be on the pythonPath

  Note that there are potential problems if the files we want are not
  the ones encountered first on the pythonPath
  """

  listdir = os.listdir(dirname)
  try:
    listdir.remove('__init__.py')
  except ValueError:
    if not force:
      return

  files = []

  if ignoreModules is None:
    ignoreModules = []

  if modname is None:
    prefix = ''
  else:
    prefix = modname + '.'

  listdir2 = []
  for name in listdir:
    head,ext = os.path.splitext(name)
    if (prefix + head) in ignoreModules:
      pass
    elif ext == '.py' and head.find('.') == -1:
      files.append(head)
    else:
      listdir2.append(name)

  # import directory and underlying directories
  if modname:
    # Note that files is never empty, so module is lowest level not toplevel
    for ff in files:
      try:
        __import__(modname, {}, {}, [ff])
      except:
        print("WARNING, Import failed for %s.%s" % (modname,ff))

  for name in listdir2:
    newdirname = Path.joinPath(dirname,name)
    if os.path.isdir(newdirname) and name.find('.') == -1:
      recursiveImport(newdirname, prefix + name,ignoreModules)


def getConfigParameter(name):
  """get configuration parameter, from reading configuration file
  """

  file = Path.joinPath(Path.getTopDirectory(),metaConstants.configFilePath)
  dd = json.load(open(file))
  return dd[
    'configuration'].get(name)


def isWindowsOS():

  return sys.platform[:3].lower() == 'win'