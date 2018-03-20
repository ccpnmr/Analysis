"""
Module Documentation here
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:48 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore
from ccpn.ui.gui.widgets.MessageDialog import MessageDialog
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PulldownList import PulldownList

from ccpn.util.Colour import spectrumColours, addNewColourString
from ccpn.ui.gui.popups.Dialog import CcpnDialog      # ejb
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.util.Logging import getLogger

# def _getColour(peakList, peakListViews, attr):
#
#   if peakListViews:
#     colour = getattr(peakListViews[0], attr)
#   else:
#     colour = getattr(peakList, attr)
#
#   if not colour:
#     colour = peakList.spectrum.positiveContourColour
#
#   return colour

# FIXME   Notifiers are not triggered correctly when changing colours.
# TODO
# Make it working for all the display and not for the one currently opened.
# Add apply, cancel button.
# 1D.

class PeakListPropertiesPopup(CcpnDialog):
  def __init__(self, parent=None, mainWindow=None, peakList=None, title='Peak List Properties', **kw):
    CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

    self.mainWindow = mainWindow
    self.application = mainWindow.application
    self.project = mainWindow.application.project
    self.current = mainWindow.application.current
    self.peakList = peakList

    if not self.peakList:
      MessageDialog.showWarning(title, 'No PeakList Found')
      self.close()

    else:
      self.peakListViews = [peakListView for peakListView in peakList.project.peakListViews if peakListView.peakList == peakList]

      # NOTE: below is not sorted in any way, but if we change that, we also have to change loop in _fillColourPulldown
      spectrumColourKeys = list(spectrumColours.keys())
      if not self.peakList.symbolColour:
        self.peakList.symbolColour = spectrumColourKeys[0]  # default
      if not self.peakList.textColour:
        self.peakList.textColour = spectrumColourKeys[1]   # default*

      self.peakListLabel = Label(self, "PeakList Name ", grid=(0, 0))
      self.peakListLabel = Label(self, peakList.id, grid=(0, 1))

      # does nothing.
      # self.symbolLabel = Label(self, 'Peak Symbol', grid=(2, 0))
      # self.symbolPulldown = PulldownList(self, grid=(2, 1))
      # self.symbolPulldown.setData(['x'])
      self.symbolColourLabel = Label(self, 'Peak Symbol Colour', grid=(3, 0))
      self.symbolColourPulldownList = PulldownList(self, grid=(3, 1))
      self._fillColourPulldown(self.symbolColourPulldownList)
      # FIXME BROKEN .index(peakList.symbolColour) is not in list

      c = peakList.symbolColour
      if c in spectrumColourKeys:
        self.symbolColourPulldownList.setCurrentIndex(spectrumColourKeys.index(c))
      else:
        # FIXME
        # self.symbolColourPulldownList.setCurrentIndex(spectrumColourKeys[0])
        addNewColourString(c)
        self._fillColourPulldown(self.symbolColourPulldownList)

      self.symbolColourPulldownList.activated.connect(self._applyChanges)

      self.textColourLabel = Label(self, 'Peak Text Colour', grid=(4, 0))
      self.textColourPulldownList = PulldownList(self, grid=(4, 1))
      self._fillColourPulldown(self.textColourPulldownList)
      # FIXME BROKEN .index(peakList.symbolColour) is not in list

      c = peakList.textColour
      if c in spectrumColourKeys:
        self.textColourPulldownList.setCurrentIndex(spectrumColourKeys.index(c))
      else:
        # FIXME
        # self.textColourPulldownList.setCurrentIndex(spectrumColourKeys[0])
        addNewColourString(c)
        self._fillColourPulldown(self.symbolColourPulldownList)
        self._fillColourPulldown(self.textColourPulldownList)

      # self.textColourPulldownList.setCurrentIndex(spectrumColourKeys.index(peakList.textColour))
      self.textColourPulldownList.activated.connect(self._applyChanges)

      self.closeButton = Button(self, text='Close', grid=(6, 1), callback=self._accept)
      ## Broken.
      # self.minimalAnnotationLabel = Label(self, 'Minimal Annotation', grid=(5, 0))
      # self.minimalAnnotationCheckBox = CheckBox(self, grid=(5, 1))

      ## Broken. If you close and reopen a display, it doesn't care about the checkbox.
      # self.displayedLabel = Label(self, 'Is displayed', grid=(1, 0))
      # self.displayedCheckBox = CheckBox(self, grid=(1, 1))
      # if(any([peakListView.isVisible() for peakListView in self.peakListViews])):
      #   self.displayedCheckBox.setChecked(True)
      #
      # for peakListView in self.peakListViews:
      #   self.displayedCheckBox.toggled.connect(peakListView.setVisible)

    self.numUndos = 0

  def _setNewColour(self, colList, newCol):
    pix = QtGui.QPixmap(QtCore.QSize(20, 20))
    pix.fill(QtGui.QColor(newCol))
    # add the new colour to the spectrumColours dict
    newIndex = str(len(spectrumColours.items()) + 1)
    # spectrumColours[newColour.name()] = 'Colour %s' % newIndex
    addNewColourString(newCol)
    if newCol not in colList.texts:
      colList.addItem(icon=QtGui.QIcon(pix), text='Colour %s' % newIndex)
      colList.setCurrentIndex(int(newIndex) - 1)

  def _changeSymbolColour(self, value):
    self.project._undo.increaseBlocking()     # prevent more undo points
    colour = list(spectrumColours.keys())[value]
    self.peakList.symbolColour = colour
    self.project._undo.decreaseBlocking()

  def _changeTextColour(self, value):
    self.project._undo.increaseBlocking()     # prevent more undo points
    colour = list(spectrumColours.keys())[value]
    self.peakList.textColour = colour
    self.project._undo.decreaseBlocking()

  def _changeColours(self):
    value = self.symbolColourPulldownList.index
    colour = list(spectrumColours.keys())[value]
    self.peakList.symbolColour = colour

    value = self.textColourPulldownList.index
    colour = list(spectrumColours.keys())[value]
    self.peakList.textColour = colour

  def _fillColourPulldown(self, pulldown):
    pulldown.clear()
    for item in spectrumColours.items():
      if item[0] != '#':
        pix=QtGui.QPixmap(QtCore.QSize(20, 20))
        pix.fill(QtGui.QColor(item[0]))
        pulldown.addItem(icon=QtGui.QIcon(pix), text=item[1])
      else:
        pulldown.addItem(text=item[1])

  def _applyChanges(self):
    """
    The apply button has been clicked
    Define an undo block for setting the properties of the object
    If there is an error setting any values then generate an error message
      If anything has been added to the undo queue then remove it with application.undo()
      repopulate the popup widgets
    """
    while self.numUndos > 0:      # remove any previous undo from this popup
      # self.application.undo()     # so only the last colour change is kept
      self.project._undo.undo()     # this doesn't popup the undo progressManager
      self.numUndos -= 1

    applyAccept = False
    oldUndo = self.project._undo.numItems()

    from ccpn.util.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=self)

    self.project._startCommandEchoBlock('_applyChanges', quiet=True)
    try:
      self._changeColours()

      # repaint
      GLSignals.emitEvent(targets=[self.peakList], triggers=[GLNotifier.GLPEAKLISTS,
                                                             GLNotifier.GLPEAKLISTLABELS])

      applyAccept = True
    except Exception as es:
      showWarning(str(self.windowTitle()), str(es))
    finally:
      self.project._endCommandEchoBlock()

    if applyAccept is False:
      # should only undo if something new has been added to the undo deque
      # may cause a problem as some things may be set with the same values
      # and still be added to the change list, so only undo if length has changed
      errorName = str(self.__class__.__name__)
      if oldUndo != self.project._undo.numItems():
        self.project._undo.undo()
        getLogger().debug('>>>Undo.%s._applychanges' % errorName)
      else:
        getLogger().debug('>>>Undo.%s._applychanges nothing to remove' % errorName)

      return False
    else:
      self.numUndos += 1
      return True

  def _okButton(self):
    if self._applyChanges() is True:
      self._accept()

  def _accept(self):
    self.symbolColourPulldownList.activated.disconnect(self._applyChanges)
    self.textColourPulldownList.activated.disconnect(self._applyChanges)
    self.accept()
