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
__modifiedBy__ = "$modifiedBy: Wayne Boucher $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:44 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import typing

import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

from ccpn.core.Peak import Peak
from ccpn.core.PeakList import PeakList
from ccpn.core.Project import Project
from ccpn.core.lib.Notifiers import Notifier

from ccpn.ui.gui.guiSettings import getColours, GUISTRIP_PIVOT
from ccpn.ui.gui.guiSettings import textFontSmall
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.PlotWidget import PlotWidget
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import FloatLineEdit
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.widgets.PlaneToolbar import _StripLabel
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.lib.GuiNotifier import GuiNotifier
from ccpn.ui.gui.widgets.DropBase import DropBase
# from ccpn.ui.gui.widgets.Icon import Icon
# from ccpn.ui.gui.widgets.Menu import Menu
from ccpn.ui.gui import guiSettings

from ccpn.util import Ticks
from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import Ruler as ApiRuler

from ccpn.util.Logging import getLogger


class GuiStrip(Frame):

  def __init__(self, spectrumDisplay, useOpenGL=False):
    """
    Basic strip class; used in StripNd and Strip1d

    :param spectrumDisplay: spectrumDisplay instance

    This module inherits attributes from the Strip wrapper class:
    Use clone() method to make a copy
    """

    # For now, cannot set spectrumDisplay attribute as it is owned by the wrapper class
    # self.spectrumDisplay = spectrumDisplay
    self.mainWindow = self.spectrumDisplay.mainWindow
    self.application = self.mainWindow.application
    self.current = self.application.current

    getLogger().debug('GuiStrip>>> spectrumDisplay: %s' % self.spectrumDisplay)
    Frame.__init__(self, parent=spectrumDisplay.stripFrame, setLayout=True, showBorder=False,
                   acceptDrops=True, hPolicy='expanding', vPolicy='expanding' ##'minimal'
                   )

    # it appears to be required to explicitly set these, otherwise
    # the Widget will not fill all available space
    ###self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    # The strip is responsive on restore to the contentMargins set here
    #self.setContentsMargins(5, 0, 5, 0)
    self.setContentsMargins(0, 0, 0, 0)
    self.setMinimumWidth(50)
    self.setMinimumHeight(150)

    self.plotWidget = PlotWidget(self, useOpenGL=useOpenGL)
    #showDoubleCrosshair = self.application.preferences.general.doubleCrossHair)
    self.plotWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
    # GWV: plotWidget appears not to be responsive to contentsMargins
    self.plotWidget.setContentsMargins(10, 30, 10, 30)
    self.getLayout().addWidget(self.plotWidget, 1, 0)
    self.layout().setHorizontalSpacing(0)
    self.layout().setVerticalSpacing(0)
    # self.plotWidget.showGrid(x=True, y=True, alpha=None)

    self._useCcpnGL = True
    # TODO: ED comment out the block below to return to normal
    if self._useCcpnGL:
      self.plotWidget.hide()

      if spectrumDisplay.is1D:
        from ccpn.ui.gui.widgets.GLWidgets import Gui1dWidget as CcpnGLWidget
      else:
        from ccpn.ui.gui.widgets.GLWidgets import GuiNdWidget as CcpnGLWidget

      self._CcpnGLWidget = CcpnGLWidget(parent=self, mainWindow=self.mainWindow)
      self.getLayout().addWidget(self._CcpnGLWidget, 1, 0)    # (3,0) if not hiding plotWidget
      self._CcpnGLWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding
                                               , QtWidgets.QSizePolicy.Expanding)

      # set the ID label in the new widget
      self._CcpnGLWidget.setStripID('.'.join(self.id.split('.')))
      self._CcpnGLWidget.gridVisible = self.application.preferences.general.showGrid

    # self.plotWidgetOverlay = pg.PlotWidget(self, useOpenGL=useOpenGL)  #    make a copy
    # self.plotWidgetOverlay.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    # self.plotWidgetOverlay.resize(200, 200)
    # self.plotWidgetOverlay.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    # self.plotWidgetOverlay.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
    # self.plotWidgetOverlay.showGrid(x=True, y=True, alpha=None)

    # Widgets for toolbar; items will be added by GuiStripNd (eg. the Z/A-plane boxes)
    # and GuiStrip1d; will be hidden for 2D's by GuiSpectrumView
    self._stripToolBarWidget = Widget(parent=self, setLayout=True,
                                      hPolicy='expanding',
                                      grid=(2, 0), spacing=(5,5))

    # Widgets for _stripIdLabel and _stripLabel
    self._labelWidget = Widget(parent=self, setLayout=True,
                               # hPolicy='expanding', vAlign='center',
                               grid=(0, 0), spacing=(0,0))
    # self._labelWidget.layout().setHorizontalSpacing(0)
    # self._labelWidget.layout().setVerticalSpacing(0)
    self._labelWidget.setFixedHeight(16)

    # display and pid
    #TODO:GEERTEN correct once pid has been reviewed
    # self._stripIdLabel = Label(parent=self._labelWidget,
    #                            text='.'.join(self.id.split('.')), margins=[0,0,0,0], spacing=(0,0),
    #                            grid=(0,0), gridSpan=(1,1), hAlign='left', vAlign='top', hPolicy='minimum')
    # self._stripIdLabel.setFont(textFontSmall)
    # TODO:ED check - have moved the label to the top-left corner
    self.plotWidget.stripIDLabel.setText('.'.join(self.id.split('.')))


    # Displays a draggable label for the strip
    #TODO:GEERTEN reinsert a notifier for update in case this displays a nmrResidue
    self._stripLabel = _StripLabel(parent=self._labelWidget,
                                   text='', spacing=(0,0),
                                   grid=(0,0), gridSpan=(1,3))    #, hAlign='left', vAlign='top', hPolicy='minimum')

    self._stripLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    self._stripLabel.setFont(textFontSmall)

    # Strip needs access to plotWidget's items and info #TODO: get rid of this
    self.plotItem = self.plotWidget.plotItem
    self.viewBox = self.plotItem.vb

    self._showCrossHair()
    # callbacks
    ###self.plotWidget.scene().sigMouseMoved.connect(self._mouseMoved)
    self.plotWidget.scene().sigMouseMoved.connect(self._showMousePosition)    # update mouse cursors
    self.storedZooms = []

    self.beingUpdated = False
    self.xPreviousRegion, self.yPreviousRegion = self.viewBox.viewRange()

    # need to keep track of mouse position because Qt shortcuts don't provide
    # the widget or the position of where the cursor is
    self.axisPositionDict = {}  # axisCode --> position

    self._initRulers()

    self.hPhasingPivot = pg.InfiniteLine(angle=90, movable=True)
    self.hPhasingPivot.setVisible(False)
    self.plotWidget.addItem(self.hPhasingPivot)
    self.hPhasingPivot.sigPositionChanged.connect(lambda phasingPivot: self._movedPivot())
    self.haveSetHPhasingPivot = False

    self.vPhasingPivot = pg.InfiniteLine(angle=0, movable=True)
    self.vPhasingPivot.setVisible(False)
    self.plotWidget.addItem(self.vPhasingPivot)
    self.vPhasingPivot.sigPositionChanged.connect(lambda phasingPivot: self._movedPivot())
    self.haveSetVPhasingPivot = False

    # notifier for highlighting the strip
    self._stripNotifier = Notifier(self.current, [Notifier.CURRENT], 'strip', self._highlightCurrentStrip)
    # Notifier for updating the peaks
    self._peakNotifier = Notifier(self.project, [Notifier.CREATE,
                                                 Notifier.DELETE,
                                                 Notifier.CHANGE], 'Peak', self._updateDisplayedPeaks,
                                  onceOnly=True)

    self._integralNotifier = Notifier(self.project, [Notifier.CREATE,
                                                 Notifier.DELETE,
                                                 Notifier.CHANGE], 'Integral', self._updateDisplayedIntegrals,
                                  onceOnly=True)

    # Notifier for change of stripLabel
    self._stripLabelNotifier = Notifier(self.project, [Notifier.RENAME], 'NmrResidue', self._updateStripLabel)
    #self._stripNotifier.setDebug(True)
    #self._peakNotifier.setDebug(True)

    # For now, all dropevents are not strip specific, use spectrumDisplay's
    # handling
    self._droppedNotifier = GuiNotifier(self,
                                        [GuiNotifier.DROPEVENT], [DropBase.URLS, DropBase.PIDS],
                                        self.spectrumDisplay._processDroppedItems)
    self.moveEventNotifier = GuiNotifier(self,
                                       [GuiNotifier.DRAGMOVEEVENT], [DropBase.URLS, DropBase.PIDS],
                                       self.spectrumDisplay._processDragEnterEvent)

    # set peakLabelling to the default from preferences or strip to the left
    if len(spectrumDisplay.strips) > 1:
      self.peakLabelling = spectrumDisplay.strips[0].peakLabelling
      self.peakSymbolType = spectrumDisplay.strips[0].peakSymbolType
      self.peakSymbolSize = spectrumDisplay.strips[0].peakSymbolSize
      self.peakSymbolThickness = spectrumDisplay.strips[0].peakSymbolThickness
      self.gridVisible = spectrumDisplay.strips[0].gridVisible
      self.crosshairVisible = spectrumDisplay.strips[0].crosshairVisible

      try:
        self._CcpnGLWidget._axisLocked = spectrumDisplay.strips[0]._CcpnGLWidget._axisLocked

        # self._CcpnGLWidget._updateHTrace = spectrumDisplay.strips[0]._CcpnGLWidget._updateHTrace
        # self._CcpnGLWidget._updateVTrace = spectrumDisplay.strips[0]._CcpnGLWidget._updateVTrace
        # self.hTraceAction.setChecked(self._CcpnGLWidget._updateHTrace)
        # self.vTraceAction.setChecked(self._CcpnGLWidget._updateVTrace)

      except Exception as es:
        getLogger().debug('OpenGL widget not instantiated')
    else:
      self.peakLabelling = self.application.preferences.general.annotationType
      self.peakSymbolType = self.application.preferences.general.peakSymbolType
      self.peakSymbolSize = self.application.preferences.general.peakSymbolSize
      self.peakSymbolThickness = self.application.preferences.general.peakSymbolThickness
      self.gridVisible = self.application.preferences.general.showGrid
      self.crosshairVisible = self.application.preferences.general.showCrosshair

    self.plotWidget.grid.setVisible(self.application.preferences.general.showGrid)

    self._storedPhasingData = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

    try:
      self._CcpnGLWidget.gridVisible = self.application.preferences.general.showGrid
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

    # self._stripToolBarWidget.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
    # self._labelWidget.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
    # self._stripLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

    # self.show()

  def viewRange(self):
    return self._CcpnGLWidget.viewRange()

  @property
  def gridIsVisible(self):
    "True if grid is visible"

    try:
      return self._CcpnGLWidget.gridVisible
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

    return self.plotWidget.grid.isVisible()

  @property
  def crossHairIsVisible(self):
    "True if crosshair is visible"

    try:
      return self._CcpnGLWidget.crossHairVisible
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

    return self.plotWidget.crossHair1.isVisible()

  @property
  def pythonConsole(self):
    return self.mainWindow.pythonConsole

  def getStripLabel(self):
    """Return the stripLabel widget"""
    return self._stripLabel

  def setStripLabelText(self, text: str):
    """set the text of the _stripLabel"""
    if text is not None:
      self._stripLabel.setText(text)

  def getStripLabelText(self) -> str:
    """return the text of the _stripLabel"""
    return self._stripLabel.text()

  def showStripLabel(self, doShow: bool=True):
    """show / hide the _stripLabel"""
    self._stripLabel.setVisible(doShow)

  def hideStripLabel(self):
    "Hide the _stripLabel; convienience"
    self._stripLabel.setVisible(False)

  def _updateStripLabel(self, callbackDict):
    "Update the striplabel if it represented a NmrResidue that has changed its id"
    text = self.getStripLabelText()
    if callbackDict['oldPid'] == text:
      self.setStripLabelText(callbackDict['object'].pid)

    try:
      self._CcpnGLWidget.setStripIDString(callbackDict['object'].pid)
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

  def _unregisterStrip(self):
    self._stripNotifier.unRegister()
    self._peakNotifier.unRegister()
    self._stripLabelNotifier.unRegister()
    self._droppedNotifier.unRegister()

  def _updateDisplayedPeaks(self, data):
    "Callback when peaks have changed"
    # self.showPeaks(data['object'].peakList)

    # from ccpn.util.CcpnOpenGL import GLNotifier
    # GLSignals = GLNotifier(parent=self)
    # GLSignals.emitEvent(triggers=[GLNotifier.GLPEAKNOTIFY], targets=data)

    try:
      self._CcpnGLWidget._processPeakNotifier(data)
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

  def _updateDisplayedIntegrals(self, data):
    "Callback when peaks have changed"
    # self.showPeaks(data['object'].peakList)

    # from ccpn.util.CcpnOpenGL import GLNotifier
    # GLSignals = GLNotifier(parent=self)
    # GLSignals.emitEvent(triggers=[GLNotifier.GLPEAKNOTIFY], targets=data)

    try:
      self._CcpnGLWidget._processIntegralNotifier(data)
    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

  def _highlightCurrentStrip(self, data):
    "Callback to highlight the axes of current strip"
    # self.plotWidget.highlightAxes(self is self.current.strip)

    try:
      self._CcpnGLWidget.highlightCurrentStrip(self is self.current.strip)

      # # spawn a redraw of the GL windows
      # from ccpn.util.CcpnOpenGL import GLNotifier
      # GLSignals = GLNotifier(parent=None)
      # GLSignals.emitPaintEvent()

    except Exception as es:
      getLogger().debug('OpenGL widget not instantiated')

  def _printToFile(self, printer):
    # CCPN INTERNAL - called in printToFile method of GuiMainWindow

    for spectrumView in self.spectrumViews:
      spectrumView._printToFile(printer)

    # print box

    # print ticks and grid line
    viewRegion = self.plotWidget.viewRange()
    v1, v0 = viewRegion[0]  # TBD: relies on axes being backwards
    w1, w0 = viewRegion[1]  # TBD: relies on axes being backwards, which is not true in 1D
    xMajorTicks, xMinorTicks, xMajorFormat = Ticks.findTicks((v0, v1))
    yMajorTicks, yMinorTicks, yMajorFormat = Ticks.findTicks((w0, w1))

    xScale = (printer.x1-printer.x0)/(v1-v0)
    xOffset = printer.x0 - xScale*v0
    yScale = (printer.y1-printer.y0)/(w1-w0)
    yOffset = printer.y0 - yScale*w0
    xMajorText = [xMajorFormat % tick for tick in xMajorTicks]
    xMajorTicks = [tick*xScale+xOffset for tick in xMajorTicks]
    xMinorTicks = [tick*xScale+xOffset for tick in xMinorTicks]
    yMajorText = [xMajorFormat % tick for tick in yMajorTicks]
    yMajorTicks = [tick*yScale+yOffset for tick in yMajorTicks]
    yMinorTicks = [tick*yScale+yOffset for tick in yMinorTicks]

    xTickHeight = yTickHeight = max(printer.y1-printer.y0, printer.x1-printer.x0)*0.01

    for tick in xMinorTicks:
      printer.writeLine(tick, printer.y0, tick, printer.y0+0.5*xTickHeight)

    fontsize = 10
    for n, tick in enumerate(xMajorTicks):
      if self.plotWidget.grid.isVisible():
        printer.writeLine(tick, printer.y0, tick, printer.y1, colour='#888888')
      printer.writeLine(tick, printer.y0, tick, printer.y0+xTickHeight)
      text = xMajorText[n]
      printer.writeText(text, tick-0.5*len(text)*fontsize*0.7, printer.y0+xTickHeight+1.5*fontsize)

    # output backwards for y
    for tick in yMinorTicks:
      printer.writeLine(printer.x0, printer.y1-tick, printer.x0+0.5*yTickHeight, printer.y1-tick)

    for n, tick in enumerate(yMajorTicks):
      if self.plotWidget.grid.isVisible():
        printer.writeLine(printer.x0, printer.y1-tick, printer.x1, printer.y1-tick, colour='#888888')
      printer.writeLine(printer.x0, printer.y1-tick, printer.x0+yTickHeight, printer.y1-tick)
      text = yMajorText[n]
      printer.writeText(text, printer.x0+yTickHeight+0.5*fontsize*0.7, printer.y1-tick+0.5*fontsize)

  def _newPhasingTrace(self):

    try:
      self._CcpnGLWidget.newTrace()
    except Exception as es:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

    return



    for spectrumView in self.spectrumViews:
      spectrumView._newPhasingTrace()

  """
  def newHPhasingTrace(self):
    
    for spectrumView in self.spectrumViews:
      spectrumView.newHPhasingTrace(self.mousePosition[1])
      
  def newVPhasingTrace(self):
    
    for spectrumView in self.spectrumViews:
      spectrumView.newVPhasingTrace(self.mousePosition[0])
  """

  def _setPhasingPivot(self):

    phasingFrame = self.spectrumDisplay.phasingFrame
    direction = phasingFrame.getDirection()
    # position = self.current.cursorPosition[0] if direction == 0 else self.current.cursorPosition[1]
    # position = self.current.positions[0] if direction == 0 else self.current.positions[1]

    mouseMovedDict = self.current.mouseMovedDict
    if direction == 0:
      for mm in mouseMovedDict.keys():
        if mm[0] == self.axisCodes[0][0]:
          position = mouseMovedDict[mm]
    else:
      for mm in mouseMovedDict.keys():
        if mm[0] == self.axisCodes[1][0]:
          position = mouseMovedDict[mm]

    phasingFrame.pivotEntry.set(position)
    self._updatePivot()

  def removePhasingTraces(self):

    try:
      self._CcpnGLWidget.clearStaticTraces()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

    return
    for spectrumView in self.spectrumViews:
      spectrumView.removePhasingTraces()

  """
  def togglePhasingPivot(self):
    
    self.hPhasingPivot.setPos(self.mousePosition[0])
    self.hPhasingPivot.setVisible(not self.hPhasingPivot.isVisible())
  """

  def _updatePivot(self): # this is called if pivot entry at bottom of display is updated and then "return" key used

    # update the static traces from the phasing console
    # redraw should update the display
    try:
      self._CcpnGLWidget.rescaleStaticTraces()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)
    return

    phasingFrame = self.spectrumDisplay.phasingFrame
    position = phasingFrame.pivotEntry.get()
    direction = phasingFrame.getDirection()
    if direction == 0:
      self.hPhasingPivot.setPos(position)
    else:
      self.vPhasingPivot.setPos(position)
    self._updatePhasing()

  def _movedPivot(self): # this is called if pivot on screen is dragged

    phasingFrame = self.spectrumDisplay.phasingFrame
    direction = phasingFrame.getDirection()
    if direction == 0:
      position = self.hPhasingPivot.getXPos()
    else:
      position = self.vPhasingPivot.getYPos()

    phasingFrame.pivotEntry.set(position)
    self._updatePhasing()

  def setTraceScale(self, traceScale):
    for spectrumView in self.spectrumViews:
      spectrumView.traceScale = traceScale

  def turnOnPhasing(self):

    phasingFrame = self.spectrumDisplay.phasingFrame
    self.hPhasingPivot.setVisible(True)
    self.vPhasingPivot.setVisible(True)

    # change menu
    self.viewBox.menu = self._phasingMenu

    if self.spectrumDisplay.is1D:

      self._hTraceActive = True
      self._vTraceActive = False
      self._newConsoleDirection = 0
    else:
      # TODO:ED remember trace direction
      self._hTraceActive = self.spectrumDisplay.hTraceAction    # self.hTraceAction.isChecked()
      self._vTraceActive = self.spectrumDisplay.vTraceAction    # self.vTraceAction.isChecked()

      # set to the first active or the remembered phasingDirection
      self._newConsoleDirection = phasingFrame.getDirection()
      if self._hTraceActive:
        self._newConsoleDirection = 0
        phasingFrame.directionList.setIndex(0)
      elif self._vTraceActive:
        self._newConsoleDirection = 1
        phasingFrame.directionList.setIndex(1)

    for spectrumView in self.spectrumViews:
      spectrumView._turnOnPhasing()

    # # make sure that all traces are clear
    # from ccpn.util.CcpnOpenGL import GLNotifier
    # GLSignals = GLNotifier(parent=self)
    # if self.spectrumDisplay.is1D:
    #   GLSignals.emitEvent(triggers=[GLNotifier.GLADD1DPHASING], display=self.spectrumDisplay)
    # else:
    #   GLSignals.emitEvent(triggers=[GLNotifier.GLCLEARPHASING], display=self.spectrumDisplay)

    vals = self.spectrumDisplay.phasingFrame.getValues(self._newConsoleDirection)
    self.spectrumDisplay.phasingFrame.slider0.setValue(vals[0])
    self.spectrumDisplay.phasingFrame.slider1.setValue(vals[1])
    self.spectrumDisplay.phasingFrame.pivotEntry.set(vals[2])

    # TODO:ED remember direction
    self._newPosition = phasingFrame.pivotEntry.get()
    self.pivotLine = self._CcpnGLWidget.addInfiniteLine(colour='highlight', movable=True, lineStyle='dashed')

    if not self.pivotLine:
      getLogger().warning('no infiniteLine')
      return

    if self._newConsoleDirection == 0:
      self.pivotLine.orientation = ('v')

      # TODO:ED don't need as menu will change
      # self.hTraceAction.setChecked(True)
      # self.vTraceAction.setChecked(False)
      if not self.spectrumDisplay.is1D:
        self.hTraceAction.setChecked(True)
        self.vTraceAction.setChecked(False)
        self._CcpnGLWidget.updateHTrace = True
        self._CcpnGLWidget.updateVTrace = False
    else:
      self.pivotLine.orientation = ('h')
      # self.hTraceAction.setChecked(False)
      # self.vTraceAction.setChecked(True)
      if not self.spectrumDisplay.is1D:
        self.hTraceAction.setChecked(False)
        self.vTraceAction.setChecked(True)
        self._CcpnGLWidget.updateHTrace = False
        self._CcpnGLWidget.updateVTrace = True

    self.pivotLine.valuesChanged.connect(self._newPositionLineCallback)
    self.pivotLine.setValue(self._newPosition)
    phasingFrame.pivotEntry.valueChanged.connect(self._newPositionPivotCallback)

    # make sure that all traces are clear
    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=self)
    if self.spectrumDisplay.is1D:
      GLSignals.emitEvent(triggers=[GLNotifier.GLADD1DPHASING], display=self.spectrumDisplay)
    else:
      GLSignals.emitEvent(triggers=[GLNotifier.GLCLEARPHASING], display=self.spectrumDisplay)

  def _newPositionLineCallback(self):
    if not self.isDeleted:
      phasingFrame = self.spectrumDisplay.phasingFrame
      self._newPosition = self.pivotLine.values[0]
      phasingFrame.pivotEntry.setValue(self._newPosition)

  def _newPositionPivotCallback(self, value):
    self._newPosition = value
    self.pivotLine.setValue(value)

  def turnOffPhasing(self):
    phasingFrame = self.spectrumDisplay.phasingFrame

    self.hPhasingPivot.setVisible(False)
    self.vPhasingPivot.setVisible(False)

    # change menu
    self.viewBox.menu = self._defaultMenu

    for spectrumView in self.spectrumViews:
      spectrumView._turnOffPhasing()

    # make sure that all traces are clear
    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
    GLSignals = GLNotifier(parent=self)
    GLSignals.emitEvent(triggers=[GLNotifier.GLCLEARPHASING], display=self.spectrumDisplay)

    self._CcpnGLWidget.removeInfiniteLine(self.pivotLine)
    self.pivotLine.valuesChanged.disconnect(self._newPositionLineCallback)
    phasingFrame.pivotEntry.valueChanged.disconnect(self._newPositionPivotCallback)

    if self.spectrumDisplay.is1D:
      self._CcpnGLWidget.updateHTrace = False
      self._CcpnGLWidget.updateVTrace = False
    else:
      # TODO:ED remember trace direction
      self.hTraceAction.setChecked(False)     #self._hTraceActive)
      self.vTraceAction.setChecked(False)     #self._vTraceActive)
      self._CcpnGLWidget.updateHTrace = False     #self._hTraceActive
      self._CcpnGLWidget.updateVTrace = False     #self._vTraceActive

  def _changedPhasingDirection(self):

    phasingFrame = self.spectrumDisplay.phasingFrame
    direction = phasingFrame.getDirection()

    # phasingFrame.setDirection(1-direction)
    # self.spectrumDisplay._storedPhasingData[1-direction] = [phasingFrame.slider0.value(),
    #                                                         phasingFrame.slider1.value(),
    #                                                         phasingFrame.pivotEntry.get()]

    if not phasingFrame.isVisible():
      return

    if direction == 0:
      self.hPhasingPivot.setVisible(True)
      self.vPhasingPivot.setVisible(False)
      # self.pivotLine.orientation = ('v')
    else:
      self.hPhasingPivot.setVisible(False)
      self.vPhasingPivot.setVisible(True)
      # self.pivotLine.orientation = ('h')

    if direction == 0:
      self.pivotLine.orientation = ('v')
      self.hTraceAction.setChecked(True)
      self.vTraceAction.setChecked(False)
      self._CcpnGLWidget.updateHTrace = True
      self._CcpnGLWidget.updateVTrace = False
    else:
      self.pivotLine.orientation = ('h')
      self.hTraceAction.setChecked(False)
      self.vTraceAction.setChecked(True)
      self._CcpnGLWidget.updateHTrace = False
      self._CcpnGLWidget.updateVTrace = True

    vals = phasingFrame.getValues(direction)
    # phasingFrame.slider0.setValue(self.spectrumDisplay._storedPhasingData[direction][0])
    # phasingFrame.slider1.setValue(self.spectrumDisplay._storedPhasingData[direction][1])
    # phasingFrame.pivotEntry.set(self.spectrumDisplay._storedPhasingData[direction][2])
    phasingFrame.slider0.setValue(vals[0])
    phasingFrame.slider1.setValue(vals[1])
    phasingFrame.pivotEntry.set(vals[2])

    try:
      self._CcpnGLWidget.clearStaticTraces()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

    for spectrumView in self.spectrumViews:
      spectrumView._changedPhasingDirection()

  def _updatePhasing(self):

    # update the static traces from the phasing console
    # redraw should update the display
    try:
      colour = getColours()[GUISTRIP_PIVOT]
      self._CcpnGLWidget.setInfiniteLineColour(self.pivotLine, colour)
      self._CcpnGLWidget.rescaleStaticTraces()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)
    return

    # TODO:GEERTEN: Fix  (not yet picked-up!; why? - ED: old code, return statement above)
    colour = getColours()[GUISTRIP_PIVOT]
    self.hPhasingPivot.setPen({'color': colour})
    self.vPhasingPivot.setPen({'color': colour})
    for spectrumView in self.spectrumViews:
      spectrumView.setPivotColour(colour)
      spectrumView._updatePhasing()
      
  def _updateXRegion(self, viewBox):
    # this is called when the viewBox is changed on the screen via the mouse
    # this code is complicated because need to keep viewBox region and axis region in sync
    # and there can be different viewBoxes with the same axis

    if not self._finaliseDone: return

    assert viewBox is self.viewBox, 'viewBox = %s, self.viewBox = %s' % (viewBox, self.viewBox)

    self._updateX()
    self._updatePhasing()

  def _updateYRegion(self, viewBox):
    # this is called when the viewBox is changed on the screen via the mouse
    # this code is complicated because need to keep viewBox region and axis region in sync
    # and there can be different viewBoxes with the same axis

    if not self._finaliseDone: return

    assert viewBox is self.viewBox, 'viewBox = %s, self.viewBox = %s' % (viewBox, self.viewBox)

    self._updateY()
    self._updatePhasing()

  def _updateX(self):

    def _widthsChangedEnough(r1, r2, tol=1e-5):
      r1 = sorted(r1)
      r2 = sorted(r2)
      minDiff = abs(r1[0] - r2[0])
      maxDiff = abs(r1[1] - r2[1])
      return (minDiff > tol) or (maxDiff > tol)

    if not self._finaliseDone: return

    # this only wants to get the scaling of the modified strip and not the actual values

    xRange = list(self.viewBox.viewRange()[0])
    for strip in self.spectrumDisplay.strips:
      if strip is not self:
        stripXRange = list(strip.viewBox.viewRange()[0])
        if _widthsChangedEnough(stripXRange, xRange):

          # TODO:ED check whether the strip has a range set yet
          diff = (xRange[1]-xRange[0])/2.0
          mid = (stripXRange[1]+stripXRange[0])/2.0
          xRange = (mid-diff, mid+diff)

          strip.viewBox.setXRange(*xRange, padding=0)

  def _updateY(self):

    def _widthsChangedEnough(r1, r2, tol=1e-5):
      r1 = sorted(r1)
      r2 = sorted(r2)
      minDiff = abs(r1[0] - r2[0])
      maxDiff = abs(r1[1] - r2[1])
      return (minDiff > tol) or (maxDiff > tol)

    if not self._finaliseDone: return

    yRange = list(self.viewBox.viewRange()[1])
    for strip in self.spectrumDisplay.strips:
      if strip is not self:
        stripYRange = list(strip.viewBox.viewRange()[1])
        if _widthsChangedEnough(stripYRange, yRange):
          strip.viewBox.setYRange(*yRange, padding=0)

  def _toggleCrossHair(self):
    " Toggles whether crosshair is visible"
    self.plotWidget.crossHair1.toggle()
    if self.spectrumViews and self.spectrumViews[0].spectrum.showDoubleCrosshair:
      self.plotWidget.crossHair2.toggle()

    try:
      self.crosshairVisible = not self.crosshairVisible
      self._CcpnGLWidget.crossHairVisible = self.crosshairVisible
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def _showCrossHair(self):
    "Displays crosshair in strip"
    # self.plotWidget.crossHair1.show()
    # if self.spectrumViews and self.spectrumViews[0].spectrum.showDoubleCrosshair:
    #   self.plotWidget.crossHair2.show()

    try:
      self.crosshairVisible = True
      self._CcpnGLWidget.crossHairVisible = True
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def _hideCrossHair(self):
    "Hides crosshair in strip."
    # self.plotWidget.crossHair1.hide()
    # if self.spectrumViews and self.spectrumViews[0].spectrum.showDoubleCrosshair:
    #   self.plotWidget.crossHair2.hide()

    try:
      self.crosshairVisible = False
      self._CcpnGLWidget.crossHairVisible = False
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def toggleGrid(self):
    "Toggles whether grid is visible in the strip."
    self.plotWidget.toggleGrid()

    try:
      self.gridVisible = not self.gridVisible
      self._CcpnGLWidget.gridVisible = self.gridVisible
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def cyclePeakLabelling(self):
    "Toggles whether peak labelling is minimal is visible in the strip."
    self.peakLabelling += 1
    if self.peakLabelling > 2:
      self.peakLabelling = 0

    if self.spectrumViews:
      for sV in self.spectrumViews:

        for peakListView in sV.peakListViews:
          # peakListView.buildPeakLists = True
          peakListView.buildPeakListLabels = True

      # spawn a redraw of the GL windows
      from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
      GLSignals = GLNotifier(parent=None)
      GLSignals.emitPaintEvent()

  def cyclePeakSymbols(self):
    "Toggles whether peak labelling is minimal is visible in the strip."
    self.peakSymbolType += 1
    if self.peakSymbolType > 2:
      self.peakSymbolType = 0

    if self.spectrumViews:
      for sV in self.spectrumViews:

        for peakListView in sV.peakListViews:
          peakListView.buildPeakLists = True
          # peakListView.buildPeakListLabels = True

      # spawn a redraw of the GL windows
      from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
      GLSignals = GLNotifier(parent=None)
      GLSignals.emitPaintEvent()

      # old code from plotWidget
        # for peakList in sV.spectrum.peakLists:
        #
        #   peakListView = self._findPeakListView(peakList)
        #   if peakListView:
        #     peakListView._changedPeakListView()
        #
        # # new for the OpenGL widget - emit a signal?
        # sV.buildPeakLists = True
        # sV.buildPeakListLabels = True

  def _crosshairCode(self, axisCode):
    # determines what axisCodes are compatible as far as drawing crosshair is concerned
    # TBD: the naive approach below should be improved
    return axisCode #if axisCode[0].isupper() else axisCode

  def _createMarkAtCursorPosition(self):
    # TODO: this creates a mark in all dims, is that what we want??

    if not self._finaliseDone: return

    try:
      # axisPositionDict = self.axisPositionDict
      # axisCodes = [axis.code for axis in self.orderedAxes[:2]]
      # positions = [axisPositionDict[axisCode] for axisCode in axisCodes]
      # self._project.newMark('white', positions, axisCodes) # the 'white' is overridden in PlotWidget._addRulerLine()

      colourDict = guiSettings.MARK_LINE_COLOUR_DICT  # maps atomName --> colour

      positions = [self.current.mouseMovedDict[ax] for ax in self.axisCodes]
      self._project.newMark(colourDict[guiSettings.DEFAULT], positions, self.axisCodes)  # the 'white' is overridden in PlotWidget._addRulerLine()
      # self._project.newMark('#e0e0e0', self.current.cursorPosition[:2], self.axisCodes[:2])  # the 'white' is overridden in PlotWidget._addRulerLine()

    except Exception as es:
      getLogger().warning('Error setting mark at current position')

  # TODO: remove apiRuler (when notifier at bottom of module gets rid of it)
  def _initRulers(self):

    for mark in self._project.marks:
      apiMark = mark._wrappedData
      for apiRuler in apiMark.rulers:
        self.plotWidget._addRulerLine(apiRuler)

  def _showMousePosition(self, pos:QtCore.QPointF):
    """
    Displays mouse position for both axes by axis code.
    """
    if not self._finaliseDone: return

    if self.isDeleted:
      return

    position = self.viewBox.mapSceneToView(pos)
    try:
      # this only calls a single _wrapper function
      if self.orderedAxes[1] and self.orderedAxes[1].code == 'intensity':
        format = "%s: %.3f\n%s: %.4g"
      else:
        format = "%s: %.2f\n%s: %.2f"
    except:
      format = "%s: %.3f  %s: %.4g"

    # self._cursorLabel.setText(format %
    #   (self.axisOrder[0], position.x(), self.axisOrder[1], position.y())
    # )

    self.plotWidget.mouseLabel.setText(format %
                                       (self.axisOrder[0], position.x(), self.axisOrder[1], position.y())
                                       )
    self.plotWidget.mouseLabel.setPos(position.x(), position.y())
    self.plotWidget.mouseLabel.show()

  def zoomToRegion(self, xRegion:typing.Tuple[float, float], yRegion:typing.Tuple[float, float]):
    """
    Zooms strip to the specified region
    """
    if not self._finaliseDone: return
    padding = self.application.preferences.general.stripRegionPadding
    self.viewBox.setXRange(*xRegion, padding=padding)
    self.viewBox.setYRange(*yRegion, padding=padding)

  def zoomX(self, x1:float, x2:float):
    """
    Zooms x axis of strip to the specified region
    """
    if not self._finaliseDone: return

    padding = self.application.preferences.general.stripRegionPadding
    self.viewBox.setXRange(x1, x2, padding=padding)

  def zoomY(self, y1:float, y2:float):
    """
    Zooms y axis of strip to the specified region
    """
    if not self._finaliseDone: return
    padding = self.application.preferences.general.stripRegionPadding
    self.viewBox.setYRange(y1, y2, padding=padding)

  def showZoomPopup(self):
    """
    Creates and displays a popup for zooming to a region in the strip.
    """
    zoomPopup = QtWidgets.QDialog()

    Label(zoomPopup, text='x1', grid=(0, 0))
    x1LineEdit = FloatLineEdit(zoomPopup, grid=(0, 1))
    Label(zoomPopup, text='x2', grid=(0, 2))
    x2LineEdit = FloatLineEdit(zoomPopup, grid=(0, 3))
    Label(zoomPopup, text='y1', grid=(1, 0))
    y1LineEdit = FloatLineEdit(zoomPopup, grid=(1, 1))
    Label(zoomPopup, text='y2', grid=(1, 2))
    y2LineEdit = FloatLineEdit(zoomPopup, grid=(1, 3))

    def _zoomTo():
      x1 = x1LineEdit.get()
      y1 = y1LineEdit.get()
      x2 = x2LineEdit.get()
      y2 = y2LineEdit.get()
      if None in (x1, y1, x2, y2):
        getLogger().warning('Zoom: must specify region completely')
        return
      self.zoomToRegion(xRegion=(x1, x2), yRegion=(y1, y2))
      zoomPopup.close()

    Button(zoomPopup, text='OK', callback=_zoomTo, grid=(2, 0), gridSpan=(1, 2))
    Button(zoomPopup, text='Cancel', callback=zoomPopup.close, grid=(2, 2), gridSpan=(1, 2))

    zoomPopup.exec_()

  # TODO. Set limit range properly for each case: 1D/nD, flipped axis
  # def setZoomLimits(self, xLimits, yLimits, factor=5):
  #   '''
  #
  #   :param xLimits: List [min, max] , e.g ppm [0,15]
  #   :param yLimits:  List [min, max]  eg. intensities [-300,2500]
  #   :param factor:
  #   :return: Limits the viewBox from zooming in too deeply(crashing the program) to zooming out too far.
  #   '''
  #   ratio = (abs(xLimits[0] - xLimits[1])/abs(yLimits[0] - yLimits[1]))/factor
  #   if max(yLimits)>max(xLimits):
  #     self.viewBox.setLimits(xMin=-abs(min(xLimits)) * factor,
  #                            xMax=max(xLimits) * factor,
  #                            yMin=-abs(min(yLimits)) * factor,
  #                            yMax=max(yLimits) * factor,
  #                            minXRange=((max(xLimits) - min(xLimits))/max(xLimits)) * ratio,
  #                            maxXRange=max(xLimits) * factor,
  #                            minYRange=(((max(yLimits) - min(yLimits))/max(yLimits))),
  #                            maxYRange=max(yLimits) * factor
  #                            )
  #   else:
  #     self.viewBox.setLimits(xMin=-abs(min(xLimits)) * factor,
  #                            xMax=max(xLimits) * factor,
  #                            yMin=-abs(min(yLimits)) * factor,
  #                            yMax=max(yLimits) * factor,
  #                            minXRange=((max(xLimits) - min(xLimits))/max(xLimits)) ,
  #                            maxXRange=max(xLimits) * factor,
  #                            minYRange=(((max(yLimits) - min(yLimits))/max(yLimits)))*ratio,
  #                            maxYRange=max(yLimits) * factor
  #                            )

  # def removeZoomLimits(self):
  #   self.viewBox.setLimits(xMin=None,
  #                          xMax=None,
  #                          yMin=None,
  #                          yMax=None,
  #                          # Zoom Limits
  #                          minXRange=None,
  #                          maxXRange=None,
  #                          minYRange=None,
  #                          maxYRange=None
  #                          )

  def _storeZoom(self):
    """
    Adds current region to the zoom stack for the strip.
    """
    if not self._finaliseDone: return
    self.storedZooms.append(self.viewBox.viewRange())

    try:
      self._CcpnGLWidget.storeZoom()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def _restoreZoom(self):
    """
    Restores last saved region to the zoom stack for the strip.
    """
    if not self._finaliseDone: return
    if len(self.storedZooms) != 0:
      restoredZoom = self.storedZooms.pop()
      padding = self.application.preferences.general.stripRegionPadding
      self.plotWidget.setXRange(restoredZoom[0][0], restoredZoom[0][1], padding=padding)
      self.plotWidget.setYRange(restoredZoom[1][0], restoredZoom[1][1], padding=padding)
    else:
      self.resetZoom()

    try:
      self._CcpnGLWidget.restoreZoom()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  # def resetZoom(self):
  #   """
  #   Zooms both axis of strip to the specified region
  #   """
  #   if not self._finaliseDone: return
  #   padding = self.application.preferences.general.stripRegionPadding
  #   self.viewBox.autoRange(padding=padding)

  def resetZoom(self):
    try:
      self._CcpnGLWidget.resetZoom()
      self.pythonConsole.writeConsoleCommand("strip.resetZoom()", strip=self)
      getLogger().info("strip = application.getByGid('%s')\nstrip.resetZoom()" % self.pid)
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def _zoomIn(self):
    """
    zoom in to the strip.
    """
    if not self._finaliseDone: return
    zoomPercent = -self.application.preferences.general.zoomPercent/100.0
    padding = self.application.preferences.general.stripRegionPadding
    currentRange = self.viewBox.viewRange()
    l = currentRange[0][0]
    r = currentRange[0][1]
    b = currentRange[1][0]
    t = currentRange[1][1]
    dx = (r-l)/2.0
    dy = (t-b)/2.0
    nl = l-zoomPercent*dx
    nr = r+zoomPercent*dx
    nt = t+zoomPercent*dy
    nb = b-zoomPercent*dy
    self.plotWidget.setXRange(nl, nr, padding=padding)
    self.plotWidget.setYRange(nb, nt, padding=padding)

    try:
      self._CcpnGLWidget.zoomIn()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def _zoomOut(self):
    """
    zoom out of the strip.
    """
    if not self._finaliseDone: return
    zoomPercent = +self.application.preferences.general.zoomPercent/100.0
    padding = self.application.preferences.general.stripRegionPadding
    currentRange = self.viewBox.viewRange()
    l = currentRange[0][0]
    r = currentRange[0][1]
    b = currentRange[1][0]
    t = currentRange[1][1]
    dx = (r-l)/2.0
    dy = (t-b)/2.0
    nl = l-zoomPercent*dx
    nr = r+zoomPercent*dx
    nt = t+zoomPercent*dy
    nb = b-zoomPercent*dy
    self.plotWidget.setXRange(nl, nr, padding=padding)
    self.plotWidget.setYRange(nb, nt, padding=padding)

    try:
      self._CcpnGLWidget.zoomOut()
    except:
      getLogger().debug('Error: OpenGL widget not instantiated for %s' % self)

  def showPeaks(self, peakList:PeakList, peaks:typing.List[Peak]=None):
    ###from ccpn.ui.gui.modules.spectrumItems.GuiPeakListView import GuiPeakListView
    # NBNB TBD 1) we should not always display all peak lists together
    # NBNB TBD 2) This should not be called for each strip

    if not self._finaliseDone: return

    if not peaks:
      peaks = peakList.peaks

    peakListView = self._findPeakListView(peakList)
    if not peakListView:
      return

    peaks = [peak for peak in peaks if self.peakIsInPlane(peak) or self.peakIsInFlankingPlane(peak)]
    self.spectrumDisplay.showPeaks(peakListView, peaks)

  def _resetRemoveStripAction(self):
    """Update interface when a strip is created or deleted.

      NB notifier is executed after deletion is final but before the wrapper is updated.
      len() > 1 check is correct also for delete
    """
    pass  # GWV: poor soultion self.spectrumDisplay._resetRemoveStripAction()

  def _moveToNextSpectrumView(self):
    spectrumViews = self.orderedSpectrumViews()
    countSpvs = len(spectrumViews)
    if countSpvs > 0:
      visibleSpectrumViews = [i for i in spectrumViews if i.isVisible()]
      if len(visibleSpectrumViews) > 0:
        currentIndex = spectrumViews.index(visibleSpectrumViews[-1])
        if countSpvs > currentIndex + 1:
          for visibleSpectrumView in visibleSpectrumViews:
            visibleSpectrumView.setVisible(False)
          spectrumViews[currentIndex + 1].setVisible(True)
        elif countSpvs == currentIndex + 1: #starts again from the first
          for visibleSpectrumView in visibleSpectrumViews:
            visibleSpectrumView.setVisible(False)
          spectrumViews[0].setVisible(True)
      else:
        spectrumViews[-1].setVisible(True) #starts the loop again if none is selected
    else:
      getLogger().warning('No spectra displayed')

  def _moveToPreviousSpectrumView(self):
    spectrumViews = self.orderedSpectrumViews()
    countSpvs = len(spectrumViews)
    if countSpvs > 0:
      visibleSpectrumViews = [i for i in spectrumViews if i.isVisible()]
      if len(visibleSpectrumViews) >0:
        currentIndex = spectrumViews.index(visibleSpectrumViews[0])
        # if countSpvs > currentIndex + 1:
        for visibleSpectrumView in visibleSpectrumViews:
          visibleSpectrumView.setVisible(False)
        spectrumViews[currentIndex - 1].setVisible(True)
      else:
        spectrumViews[-1].setVisible(True)  # starts the loop again if none is selected

    else:
      getLogger().warning('No spectra displayed')

  def _showAllSpectrumViews(self, value:bool=True):
    spectrumViews = self.orderedSpectrumViews()
    for sp in spectrumViews:
      sp.setVisible(value)

  def _invertSelectedSpectra(self):
    spectrumViews = self.orderedSpectrumViews()
    countSpvs = len(spectrumViews)
    if countSpvs > 0:

      visibleSpectrumViews = [i.isVisible() for i in spectrumViews]
      if any(visibleSpectrumViews):
        changeState = [i.setVisible(not i.isVisible()) for i in spectrumViews]
      else:
        self._showAllSpectrumViews(True)




