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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtCore, QtGui, QtWidgets

from ccpn.ui.gui.widgets.Menu import Menu
from ccpn.ui.gui.widgets.ToolBar import ToolBar
from functools import partial
from ccpn.core.lib.Notifiers import Notifier
from collections import OrderedDict
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.ui._implementation.PeakListView import  PeakListView
from ccpn.ui._implementation.IntegralListView import  IntegralListView
from ccpn.ui._implementation.MultipletListView import  MultipletListView

class SpectrumToolBar(ToolBar):

  def __init__(self, parent=None, widget=None, **kwds):

    ToolBar.__init__(self, parent=parent, **kwds)
    self.widget = widget
    self.parent = parent
    self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    self.eventFilter = self._eventFilter
    self.installEventFilter(self)
    self.setMouseTracking(True)

  def _paintButtonToMove(self, button):
    pixmap = button.grab()  # makes a "ghost" of the button as we drag
    # below makes the pixmap half transparent
    painter = QtGui.QPainter(pixmap)
    painter.setCompositionMode(painter.CompositionMode_DestinationIn)
    painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
    painter.end()
    return pixmap


  def _updateSpectrumViews(self, newIndex):
    newSpectrumViewsOrder = []

    for action in self.actions():
      spectrumView = self.widget.project.getByPid(action.spectrumViewPid)
      newSpectrumViewsOrder.append(spectrumView)

    # self.widget.project.blankNotification()
    # newIndex = [newIndex.index(ii) for ii in self.widget.getOrderedSpectrumViewsIndex()]
    newIndex = [self.widget.getOrderedSpectrumViewsIndex()[ii] for ii in newIndex]
    self.widget.setOrderedSpectrumViewsIndex(newIndex)
    # self.widget.project.unblankNotification()

    # defaults = OrderedDict((('newIndex', None),))
    #
    # self.widget._startCommandEchoBlock('indexOrderedSpectrumViews', values=locals(), defaults=defaults)
    # self.widget.project.blankNotification()
    # try:
    #   for strip in self.widget.strips:
    #     # strip.setOrderedSpectrumViews(newSpectrumViewsOrder)
    #     strip._indexOrderedSpectrumViews(newIndex)
    #
    # finally:
    #   self.widget.project.unblankNotification()
    #   self.widget._endCommandEchoBlock()

    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=None)
    GLSignals.emitPaintEvent()


  def _createContextMenu(self, button:QtWidgets.QToolButton):
    """
    Creates a context menu containing a command to delete the spectrum from the display and its
    button from the toolbar.
    """
    if not button:
      return None
    contextMenu = Menu('', self, isFloatWidget=True)
    viewObjs = [PeakListView, IntegralListView, MultipletListView]
    for viewObj in viewObjs:
      title = viewObj._pluralLinkName
      smenu =  contextMenu.addMenu(title)
      views = getattr(self.widget, title)
      smenu.setEnabled(len(views) > 0)
      smenu.addAction('Show All', partial(self._setVisibleAllFromList, True, smenu, views))
      smenu.addAction('Hide All', partial(self._setVisibleAllFromList, False, smenu, views))
      smenu.addSeparator()
      for view in views:
        ccpnObj = view._childClass
        if ccpnObj:
          action = smenu.addAction(ccpnObj.pid)
          action.setCheckable(True)
          if view.isVisible():
            action.setChecked(True)
          action.toggled.connect(view.setVisible)
          action.toggled.connect(partial(self._updateGl, view._parent))

    contextMenu.addSeparator()
    contextMenu.addAction('Remove Spectrum', partial(self._removeSpectrum, button))
    return contextMenu


  # old to be deleted
  # def _createContextMenuOld(self, button:QtWidgets.QToolButton):
  #   """
  #   Creates a context menu containing a command to delete the spectrum from the display and its
  #   button from the toolbar.
  #   """
  #   if not button:
  #     return None
  #   contextMenu = Menu('', self, isFloatWidget=True)
  #   plMenu =  contextMenu.addMenu('PeakList')
  #   ilMenu =  contextMenu.addMenu('IntegralList')
  #   mlMenu =  contextMenu.addMenu('MultipletList')
  #
  #   peakListViews = self.widget.peakListViews
  #   integralListViews = self.widget.integralListViews
  #   multipletListViews = self.widget.multipletListViews
  #
  #   action = button.actions()[0]
  #   # keys = [key for key, value in self.widget.spectrumActionDict.items() if value is action]
  #   # if not keys: # if you click on >> button which shows more spectra
  #   #   return None
  #   # key = keys[0]
  #
  #   plMenu.setEnabled(len(peakListViews)>0)
  #   plMenu.addAction('Show All', partial(self._setVisibleAllFromList,True, plMenu, peakListViews))
  #   plMenu.addAction('Hide All', partial(self._setVisibleAllFromList,False, plMenu, peakListViews))
  #   plMenu.addSeparator()
  #   for peakListView in peakListViews:
  #     # if peakListView.spectrumView._apiDataSource == key:
  #       if peakListView.peakList:
  #         action = plMenu.addAction(peakListView.peakList.pid)
  #         action.setCheckable(True)
  #         if peakListView.isVisible():
  #           action.setChecked(True)
  #         # else:
  #         #   allPlAction.setChecked(False)
  #         action.toggled.connect(peakListView.setVisible)
  #         # TODO:ED check this is okay for each spectrum
  #         action.toggled.connect(partial(self._updateVisiblePeakLists, peakListView.spectrumView))
  #
  #
  #   ilMenu.setEnabled(len(integralListViews)>0)
  #   ilMenu.addAction('Show All', partial(self._setVisibleAllFromList,True, ilMenu, integralListViews))
  #   ilMenu.addAction('Hide All', partial(self._setVisibleAllFromList,False, ilMenu, integralListViews))
  #   ilMenu.addSeparator()
  #   for integralListView in integralListViews:
  #     # if integralListView.spectrumView._apiDataSource == key:
  #       if integralListView.integralList:
  #         action = ilMenu.addAction(integralListView.integralList.pid)
  #         action.setCheckable(True)
  #         if integralListView.isVisible():
  #           action.setChecked(True)
  #         # else:
  #         #   allPlAction.setChecked(False)
  #         action.toggled.connect(integralListView.setVisible)
  #
  #         # TODO:ED check this is okay for each spectrum
  #         action.toggled.connect(partial(self._updateVisibleIntegralLists, integralListView.spectrumView))
  #
  #   mlMenu.setEnabled(len(multipletListViews)>0)
  #   mlMenu.addAction('Show All', partial(self._setVisibleAllFromList,True, mlMenu, multipletListViews))
  #   mlMenu.addAction('Hide All', partial(self._setVisibleAllFromList,False, mlMenu, multipletListViews))
  #   mlMenu.addSeparator()
  #   for multipletListView in multipletListViews:
  #     # if multipletListView.spectrumView._apiDataSource == key:
  #       if multipletListView.multipletList:
  #         action = mlMenu.addAction(multipletListView.multipletList.pid)
  #         action.setCheckable(True)
  #         if multipletListView.isVisible():
  #           action.setChecked(True)
  #         # else:
  #         #   allPlAction.setChecked(False)
  #         action.toggled.connect(multipletListView.setVisible)
  #
  #         # TODO:ED check this is okay for each spectrum
  #         action.toggled.connect(partial(self._updateVisibleMultipletLists, multipletListView.spectrumView))
  #
  #   contextMenu.addSeparator()
  #   contextMenu.addAction('Remove Spectrum', partial(self._removeSpectrum, button))
  #   return contextMenu

  def _updateGl(self):
    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=self)
    GLSignals.emitPaintEvent()


  # Triplicated Code?
  # def _updateVisiblePeakLists(self, spectrumView=None, visible=True):
  #   from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
  #   GLSignals = GLNotifier(parent=self)
  #   GLSignals.emitPaintEvent()
  #
  # def _updateVisibleIntegralLists(self, spectrumView=None, visible=True):
  #   from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
  #   GLSignals = GLNotifier(parent=self)
  #   GLSignals.emitPaintEvent()
  #
  # def _updateVisibleMultipletLists(self, spectrumView=None, visible=True):
  #   from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
  #   GLSignals = GLNotifier(parent=self)
  #   GLSignals.emitPaintEvent()

  def _getSpectrumViewFromButton(self, button):
    spvs = []
    key = [key for key, value in self.widget.spectrumActionDict.items() if value == button.actions()[0]][0]

    for spectrumView in self.widget.spectrumViews:
      if spectrumView._apiDataSource == key:
        spvs.append(spectrumView)
    if len(spvs) == 1:
      return spvs[0]


  # def _allPeakLists(self, contextMenu, button):
  #   key = [key for key, value in self.widget.spectrumActionDict.items() if value == button.actions()[0]][0]
  #   for peakListView in self.widget.peakListViews:
  #     if peakListView.spectrumView._apiDataSource == key:
  #       for action in contextMenu.actions():
  #         if action is not self.sender():
  #           if not action.isChecked():
  #             action.setChecked(True)
  #             action.toggled.connect(peakListView.setVisible)
  #   self._updateVisiblePeakLists()
  #
  # def _noPeakLists(self, contextMenu, button):
  #   key = [key for key, value in self.widget.spectrumActionDict.items() if value == button.actions()[0]][0]
  #   for peakListView in self.widget.peakListViews:
  #     if peakListView.spectrumView._apiDataSource == key:
  #       for action in contextMenu.actions():
  #         if action is not self.sender():
  #           if action.isChecked():
  #             action.setChecked(False)
  #             action.toggled.connect(peakListView.setVisible)
  #   self._updateVisiblePeakLists()

  def _setVisibleAllFromList(self,abool, menu, views):
    '''
    
    :param abool: T or F
    :param menu: 
    :param views: any of Views obj _pluralLinkName
    :return: 
    '''
    if views:
      for view in views:
        view.setVisible(abool)
        for action in menu.actions():
          if action.text() == view.pid:
            action.setChecked(abool)


  def _removeSpectrum(self, button:QtWidgets.QToolButton):
    """
    Removes the spectrum from the display and its button from the toolbar.
    """
    # TODO:ED this needs patching in to the spectrumView.delete()
    # remove the item from the toolbar
    self.removeAction(button.actions()[0])

    # and delete the spectrumView from the V2
    key = [key for key, value in self.widget.spectrumActionDict.items() if value == button.actions()[0]][0]
    stripUpdateList = []
    for spectrumView in self.widget.spectrumViews:
      if spectrumView._apiDataSource == key:
        index = self.widget.spectrumViews.index(spectrumView)
        break
    else:
      showWarning('Spectrum not found in toolbar')
      return

    # found value is spectrumView, index

    spectrumView.delete()
    # self.widget.removeOrderedSpectrumView(index)

    # spawn a redraw of the GL windows
    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=None)
    GLSignals.emitPaintEvent()


  def _dragButton(self, event):

    toolButton = self.childAt(event.pos())
    self._buttonBeingDragged = toolButton
    allActionsTexts = []

    if toolButton:
      pixmap = self._paintButtonToMove(toolButton)

      mimeData = QtCore.QMimeData()
      mimeData.setText('%d,%d' % (event.x(), event.y()))
      drag = QtGui.QDrag(self)
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)
      # start the drag operation

      allActionsTexts = [action.text() for action in self.actions()]
      if drag.exec_(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:

        point = QtGui.QCursor.pos()
        droppedPoint = self.mapFromGlobal(point)
        nextButton = self.childAt(droppedPoint)
        x, y = droppedPoint.x(), droppedPoint.y(),
        if not nextButton:
          nextButton = self.childAt(QtCore.QPoint(30 + x, y))
        if nextButton:
          if nextButton == toolButton:
            return
          # allActionsTexts = [action.text() for action in self.actions()]
          if allActionsTexts.index(toolButton.text()) > allActionsTexts.index(nextButton.text()):
            self.insertAction(nextButton.actions()[0], toolButton.actions()[0])
          else:
            self.insertAction(toolButton.actions()[0],nextButton.actions()[0])

        else:
          # Dropping outside
          self.insertAction(toolButton.actions()[0], toolButton.actions()[0])
      else:
        event.ignore()

      actionIndex = [allActionsTexts.index(act.text()) for act in self.actions() if act.text() in allActionsTexts]
      self._updateSpectrumViews(actionIndex)
      for action in self.actions():
        self._setSizes(action)

  def _eventFilter(self, obj, event):
    """
    Replace all the events with a single filter process

    """

    if event.type() == QtCore.QEvent.MouseButtonPress:
      # if event.button() == QtCore.Qt.LeftButton: Can't make it working!!!

      if event.button() == QtCore.Qt.RightButton:
        toolButton = self.childAt(event.pos())

        menu = self._createContextMenu(toolButton)
        if menu:
          menu.move(event.globalPos().x(), event.globalPos().y() + 10)
          menu.exec()
      if event.button() == QtCore.Qt.MiddleButton:
        self._dragButton(event)


    return super(SpectrumToolBar, self).eventFilter(obj,event)    # do the rest


  def _addSpectrumViewToolButtons(self, spectrumView):

    spectrumDisplay = spectrumView.strip.spectrumDisplay
    spectrum = spectrumView.spectrum
    apiDataSource = spectrum._wrappedData
    action = spectrumDisplay.spectrumActionDict.get(apiDataSource)
    if not action:
      # add toolbar action (button)
      spectrumName = spectrum.name
      if len(spectrumName) > 12:
        spectrumName = spectrumName[:12]+'.....'

      actionList = self.actions()
      try:
        # try and find the spectrumView in the orderedlist - for undo function
        oldList = spectrumDisplay.spectrumViews
        oldList = spectrumDisplay.orderedSpectrumViews(oldList)
        if spectrumView in oldList:
          oldIndex = oldList.index(spectrumView)
        else:
          oldIndex = len(oldList)

        if actionList and oldIndex < len(actionList):
          nextAction = actionList[oldIndex]

          # create a new action and move it to the correct place in the list
          action = self.addAction(spectrumName)
          self.insertAction(nextAction, action)
        else:
          action = self.addAction(spectrumName)

      except Exception as es:
        action = self.addAction(spectrumName)


      action.setCheckable(True)
      action.setChecked(True)
      action.setToolTip(spectrum.name)
      widget = self.widgetForAction(action)
      widget.setIconSize(QtCore.QSize(120, 10))
      self._setSizes(action)
      # WHY _wrappedData and not spectrumView?
      widget.spectrumView = spectrumView._wrappedData
      action.spectrumViewPid = spectrumView.pid

      spectrumDisplay.spectrumActionDict[apiDataSource] = action
      # The following call sets the icon colours:
      spectrumView._spectrumViewHasChanged()

    if spectrumDisplay.is1D:
      action.toggled.connect(spectrumView.plot.setVisible)
    action.toggled.connect(spectrumView.setVisible)


  def _setSizes(self, action):

    widget = self.widgetForAction(action)
    widget.setIconSize(QtCore.QSize(120, 10))
    widget.setFixedSize(75, 30)

  def _toolbarChange(self, spectrumViews):
    actionList = self.actions()
    # self.clear()
    for specView in spectrumViews:

      # self._addSpectrumViewToolButtons(specView)
      spectrum = specView.spectrum
      spectrumName = spectrum.name
      if len(spectrumName) > 12:
        spectrumName = spectrumName[:12] + '.....'

      for act in actionList:
        if act.text() == spectrumName:
          self.addAction(act)

          widget = self.widgetForAction(act)
          widget.setIconSize(QtCore.QSize(120, 10))
          self._setSizes(act)
    self.update()