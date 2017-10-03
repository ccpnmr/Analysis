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
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
import sys
from PyQt5 import QtGui, QtWidgets

def inverseGrey(colour):

  r, g, b, a = colour.getRgb()

  m = (11*r + 16*g + 5*b)/32

  if (m > 192) or (m < 64):
    m = 255-m
  elif m<128:
    m += 128
  elif m<192:
    m -= 128

  return QtGui.QColor(m, m, m)


class ColourDialog(QtGui.QColorDialog):

  def __init__(self, parent=None, doAlpha=False, **kw):

    QtGui.QColorDialog.__init__(self, parent)

    self.setOption(self.ShowAlphaChannel, doAlpha)
    self.setOption(QtGui.QColorDialog.DontUseNativeDialog,  True)
    self.aborted = False
    self.rejected.connect(self.quit)


  def set(self, colour):

    self.setColour(colour)


  def getColor(self, initialColour=None):

    if initialColour is not None:
      self.setColor(initialColour)

    self.exec_()

    colour = self.currentColor()

    if self.aborted:
      return None
    else:
      return colour

  def setColour(self, colour):
    # colour can be name, #hex, (r,g,b) or (r,g,b,a)

    if isinstance(colour, (list, tuple)) and colour:

      if isinstance(colour[0], float):
        colour = [int(255*c) for c in colour]

      qColour = QtGui.QColor(*colour)
      colour = colour.upper()

    elif isinstance(colour, QtGui.QColor):
      qColour = QtGui.QColor(colour)

    elif colour[0] == '#':
      if isinstance(colour[0], float):
        colour = [int(255*c) for c in colour]

      qColour = QtGui.QColor(*colour)
      colour = colour.upper()

      if len(colour) == 9:
        r = int(colour[1:3], 16)
        g = int(colour[3:5], 16)
        b = int(colour[5:7], 16)
        a = int(colour[7:9], 16)
        colour = (r, g, b, a)

      else:
        r = int(colour[1:3], 16)
        g = int(colour[3:5], 16)
        b = int(colour[5:7], 16)
        colour = (r, g, b)

      qColour = QtGui.QColor(*colour)

    self.setCurrentColor(qColour)

  def quit(self):

    self.aborted = True

