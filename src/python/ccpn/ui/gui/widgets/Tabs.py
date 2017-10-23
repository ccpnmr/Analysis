"""

Basic Usage:
  Example of a popup with 1 tab:
  
  tabWidget = Tabs(self, grid=(0,0), gridSpan=(1,3))
  
  ## create a frame. This will be the container with all the widgets that will go in the first tab
  
  tab1Frame = Frame(self, setLayout=True)
  
  ## add all the children to the frame
  
  label = Label(tab1Frame, "Example tab 1", grid=(0, 0))
  
  ## add the frame to the TabsWidget to activate as a new tab
  
  tabWidget.addTab(tab1Frame, 'Tab1')
  
  
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:56 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


from PyQt5 import QtGui, QtWidgets
from ccpn.ui.gui.widgets.Base import Base


class Tabs(QtGui.QTabWidget, Base):
  def __init__(self, parent,  **kw):
    QtGui.QTabWidget.__init__(self, parent)
    Base.__init__(self, **kw)




if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.Frame import Frame
  from ccpn.ui.gui.widgets.Label import Label
  from ccpn.ui.gui.popups.Dialog import CcpnDialog

  app = TestApplication()
  popup = CcpnDialog()

  tabWidget = Tabs(popup, grid=(0, 0), gridSpan=(1, 3))

  tab1Frame = Frame(popup, setLayout=True)
  for i in range(5):
    Label(tab1Frame, "Example tab 1", grid=(i, 0))

  tabWidget.addTab(tab1Frame, 'Tab1')

  tab2Frame = Frame(popup, setLayout=True)
  for i in range(5):
    Label(tab2Frame, "Example tab 2", grid=(i, 0))
  tabWidget.addTab(tab2Frame, 'Tab2')

  popup.show()
  popup.raise_()

  app.start()

