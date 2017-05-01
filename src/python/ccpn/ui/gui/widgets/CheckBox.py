"""
CheckBox widget

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
__author__ = "$Author: CCPN $"
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:40:42 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"

#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.widgets.Base import Base

class CheckBox(QtGui.QCheckBox, Base):

  def __init__(self, parent=None, checked=False, text='', callback=None, **kw):

    QtGui.QCheckBox.__init__(self, parent)
    self.setChecked(checked)
    if text:
      self.setText(text)
    Base.__init__(self, **kw)
    if callback:
      self.setCallback(callback)

  def get(self):
    return self.isChecked()

  def setCallback(self, callback):
    self.connect(self, QtCore.SIGNAL('clicked()'), callback)


if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.BasePopup import BasePopup

  app = TestApplication()

  def callback():
    print('callback')

  popup = BasePopup(title='Test CheckBox')

  checkBox1 = CheckBox(parent=popup, text="test", callback=callback, grid=(0, 0)
                      )
  app.start()
