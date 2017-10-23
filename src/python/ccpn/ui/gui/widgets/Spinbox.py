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
__dateModified__ = "$dateModified: 2017-07-07 16:32:56 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"

#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Label import Label

class Spinbox(QtGui.QSpinBox, Base):

  def __init__(self, parent, prefix=None, value=None,step=None, min=None, max=None, showButtons=True, **kw):

    QtGui.QSpinBox.__init__(self, parent)
    if min is not None:
      self.setMinimum(min)
    if max is not None:
      self.setMaximum(max)
    if value is not None: #set Value only after you set min and max
      self.setValue(value)
    if step is not None:
      self.setSingleStep(step)
    if prefix:
      self.setPrefix(prefix+' ')


    Base.__init__(self, **kw)

    if showButtons is False:
      self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)


if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.popups.Dialog import CcpnDialog

  app = TestApplication()
  popup = CcpnDialog()
  sb = Spinbox(popup, step=10, grid=(0,0))
  sb.setPrefix('H Weight ')

  popup.show()
  popup.raise_()

  app.start()

