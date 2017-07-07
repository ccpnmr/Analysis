"""Module Documentation here

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
__dateModified__ = "$dateModified: 2017-04-07 11:40:42 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.widgets.Base import Base

class BasePopup(QtGui.QWidget, Base):

  def __init__(self, parent=None, title='', location=None, hide=False,
               modal=False, closeFunc=None, tipText=None, **kw):

    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    
    self.closeFunc = closeFunc
    
    if modal: # Set before visible
      self.setWindowModality(QtCore.Qt.ApplicationModal)
    
    if tipText:
      self.setToolTip(tipText)

    parent = self.parent()
    if parent and not location:
      x = parent.x() + 50
      y = parent.y() + 50
      
      rect = self.rect()
      w = rect.width()
      h = rect.height()
      
      location = (x, y, w, h)
      
    if location:
      self.show()  # TBD: is this needed?
      # self.setGeometry(*location)

    self.setWindowTitle(title)

    self.body(self)

    if hide:
      self.hide()
    else:
      self.show()
      self.raise_()
      
  # overrides QWidget
  def closeEvent(self, event):
  
    if self.closeFunc:
      self.closeFunc()
    
    QtGui.QWidget.closeEvent(self, event)
 
  def open(self):

    self.showNormal()
    self.raise_()
    self.activateWindow()
  
  # def setSize(self, w, h):
  #
  #   self.setGeometry(self.x(), self.y(), w, h)
  #
  # def setGeometry(self, x, y, w=None, h=None):
  #
  #   # this resizes / moves popup if it doesn't fit on screen
  #   # not sure if we need this functionality but leave for now
  #
  #   if w is None:
  #     w = self.rect().width()
  #
  #   if h is None:
  #     h = self.rect().width()
  #
  #   screenRect = QtGui.QApplication.desktop()
  #
  #   sWidth = screenRect.width()
  #   sHeight = screenRect.height()
  #
  #   w = min(sWidth, w)
  #   h = min(sHeight, h)
  #
  #   if (x+w) > sWidth:
  #     if w == 1:
  #       x = sWidth // 2
  #     else:
  #       x = sWidth - w
  #   elif x < 0:
  #     x = 0
  #
  #   if (y+h) > sHeight:
  #     if h == 1:
  #       y = sHeight // 2
  #     else:
  #       y = sHeight - h
  #   elif y < 0:
  #     y = 0
  #
  #   QtGui.QWidget.setGeometry(self, x, y, w, h)

  def body(self, master):
    
    pass # this method can be overridden in subclass

if __name__ == '__main__':

  from ccpn.ui.gui.widgets.Button import Button
  from ccpn.ui.gui.widgets.Label import Label
  from ccpn.ui.gui.widgets.Application import TestApplication
  
  app = TestApplication()

  class TestPopup(BasePopup):

    def __init__(self, parent=None):

      BasePopup.__init__(self, parent, 'Test Popup', modal=False, setLayout=True)

      self.setGeometry(600, 400, 50, 50)
      
      label = Label(self, text='label 1', grid=(0,0))
      label = Label(self, text='label 2', grid=(1,0))
      button = Button(self, text='close', callback=self.close, grid=(3,0))

  popup = None
  window = QtGui.QWidget()
  layout = QtGui.QGridLayout()
  window.setLayout(layout)

  def new():

    global popup
    popup = TestPopup()
    popup.show()

  def lift():

    if popup:
      popup.raise_()

  def close():

    if popup:
      popup.hide()

  def open_():

    if popup:
      popup.open()

  button = Button(window, text='new popup', grid=(0,0), callback=new)

  button = Button(window, text='lift popup',grid=(1,0), callback=lift)

  button = Button(window, text='open popup',grid=(2,0), callback=open_)

  button = Button(window, text='close popup',grid=(3,0), callback=close)

  button = Button(window, text='quit',grid=(4,0), callback=app.quit)

  window.show()
  window.raise_()
  
  app.start()