# Notifiers:
def _updateDisplayedMarks(data):
  "Callback when marks have changed"

  from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
  GLSignals = GLNotifier(parent=None)
  GLSignals.emitEvent(triggers=[GLNotifier.GLMARKS])

def _updateSelectedPeaks(data):
  "Callback when peaks have changed"

  from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier
  GLSignals = GLNotifier(parent=None)
  GLSignals.emitEvent(triggers=[GLNotifier.GLHIGHLIGHTPEAKS], targets=data[Notifier.OBJECT].peaks)

def _axisRegionChanged(axis:'Axis'):
  """Notifier function: Update strips etc. for when axis position or width changes"""

  strip = axis.strip
  if not strip._finaliseDone: return

  position = axis.position
  width = axis.width
  region = (position - width/2., position + width/2.)

  index = strip.axisOrder.index(axis.code)
  if not strip.beingUpdated:

    strip.beingUpdated = True

    try:
      if index == 0:
        # X axis
        padding = strip.application.preferences.general.stripRegionPadding
        strip.viewBox.setXRange(*region, padding=padding)
      elif index == 1:
        # Y axis
        padding = strip.application.preferences.general.stripRegionPadding
        strip.viewBox.setYRange(*region, padding=padding)
      else:
        # One of the Z axes
        strip._updateTraces()
        for spectrumView in strip.spectrumViews:
          spectrumView.update()
          if spectrumView.isVisible():
            for peakListView in spectrumView.peakListViews:
              if peakListView.isVisible():
                peakList = peakListView.peakList
                peaks = [peak for peak in peakList.peaks if strip.peakIsInPlane(peak) or strip.peakIsInFlankingPlane(peak)]
                strip.spectrumDisplay.showPeaks(peakListView, peaks)

        if len(strip.axisOrder) > 2:
          n = index - 2
          if n >= 0:
            planeLabel = strip.planeToolbar.planeLabels[n]
            planeSize = planeLabel.singleStep()
            planeLabel.setValue(position)
            strip.planeToolbar.planeCounts[n].setValue(width/planeSize)

      if index >= 2:
        spectrumDisplay = strip.spectrumDisplay
        if hasattr(spectrumDisplay, 'activePeakItemDict'):  # ND display
          activePeakItemDict = spectrumDisplay.activePeakItemDict
          for spectrumView in strip.spectrumViews:
            for peakListView in spectrumView.peakListViews:
              peakItemDict = activePeakItemDict.get(peakListView, {})
              for peakItem in peakItemDict.values():
                peakItem._stripRegionUpdated()

    finally:
      strip.beingUpdated = False

  if index == 1:  # ASSUMES that only do H phasing
    strip._updatePhasing()


