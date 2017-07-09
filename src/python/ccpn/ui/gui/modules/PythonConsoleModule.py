"""Module Documentation here

"""
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
__modifiedBy__ = "$modifiedBy: Luca $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:46 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: Luca $"
__date__ = "$Date: 2017-05-10 16:04:41 +0000 (Wed, May 10, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


from ccpn.ui.gui.modules.CcpnModule import CcpnModule


class PythonConsoleModule(CcpnModule):
  '''
  This class implements the module by wrapping a PeakListTable instance
  '''

  includeSettingsWidget = False
  maxSettingsState = 2
  settingsPosition = 'top'

  className = 'PythonConsoleModule'

  def __init__(self, mainWindow, name='Python Console', closeFunc=None, **kwds):
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name, closeFunc=closeFunc)

    self.mainWindow = mainWindow
    self.pythonConsoleWidget = self.mainWindow.pythonConsole

    self.mainWidget.getLayout().addWidget(self.pythonConsoleWidget)

    self.pythonConsoleWidget._startChannels()



