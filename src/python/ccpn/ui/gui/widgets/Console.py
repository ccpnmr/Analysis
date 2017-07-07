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
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:52 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
import pyqtgraph.console as console
from PyQt4 import QtGui

class Console(console.ConsoleWidget):
  def __init__(self, parent=None, namespace=None, historyFile=None):
    console.ConsoleWidget.__init__(self, parent, namespace)
    # self.console.addAction()
    self.runMacroButton = QtGui.QPushButton()
    # self.console.ui.runMacroButton.setCheckable(True)
    self.runMacroButton.setText('Run Macro')
    self.ui.horizontalLayout.addWidget(self.runMacroButton)
  #
  #
  def runMacro(self):
    print('runMacro')
    # macroFile = QtGui.QFileDialog.getOpenFileName(self, "Run Macro")
    # print(macroFile)

