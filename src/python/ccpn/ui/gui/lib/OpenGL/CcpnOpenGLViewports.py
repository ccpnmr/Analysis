"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = ""
__credits__ = ""
__licence__ = ("")
__reference__ = ("")
#=========================================================================================
# Last code modification:
#=========================================================================================
__modifiedBy__ = "$modifiedBy$"
__dateModified__ = "$dateModified$"
__version__ = "$Revision$"
#=========================================================================================
# Created:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
try:
  from OpenGL import GL, GLU, GLUT
except ImportError:
  app = QtWidgets.QApplication(sys.argv)
  QtWidgets.QMessageBox.critical(None, "OpenGL hellogl",
          "PyOpenGL must be installed to run this example.")
  sys.exit(1)


class GLViewports(object):
  # Class to handle the different viewports in the display
  def __init__(self, pixelRatio):
    # define a new empty list
    self._views = {}
    self._devicePixelRatio = pixelRatio

  def addViewport(self, name, parent, left, bottom, rightOffset, topOffset):
    # add a new viewport
    # parent points to the containing widget
    # left, bottom - coordinates of bottom-left corner
    # rightOffset   - offset from the right border
    # topOffset     - offset from the top border
    self._views[name] = (parent, left, bottom, rightOffset, topOffset)

    # e.g., GL.glViewport(0, 35, w-35, h-35)   # leave a 35 width margin for the axes - bottom/right
    #                      0, 35, -35, 0

  def setViewport(self, name):
    # change to the named viewport
    def setVal(offsetType, w, h, leftOffset):
      if offsetType[1] in 'alb':
        return offsetType[0]
      elif offsetType[1] == 'w':
        return w+offsetType[0]-leftOffset
      elif offsetType[1] == 'h':
        return h+offsetType[0]

    if name in self._views:
      thisView = self._views[name]
      w=thisView[0].width()
      h=thisView[0].height()
      l = setVal(thisView[1], w, h, 0)
      b = setVal(thisView[2], w, h, 0)
      wi = setVal(thisView[3], w, h, l)
      he = setVal(thisView[4], w, h, 0)

      GL.glViewport(int(l * self._devicePixelRatio),
                    int((b-1) * self._devicePixelRatio),
                    int(wi * self._devicePixelRatio),
                    int(he * self._devicePixelRatio))
                    # , w-thisView[3]-thisView[1], h-thisView[4]-thisView[2])
    else:
      raise RuntimeError('Error: viewport %s does not exist' % name)

  def getViewport(self, name):
    # change to the named viewport
    def setVal(offsetType, w, h, leftOffset):
      if offsetType[1] in 'alb':
        return offsetType[0]
      elif offsetType[1] == 'w':
        return w+offsetType[0]-leftOffset
      elif offsetType[1] == 'h':
        return h+offsetType[0]

    if name in self._views:
      thisView = self._views[name]
      w=thisView[0].width()
      h=thisView[0].height()
      l = setVal(thisView[1], w, h, 0)
      b = setVal(thisView[2], w, h, 0)
      wi = setVal(thisView[3], w, h, l)
      he = setVal(thisView[4], w, h, 0)

      return (l, b, wi, he)
                    # , w-thisView[3]-thisView[1], h-thisView[4]-thisView[2])
    else:
      raise RuntimeError('Error: viewport %s does not exist' % name)