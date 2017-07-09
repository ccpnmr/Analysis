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
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import unittest
import os

from ccpn.framework.lib.ExtensionLoader import getPlugins
from ccpn.util.Path import getPythonDirectory

# class TestExtensionLoader(unittest.TestCase):
#
#   def setUp(self):
#     self.testExtensionPath = os.path.join(getPythonDirectory(), 'ccpn', 'framework', 'testing')
#
#
#   def test(self):
#     extensions = getExtensions(self.testExtensionPath)
#     for e in extensions:
#       self.assertTrue(hasattr(e, 'METHODNAME'))
#       self.assertTrue(hasattr(e, 'runMethod'))
#       print(e().__class__)

class TestPluginLoader(unittest.TestCase):

  def test(self):
    Plugins = getPlugins()
    for Plugin in Plugins:
      plugin = Plugin()
      plugin.run()
