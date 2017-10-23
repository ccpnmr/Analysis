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
__dateModified__ = "$dateModified: 2017-07-07 16:32:54 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: Geerten Vuister $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from PyQt5 import QtGui, QtWidgets, QtCore
Qt = QtCore.Qt

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.guiSettings import getColours
from ccpn.framework.Translation import translator

class Label(QtWidgets.QLabel, Base):

  _styleSheet = """
  QLabel {
    font-size: %spt;
    font-weight: %s;
    color: %s;
    margin-left: %dpx;
    margin-top: %dpx;
    margin-right: %dpx;
    margin-bottom: %dpx;
    border: 0px;
  }
  """

  def __init__(self, parent=None, text='', textColour=None, textSize=12, bold=False,
               margins=[2, 1, 2, 1], **kwds):

    text = translator.translate(text)
    QtWidgets.QLabel.__init__(self, text, parent)
    Base.__init__(self, **kwds)

    # if textColor:
    #   self.setStyleSheet('QLabel {color: %s}' % textColor)
    # if textSize and textColor:
    #   self.setStyleSheet('QLabel {font-size: %s; color: %s;}' % (textSize, textColor))
    # if bold:
    #   self.setStyleSheet('QLabel {font-weight: bold;}')

    self._textSize = textSize
    self._bold = 'bold' if bold else 'normal'
    self._margins = margins

    # this appears not to pick up the colour as set by the stylesheet!
    # self._colour = textColor if textColor else self.palette().color(QtGui.QPalette.WindowText).name()

    colours = getColours()
    self._colour = textColour if textColour else colours['LabelFG']
    self._setStyleSheet()

  def get(self):
    "get the label text"
    return self.text()

  def set(self, text=''):
    "set label text, applying translator"
    text = translator.translate(text)
    self.setText(text)

  def _setStyleSheet(self):
    self.setStyleSheet(self._styleSheet % (
      self._textSize,
      self._bold,
      self._colour,
      self._margins[0],
      self._margins[1],
      self._margins[2],
      self._margins[3],
      )
    )


if __name__ == '__main__':

  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.Button import Button

  msg = 'Hello world'
  count = 0

  def func():
    global count
    count += 1
    label.set(msg + ' ' + str(count))
    print(label.get())

  app = TestApplication()
  
  window = QtWidgets.QWidget()
 
  label = Label(window, text=msg, textColor='red', grid=(0,0))
  button = Button(window, text='Click me', callback=func, grid=(0,1))

  window.show()

  app.start()
