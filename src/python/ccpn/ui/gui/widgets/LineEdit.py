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
__author__ = "$Author: simon $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.framework.Translation import translator

TextAligment = {
                'c': QtCore.Qt.AlignHCenter,
                'l': QtCore.Qt.AlignLeft,
                'r': QtCore.Qt.AlignRight
                }

class LineEdit(QtGui.QLineEdit, Base):

  def __init__(self, parent, text='', textAligment='c', minimumWidth=100, textColor=None, **kw):

    #text = translator.translate(text)

    QtGui.QLineEdit.__init__(self, text, parent)
    Base.__init__(self, **kw)

    if textColor:
      self.setStyleSheet('QLabel {color: %s;}' % textColor)

    self.setAlignment(TextAligment[textAligment])
    self.setMinimumWidth(minimumWidth)
    self.setFixedHeight(25)

  def get(self):

    return self.text()

  def set(self, text=''):

    #text = translator.translate(text)
    self.setText(text)

class FloatLineEdit(LineEdit):

  def get(self):

    result = LineEdit.get(self)
    if result:
      return float(result)
    else:
      return None

  def set(self, text=''):

    LineEdit.set(str(text))
