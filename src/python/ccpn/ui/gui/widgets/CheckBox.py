"""
CheckBox widget

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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.LineEdit import LineEdit

class CheckBox(QtWidgets.QCheckBox, Base):

  def __init__(self, parent=None, checked=False, text='', callback=None, **kw):

    QtWidgets.QCheckBox.__init__(self, parent)
    self.setChecked(checked)
    if text:
      self.setText(text)
    Base.__init__(self, **kw)
    if callback:
      self.setCallback(callback)

  def get(self):
    return self.isChecked()

  def set(self, checked):
    self.setChecked(checked)

  def setCallback(self, callback):
    # self.connect(self, QtCore.SIGNAL('clicked()'), callback)
    self.clicked.connect(callback)



class EditableCheckBox(QtWidgets.QWidget, Base):
  def __init__(self,parent, text=None, checked=False, callback=None,  **kw):
    QtWidgets.QWidget.__init__(self, parent)
    Base.__init__(self, setLayout=True, **kw)


    self.checkBox = CheckBox(self, checked=checked, grid=(0, 0), hAlign='c', )
    self.lineEdit = LineEdit(self, text=text,  grid=(0, 1), hAlign='c', )
    if callback:
      self.checkBox.setCallback(callback)

  def text(self):
    return self.lineEdit.text()

  def setText(self, value):
    self.lineEdit.setText(value)

  def isChecked(self):
    return self.checkBox.isChecked()

  def setChecked(self, value):
    return self.checkBox.setChecked(value)

if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.popups.Dialog import CcpnDialog

  app = TestApplication()

  def callback():
    print('callback')

  popup = CcpnDialog(setLayout=True)

  checkBox1 = EditableCheckBox(parent=popup, text="test", callback=callback, grid=(0, 0)
                      )
  popup.show()
  popup.raise_()
  app.start()