# NB The following two notifiers could be replaced by wrapper notifiers on
# Mark, 'change'. But it would be rather more clumsy, so leave it as it is.

# NBNB TODO code uses API object. REFACTOR

def _rulerCreated(project:Project, apiRuler:ApiRuler):
  """Notifier function for creating rulers"""
  for strip in project.strips:
    strip.plotWidget._addRulerLine(apiRuler)

def _rulerDeleted(project:Project, apiRuler:ApiRuler):
  """Notifier function for deleting rulers"""
  for strip in project.strips:
    strip.plotWidget._removeRulerLine(apiRuler)

# Add notifier functions to Project


# NB This notifier must be implemented as an API postInit notifier,
# As it relies on Axs that are not yet created when 'created' notifiers are executed
def _setupGuiStrip(project:Project, apiStrip):
  """Set up graphical parameters for completed strips - for notifiers"""
  strip = project._data2Obj[apiStrip]

  if not strip._finaliseDone: return

  orderedAxes = strip.orderedAxes
  padding = strip.application.preferences.general.stripRegionPadding

  strip.viewBox.setXRange(*orderedAxes[0].region, padding=padding)
  strip.viewBox.setYRange(*orderedAxes[1].region, padding=padding)
  strip.plotWidget._initTextItems()
  strip.viewBox.sigStateChanged.connect(strip.plotWidget._moveAxisCodeLabels)

  # signal for communicating zoom across strips
  strip.viewBox.sigXRangeChanged.connect(strip._updateXRegion)
  strip.viewBox.sigYRangeChanged.connect(strip._updateYRegion)

  try:
    strip._CcpnGLWidget.initialiseAxes(strip=strip)
    # strip._CcpnGLWidget._resetAxisRange()
  except:
    getLogger().debug('Error: OpenGL widget not instantiated for %s' % strip)