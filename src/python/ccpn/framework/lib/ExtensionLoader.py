#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:37 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-30 13:44:57 +0000 (Sun, April 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from ccpn.util.SubclassLoader import loadSubclasses



def getPipes(userExtensionPath=None):
  from ccpn.framework.PathsAndUrls import pipePath
  from ccpn.framework.lib.Pipe import Pipe

  loadedPipes = set()
  loadedPipes.update(loadSubclasses(pipePath, Pipe))
  if userExtensionPath is not None:
    sc = loadSubclasses(userExtensionPath, Pipe)
    loadedPipes.update(sc)
  return loadedPipes


def getPlugins(userPluginPath=None):
  from ccpn.framework.PathsAndUrls import pluginPath
  from ccpn.framework.lib.Plugin import Plugin

  loadedPlugins = set()
  loadedPlugins.update(loadSubclasses(pluginPath, Plugin))
  if userPluginPath is not None:
    sc = loadSubclasses(userPluginPath, Plugin)
    loadedPlugins.update(sc)
  return loadedPlugins
