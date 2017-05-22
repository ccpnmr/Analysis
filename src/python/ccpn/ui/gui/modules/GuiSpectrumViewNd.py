"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan",
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Wayne Boucher $"
__dateModified__ = "$dateModified: 2017-04-11 15:15:27 +0100 (Tue, April 11, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
import math
import numpy
import os

from OpenGL import GL
from OpenGL.error import GLError

from PyQt4 import QtCore, QtGui

import pyqtgraph as pg

from ccpn.util import Colour
from ccpn.util import Phasing

from ccpnc.contour import Contourer2d

from ccpn.ui.gui.modules import GuiStripDisplayNd
from ccpn.ui.gui.modules.GuiSpectrumView import GuiSpectrumView
###from ccpn.ui.gui.widgets.ToolButton import ToolButton
###from ccpnc.peak import Peak
###from ccpn.ui.gui.modules.spectrumPane.PeakListNdItem import PeakListNdItem

# TBD: for now ignore fact that apiSpectrumView can override contour colour and/or contour levels

from ccpnmodel.ccpncore.memops import Notifiers

#TODO:RASMUS: why is this function here when the wrapper has positiveLevels and negativeLevels
# attributes
def _getLevels(count:int, base:float, factor:float)->list:
  "return a list with contour levels"
  levels = []
  if count > 0:
    levels = [base]
    for n in range(count-1):
      levels.append(numpy.float32(factor * levels[-1]))
  return levels


class GuiSpectrumViewNd(GuiSpectrumView):
  
  ###PeakListItemClass = PeakListNdItem
  
  #sigClicked = QtCore.Signal(object, object)

  #def __init__(self, guiSpectrumDisplay, apiSpectrumView, dimMapping=None, region=None, **kw):
  def __init__(self):
    """ guiSpectrumDisplay is the parent
        apiSpectrumView is the (API) SpectrumView object
    """
    """ old comment
        region is in units of parent, ordered by spectrum dimensions
        dimMapping is from spectrum numerical dimensions to guiStrip numerical dimensions
        (for example, xDim is what gets mapped to 0 and yDim is what gets mapped to 1)
    """
    ##self.drawContoursCounter = 0

    self.setAcceptedMouseButtons = QtCore.Qt.LeftButton

    #GuiSpectrumView.__init__(self, guiSpectrumDisplay, apiSpectrumView, dimMapping)
    self.posLevelsPrev = []
    self.negLevelsPrev = []
    self.xDataDimPrev = None
    self.yDataDimPrev = None
    self.zRegionPrev = None
    self.posDisplayLists = []
    self.negDisplayLists = []

    self._traceScale = 1.0e-7 # TBD: need a better way of setting this
            
    self.okDataFile = True  # used to keep track of warning message that data file does not exist
    
    # self.spectralData = self.getSlices()
    
    ###xDim, yDim = apiSpectrumView.dimensionOrdering[:2]
    ###xDim -= 1  # dimensionOrdering starts at 1
    ###yDim -= 1

    # TBD: this is not correct
    ##apiDataSource = self._apiDataSource
    # I think this fixes it - number of DISPLAY axes, rather than dataSource axes. RHF
    # dimensionCount = apiDataSource.numDim
    dimensionCount = len(self.strip.axisCodes)
    self.previousRegion = dimensionCount * [None]

    #self.setZValue(-1)  # this is so that the contours are drawn on the bottom

    #self.contourDisplayIndexDict = {} # (xDim, yDim) -> level -> display list index

    # have to have this set before _setupBorderItem called
    self._application = self.strip.spectrumDisplay.mainWindow.application

    # have to setup border item before superclass constructor called because latter calls
    # setVisible and that in turn expects there to be a border item
    self._setupBorderItem()

    GuiSpectrumView.__init__(self)

    self.setZValue(-1)  # this is so that the contours are drawn on the bottom

    """
    self.visibilityAction = action = self._parent.spectrumDisplay.spectrumToolBar.addAction(self.spectrum.name)
    self.setActionIconColour()
    action.setCheckable(True)
    action.setChecked(True)
    widget = self._parent.spectrumDisplay.spectrumToolBar.widgetForAction(action)
    widget.setFixedSize(60, 30)

    for func in ('setPositiveContourColour', 'setSliceColour'):
      Notifiers.registerNotify(self.changedSpectrumColour, 'ccp.nmr.Nmr.DataSource', func)
"""        
    self.strip.viewBox.addItem(self)

    self._setupTrace()

  # override of Qt setVisible

  def setVisible(self, visible):
    GuiSpectrumView.setVisible(self, visible)
    if self._application.preferences.general.showSpectrumBorder:
      self.borderItem.setVisible(visible)

  def _setupBorderItem(self):
    spectrumLimits = self.spectrum.spectrumLimits
    displayIndices = self._displayOrderSpectrumDimensionIndices
    xLimits = spectrumLimits[displayIndices[0]]
    yLimits = spectrumLimits[displayIndices[1]]

    # apiSpectrumView = self._apiStripSpectrumView.spectrumView
    # dataDims = apiSpectrumView.orderedDataDims
    # ll = apiSpectrumView.dataSource.sortedDataDims()
    # # NB Not all dataDIms must match spectrum e.g. 2D spectra in a 3D display
    # dimIndices = [x and ll.index(x) for x in dataDims]
    # xDim = dimIndices[0]
    # yDim = dimIndices[1]
    #
    # spectrumLimits = self.spectrum.spectrumLimits
    # xLimits = spectrumLimits[xDim]
    # yLimits = spectrumLimits[yDim]

    colour = Colour.rgba(self._getColour('positiveContourColour')) # TBD: for now assume only one colour
    rect = QtCore.QRectF(xLimits[0], yLimits[0], xLimits[1]-xLimits[0], yLimits[1]-yLimits[0])
    self.borderItem = QtGui.QGraphicsRectItem(rect)
    self.borderItem.setPen(pg.functions.mkPen(colour[:3], width=1, style=QtCore.Qt.DotLine))
    self.strip.viewBox.addItem(self.borderItem)

    self.borderItem.setVisible(self._application.preferences.general.showSpectrumBorder)
        
  def _setBorderItemHidden(self, checked):
    """
    # CCPN INTERNAL - called by _toggleGeneralOptions method of PreferencesPopup.
    """
    self.borderItem.setVisible(self._application.preferences.general.showSpectrumBorder and self.isVisible())
          
  def _setupTrace(self):
    
    self.hTrace = pg.PlotDataItem()
    self.strip.plotWidget.scene().addItem(self.hTrace)
    
    self.vTrace = pg.PlotDataItem()
    self.strip.plotWidget.scene().addItem(self.vTrace) 
    
    self.hPhaseTraces = []
    self.vPhaseTraces = []
    
  def _turnOnPhasing(self):
    """
    # CCPN INTERNAL - called by turnOnPhasing method of GuiStrip.
    """
    phasingFrame = self.strip.spectrumDisplay.phasingFrame
    if phasingFrame.isVisible():
      direction = phasingFrame.getDirection()
      traces = self.hPhaseTraces if direction == 0 else self.vPhaseTraces
      for trace, line in traces:
        trace.setVisible(True)
        line.setVisible(True)
      
  def _turnOffPhasing(self):
    """
    # CCPN INTERNAL - called by turnOffPhasing method of GuiStrip.
    """
    for traces in self.hPhaseTraces, self.vPhaseTraces:
      for trace, line in traces:
        trace.setVisible(False)
        line.setVisible(False)
      
  def _newPhasingTrace(self):
    
    phasingFrame = self.strip.spectrumDisplay.phasingFrame
    if phasingFrame.isVisible():
      trace = pg.PlotDataItem()
      direction = phasingFrame.getDirection()
      if direction == 0:
        angle = 0
        phaseTraces = self.hPhaseTraces
        position = self.strip.mousePosition[1]
        if not self.strip.haveSetHPhasingPivot:
          viewParams = self._getSpectrumViewParams(0)
          # valuePerPoint, pointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(0)
          self.strip.hPhasingPivot.setPos(0.5*(viewParams.minAliasedFrequency +
                                               viewParams.maxAliasedFrequency))
          self.strip.hPhasingPivot.setVisible(True)
          self.strip.haveSetHPhasingPivot = True
      else:
        angle = 90
        phaseTraces = self.vPhaseTraces
        position = self.strip.mousePosition[0]
        if not self.strip.haveSetVPhasingPivot:
          viewParams = self._getSpectrumViewParams(1)
          # valuePerPoint, pointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(1)
          self.strip.vPhasingPivot.setPos(0.5*(viewParams.minAliasedFrequency +
                                               viewParams.maxAliasedFrequency))
          self.strip.vPhasingPivot.setVisible(True)
          self.strip.haveSetVPhasingPivot = True
        
      line = pg.InfiniteLine(angle=angle, pos=position, movable=True)
      line.sigPositionChanged.connect(lambda phasingLine: self._updatePhasing())
      self.strip.plotWidget.scene().addItem(trace)
      self.strip.plotWidget.addItem(line)
      trace.setVisible(True)
      line.setVisible(True)
      phaseTraces.append((trace, line))
      self._updatePhasing()
  
  def removePhasingTraces(self):
    
    phasingFrame = self.strip.spectrumDisplay.phasingFrame
    if phasingFrame.isVisible():
      direction = phasingFrame.getDirection()
      if direction == 0:
        for trace, line in self.hPhaseTraces:
          self.strip.plotWidget.scene().removeItem(trace)
          self.strip.plotWidget.removeItem(line)
        self.hPhaseTraces = []
      else:
        for trace, line in self.vPhaseTraces:
          self.strip.plotWidget.scene().removeItem(trace)
          self.strip.plotWidget.removeItem(line)
        self.vPhaseTraces = []
    
  def _changedPhasingDirection(self):
    
    phasingFrame = self.strip.spectrumDisplay.phasingFrame
    direction = phasingFrame.getDirection()
    if direction == 0:
      for trace, line in self.hPhaseTraces:
        trace.setVisible(True)
        line.setVisible(True)
      for trace, line in self.vPhaseTraces:
        trace.setVisible(False)
        line.setVisible(False)
    else:
      for trace, line in self.hPhaseTraces:
        trace.setVisible(False)
        line.setVisible(False)
      for trace, line in self.vPhaseTraces:
        trace.setVisible(True)
        line.setVisible(True)
      
    self._updatePhasing()
    
  def _updatePhasing(self):
    """
    # CCPN INTERNAL - called in _updatePhasing method of GuiStrip
    """
    if not self.isVisible():
      return
      
    position = [axis.position for axis in self.strip.orderedAxes]
    
    phasingFrame = self.strip.spectrumDisplay.phasingFrame
    if phasingFrame.isVisible():
      ph0 = phasingFrame.slider0.value()
      ph1 = phasingFrame.slider1.value()
      pivotPpm = phasingFrame.pivotEntry.get()
      direction = phasingFrame.getDirection()
      # dataDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[direction]
      # pivot = dataDim.primaryDataDimRef.valueToPoint(pivotPpm)
      axisIndex = self._displayOrderSpectrumDimensionIndices[direction]
      pivot = self.spectrum.mainSpectrumReferences[axisIndex].valueToPoint(pivotPpm)
    else:
      ph0 = ph1 = direction = 0
      pivot = 1
      
    #hPhasingPivot = self.strip.hPhasingPivot
    #if hPhasingPivot.isVisible():
    #  dataDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[0]
    #  pivot = dataDim.primaryDataDimRef.valueToPoint(hPhasingPivot.getXPos())
    #else:
    #  pivot = 1
      
    if direction == 0:
      phaseTraces = self.hPhaseTraces
    else:
      phaseTraces = self.vPhaseTraces
    for trace, line in phaseTraces:
      line.setPen({'color': self._getColour('sliceColour', '#aaaaaa')})
      if direction == 0:
        position[1] = line.getYPos()
      else:
        position[0] = line.getXPos()
      positionPoint = QtCore.QPointF(position[0], position[1])
      positionPixel = self.strip.viewBox.mapViewToScene(positionPoint)
      positionPixel = (positionPixel.x(), positionPixel.y())
      inRange, point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints = self._getTraceParams(position)        
      if inRange:
        if direction == 0:
          self._updateHTraceData(point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, positionPixel, trace, ph0, ph1, pivot)
        else:
          self._updateVTraceData(point, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints, positionPixel, trace, ph0, ph1, pivot)
            
  def _getTraceParams(self, position):
    # position is in ppm
    
    inRange = True
    point = len(position) * [0]
    for n, pos in enumerate(position): # n = 0 is x, n = 1 is y, etc.
      # spectrumPos, width, totalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(n)
      valuePerPoint, totalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(n)
      if dataDim:
        if n == 0:
          xDataDim = dataDim
          # -1 below because points start at 1 in data model
          xMinFrequency = int(dataDim.primaryDataDimRef.valueToPoint(maxAliasedFrequency)-1)
          xMaxFrequency = int(dataDim.primaryDataDimRef.valueToPoint(minAliasedFrequency)-1)
          xNumPoints = totalPointCount
        elif n == 1:
          yDataDim = dataDim
          yMinFrequency = int(dataDim.primaryDataDimRef.valueToPoint(maxAliasedFrequency)-1)
          yMaxFrequency = int(dataDim.primaryDataDimRef.valueToPoint(minAliasedFrequency)-1)
          yNumPoints = totalPointCount
        else:
          inRange = (minAliasedFrequency <= pos <= maxAliasedFrequency)
          if not inRange:
            break
        pnt = (dataDim.primaryDataDimRef.valueToPoint(pos)-1) % totalPointCount
        pnt += (dataDim.pointOffset if hasattr(dataDim, "pointOffset") else 0)
        point[dataDim.dim-1] = pnt

    return inRange, point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints
    
  def _updateHTraceData(self, point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, positionPixel, hTrace, ph0=None, ph1=None, pivot=None):
    
    # unfortunately it looks like we have to work in pixels, not ppm, yuck
    strip = self.strip
    plotWidget = strip.plotWidget
    plotItem = plotWidget.plotItem
    viewBox = strip.viewBox
    viewRegion = plotWidget.viewRange()
    
    pointInt = [1+int(pnt+0.5) for pnt in point]
    data = self.spectrum.getSliceData(pointInt, sliceDim=xDataDim.dim)
    if ph0 is not None and ph1 is not None and pivot is not None:
      data = Phasing.phaseRealData(data, ph0, ph1, pivot)
    x = numpy.array([xDataDim.primaryDataDimRef.pointToValue(p+1) for p in range(xMinFrequency, xMaxFrequency+1)])
    # scale from ppm to pixels
    pixelViewBox0 = plotItem.getAxis('left').width()
    pixelViewBox1 = pixelViewBox0 + viewBox.width()
    region1, region0 = viewRegion[0]
    x -= region0
    x *= (pixelViewBox1-pixelViewBox0) / (region1-region0)
    x += pixelViewBox0
  
    pixelViewBox0 = plotItem.getAxis('bottom').height()
    pixelViewBox1 = pixelViewBox0 + viewBox.height()
    # - sign below because ppm scale is backwards
    v = positionPixel[1] - self._traceScale * (pixelViewBox1-pixelViewBox0) * numpy.array([data[p % xNumPoints] for p in range(xMinFrequency, xMaxFrequency+1)])
  
    hTrace.setPen({'color': self._getColour('sliceColour', '#aaaaaa')})
    hTrace.setData(x, v)
  
  def _updateVTraceData(self, point, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints, positionPixel, vTrace, ph0=None, ph1=None, pivot=None):
    
    # unfortunately it looks like we have to work in pixels, not ppm, yuck
    strip = self.strip
    plotWidget = strip.plotWidget
    plotItem = plotWidget.plotItem
    viewBox = strip.viewBox
    viewRegion = plotWidget.viewRange()
    
    pointInt = [1+int(pnt+0.5) for pnt in point]
    data = self.spectrum.getSliceData(pointInt, sliceDim=yDataDim.dim)
    if ph0 is not None and ph1 is not None and pivot is not None:
      data = Phasing.phaseRealData(data, ph0, ph1, pivot)
    y = numpy.array([yDataDim.primaryDataDimRef.pointToValue(p+1) for p in range(yMinFrequency, yMaxFrequency+1)])
    # scale from ppm to pixels
    pixelViewBox0 = plotItem.getAxis('bottom').height()
    pixelViewBox1 = pixelViewBox0 + viewBox.height()
    region0, region1 = viewRegion[1]
    y -= region0
    y *= (pixelViewBox1-pixelViewBox0) / (region1-region0)
    ###y += pixelViewBox0  # not sure why this should be commented out...
    
    pixelViewBox0 = plotItem.getAxis('left').width()
    pixelViewBox1 = pixelViewBox0 + viewBox.width()
    # no - sign below because ppm scale is backwards and pixel y scale is also backwards
    # (assuming that we want positive signal to point towards the right)
    v = positionPixel[0] + self._traceScale * (pixelViewBox1-pixelViewBox0) * numpy.array([data[p % yNumPoints] for p in range(yMinFrequency, yMaxFrequency+1)])
    
    vTrace.setPen({'color': self._getColour('sliceColour', '#aaaaaa')})
    vTrace.setData(v, y)

  def _updateTrace(self, position, positionPixel, updateHTrace=True, updateVTrace=True):
        
    if not (updateHTrace or updateVTrace) or not self.isVisible():
      self.hTrace.setData([], [])
      self.vTrace.setData([], [])
      return
          
    inRange, point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints = self._getTraceParams(position)        
    # xDataDim and yDataDim should always be set here, because all spectra in strip should at least match in x, y
    
    if inRange and updateHTrace:
      self._updateHTraceData(point, xDataDim, xMinFrequency, xMaxFrequency, xNumPoints, positionPixel, self.hTrace)
    else:
      self.hTrace.setData([], [])
      
    if inRange and updateVTrace:
      self._updateVTraceData(point, yDataDim, yMinFrequency, yMaxFrequency, yNumPoints, positionPixel, self.vTrace)
    else:
      self.vTrace.setData([], [])

    self.strip.plotWidget.plotItem.update()

  @property
  def traceScale(self) -> float:
    """Scale for trace in this spectrumView"""
    return self._traceScale

  @traceScale.setter
  def traceScale(self, value):
    """Setter for scale for trace in this spectrumView"""
    self._traceScale = value
    self.strip._updateTraces()
    self._updatePhasing()

  ###def connectStrip(self, strip):
  ###  item = self.spectrumItems[strip]
  ###  self.spectrumViewButton.spaction.toggled.connect(item.setVisible)
  """
  def getLevels(self):
    
    levels = [self.baseLevel]
    for n in range(int(self.numberOfLevels-1)):
      levels.append(self.multiplier*levels[-1])
      
    return tuple(numpy.array(levels, dtype=numpy.float32))
"""

  # def zPlaneSize(self):  # TBD: Do we need this still?
  #
  #   spectrum = self.spectrum
  #   dimensionCount = spectrum.dimensionCount
  #   if dimensionCount < 3:
  #     return None  # TBD
  #
  #   # zDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[2].dim - 1
  #   zDataDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[2]
  #   point = (0.0, 1.0)
  #   # value = spectrum.getDimValueFromPoint(zDim, point)
  #   value = zDataDim.primaryDataDimRef.pointToValue(point)
  #   size = abs(value[1] - value[0])
  #
  #   return size

  def _newPeakListView(self, peakListView):
    pass
    
  def _printToFile(self, printer):
    """
    # CCPN INTERNAL - called in _printToFile method of GuiStrip
    """

    if not self.isVisible():
      return
  
    # assume that already done on screen
    #if apiDataSource.positiveContourBase == 10000.0: # horrid
    #  # base has not yet been set, so guess a sensible value
    #  apiDataSource.positiveContourBase = apiDataSource.estimateNoise()
    #  apiDataSource.negativeContourBase = - apiDataSource.positiveContourBase

    if self.displayPositiveContours:
      posLevels = _getLevels(self.positiveContourCount, self.positiveContourBase,
                             self.positiveContourFactor)
    else:
      posLevels = []
    
    if self.displayNegativeContours is True:
      negLevels = _getLevels(self.negativeContourCount, self.negativeContourBase,
                             self.negativeContourFactor)
    else:
      negLevels = []

    if not posLevels and not negLevels:
      return

    posColour = self._getColour('positiveContourColour')
    negColour = self._getColour('negativeContourColour')
  
    xTranslate, xScale, xTotalPointCount, xClipPoint0, xClipPoint1 = self._getTranslateScale(
        0, pixelViewBox0=printer.x0, pixelViewBox1=printer.x1 )
    yTranslate, yScale, yTotalPointCount, yClipPoint0, yClipPoint1 = self._getTranslateScale(
        1, pixelViewBox0=printer.y0, pixelViewBox1=printer.y1)

    xTile0 = xClipPoint0 // xTotalPointCount
    xTile1 = 1 + (xClipPoint1 // xTotalPointCount)
    yTile0 = yClipPoint0 // yTotalPointCount
    yTile1 = 1 + (yClipPoint1 // yTotalPointCount)
      
    for position, dataArray in self._getPlaneData():

      if posLevels:
        posLevelsArray = numpy.array(posLevels, numpy.float32)
        posContours = Contourer2d.contourer2d(dataArray, posLevelsArray)
        for contourData in posContours:
          self._printContourData(printer, contourData, posColour, xTile0, xTile1, yTile0, yTile1,
                                 xTranslate, xScale, xTotalPointCount, yTranslate, yScale,
                                 yTotalPointCount)
      
      if negLevels:
        negLevelsArray = numpy.array(negLevels, numpy.float32)
        negContours = Contourer2d.contourer2d(dataArray, negLevelsArray)
        for contourData in negContours:
          self._printContourData(printer, contourData, negColour, xTile0, xTile1, yTile0, yTile1,
                                 xTranslate, xScale, xTotalPointCount, yTranslate, yScale,
                                 yTotalPointCount)
                
    for peakListView in self.peakListViews:
      peakListView._printToFile(printer)
      
  def _printContourData(self, printer, contourData, colour, xTile0, xTile1, yTile0, yTile1, xTranslate, xScale, xTotalPointCount, yTranslate, yScale, yTotalPointCount):
    
    for xTile in range(xTile0, xTile1):
      for yTile in range(yTile0, yTile1):
        
        # the below is because the y axis goes from top to bottom
        #GL.glScale(1.0, -1.0, 1.0)
        #GL.glTranslate(0.0, -self.strip.plotWidget.height(), 0.0)
    
        # the below makes sure that spectrum points get mapped to screen pixels correctly
        #GL.glTranslate(xTranslate, yTranslate, 0.0)
        #GL.glScale(xScale, yScale, 1.0)
    
        #GL.glTranslate(xTotalPointCount*xTile, yTotalPointCount*yTile, 0.0)
        #GL.glClipPlane(GL.GL_CLIP_PLANE0, (1.0, 0.0, 0.0, - (xClipPoint0 - xTotalPointCount*xTile)))
        #GL.glClipPlane(GL.GL_CLIP_PLANE1, (-1.0, 0.0, 0.0, xClipPoint1 - xTotalPointCount*xTile))
        #GL.glClipPlane(GL.GL_CLIP_PLANE2, (0.0, 1.0, 0.0, - (yClipPoint0 - yTotalPointCount*yTile)))
        #GL.glClipPlane(GL.GL_CLIP_PLANE3, (0.0, -1.0, 0.0, yClipPoint1 - yTotalPointCount*yTile))
        
        
        for contour in contourData:
          n = len(contour) // 2
          contour = contour.copy()
          contour = contour.reshape((n, 2))
          contour[:,0] += xTotalPointCount*xTile
          contour[:,0] *= xScale
          contour[:,0] += xTranslate
          contour[:,1] += yTotalPointCount*yTile
          contour[:,1] *= yScale
          contour[:,1] += yTranslate
          printer.writePolyline(contour, colour)

  def paint(self, painter, option, widget=None):

    if self.isDeleted or self.project.isDeleted or not self.isVisible():
      return

    ##if not widget:
    ##  return
    dataStore = self._apiDataSource.dataStore
    if dataStore is None or not os.path.exists(dataStore.fullPath):
      if self.okDataFile:
        self.project._logger.warning("%s cannot find any data - data file misplaced?" % self )
        self.okDataFile = False
      return

    self.okDataFile = True

    try:
      self._drawContours(painter)
    except GLError:  # invalid framebuffer operation
      pass

  # def boundingRect(self):  # seems necessary to have
  #
  #   return QtCore.QRectF(-2000, -2000, 2000, 2000)  # TODO: remove hardwiring
  
  ##### functions not to be used externally #####
  # NBNB TBD internal functions should start with UNDERSCORE!
  # REFACTOR

  #def drawContours(self, painter, guiStrip):
  def _drawContours(self, painter):
    
    ##self.drawContoursCounter += 1
    ##print('***drawContours counter (%s): %d' % (self, self.drawContoursCounter))

    if self.spectrum.positiveContourBase == 10000.0: # horrid
      # base has not yet been set, so guess a sensible value
      self.spectrum.positiveContourBase = self.spectrum.estimateNoise()
      self.spectrum.negativeContourBase = - self.spectrum.positiveContourBase

    if self.displayPositiveContours:
      posLevels = _getLevels(self.positiveContourCount, self.positiveContourBase,
                             self.positiveContourFactor)
    else:
      posLevels = []

    if self.displayNegativeContours:
      negLevels = _getLevels(self.negativeContourCount, self.negativeContourBase,
                             self.negativeContourFactor)
    else:
      negLevels = []
    if not posLevels and not negLevels:
      return

    #contourDict = self.constructContours(guiStrip, posLevels, negLevels)
    try:
      self._constructContours(posLevels, negLevels)
    except FileNotFoundError:
      self._project._logger.warning("No data file found for %s" % self)
      return

    posColour = Colour.scaledRgba(self._getColour('positiveContourColour')) # TBD: for now assume only one colour
    negColour = Colour.scaledRgba(self._getColour('negativeContourColour')) # and assumes these attributes are set

    painter.beginNativePainting()  # this puts OpenGL back in its default coordinate system instead of Qt one

    try:

      xTranslate, xScale, xTotalPointCount, xClipPoint0, xClipPoint1 = self._getTranslateScale(0)
      yTranslate, yScale, yTotalPointCount, yClipPoint0, yClipPoint1 = self._getTranslateScale(1)
      
      xTile0 = xClipPoint0 // xTotalPointCount
      xTile1 = 1 + (xClipPoint1 // xTotalPointCount)
      yTile0 = yClipPoint0 // yTotalPointCount
      yTile1 = 1 + (yClipPoint1 // yTotalPointCount)
      
      GL.glEnable(GL.GL_CLIP_PLANE0)
      GL.glEnable(GL.GL_CLIP_PLANE1)
      GL.glEnable(GL.GL_CLIP_PLANE2)
      GL.glEnable(GL.GL_CLIP_PLANE3)
      
      for xTile in range(xTile0, xTile1):
        for yTile in range(yTile0, yTile1):
          
          GL.glLoadIdentity()
          GL.glPushMatrix()

          # the below is because the y axis goes from top to bottom
          GL.glScale(1.0, -1.0, 1.0)
          GL.glTranslate(0.0, -self.strip.plotWidget.height(), 0.0)
      
          # the below makes sure that spectrum points get mapped to screen pixels correctly
          GL.glTranslate(xTranslate, yTranslate, 0.0)
          GL.glScale(xScale, yScale, 1.0)
      
          GL.glTranslate(xTotalPointCount*xTile, yTotalPointCount*yTile, 0.0)
          GL.glClipPlane(GL.GL_CLIP_PLANE0, (1.0, 0.0, 0.0, - (xClipPoint0 - xTotalPointCount*xTile)))
          GL.glClipPlane(GL.GL_CLIP_PLANE1, (-1.0, 0.0, 0.0, xClipPoint1 - xTotalPointCount*xTile))
          GL.glClipPlane(GL.GL_CLIP_PLANE2, (0.0, 1.0, 0.0, - (yClipPoint0 - yTotalPointCount*yTile)))
          GL.glClipPlane(GL.GL_CLIP_PLANE3, (0.0, -1.0, 0.0, yClipPoint1 - yTotalPointCount*yTile))
          
          for (colour, levels, displayLists) in ((posColour, posLevels, self.posDisplayLists),
                                                 (negColour, negLevels, self.negDisplayLists)):
            for n, level in enumerate(levels):
              GL.glColor4f(*colour)
              # TBD: scaling, translating, etc.
              GL.glCallList(displayLists[n])
          GL.glPopMatrix()
      
      GL.glDisable(GL.GL_CLIP_PLANE0)
      GL.glDisable(GL.GL_CLIP_PLANE1)
      GL.glDisable(GL.GL_CLIP_PLANE2)
      GL.glDisable(GL.GL_CLIP_PLANE3)

    finally:
      
      painter.endNativePainting()
      
  def _constructContours(self, posLevels, negLevels, doRefresh=False):
    """ Construct the contours for this spectrum using an OpenGL display list
        The way this is done here, any change in contour level needs to call this function.
    """
    
    xDataDim, yDataDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[:2]

    if (doRefresh or xDataDim is not self.xDataDimPrev or yDataDim is not self.yDataDimPrev 
      or self.zRegionPrev != tuple([tuple(axis.region) for axis in self.strip.orderedAxes[2:]])):
      self._releaseDisplayLists(self.posDisplayLists)
      self._releaseDisplayLists(self.negDisplayLists)
      doPosLevels = doNegLevels = True
    else:
      if list(posLevels) == self.posLevelsPrev:
        doPosLevels = False
      else:
        self._releaseDisplayLists(self.posDisplayLists)
        doPosLevels = posLevels and True
      if list(negLevels) == self.negLevelsPrev:
        doNegLevels = False
      else:
        self._releaseDisplayLists(self.negDisplayLists)
        doNegLevels = negLevels and True
      
    ###self.previousRegion = self.guiSpectrumDisplay.region[:]  # TBD: not quite right, should be looking at the strip(s)
    
    # do the contouring and store results in display list
    if doPosLevels:
      posLevelsArray = numpy.array(posLevels, numpy.float32)
      # print(posLevelsArray)
      self._createDisplayLists(posLevelsArray, self.posDisplayLists)
      
    if doNegLevels:
      negLevelsArray = numpy.array(negLevels, numpy.float32)
      self._createDisplayLists(negLevelsArray, self.negDisplayLists)

    self.posLevelsPrev = list(posLevels)
    self.negLevelsPrev = list(negLevels)
    self.xDataDimPrev = xDataDim
    self.yDataDimPrev = yDataDim
    self.zRegionPrev = tuple([tuple(axis.region) for axis in self.strip.orderedAxes[2:]])

    if not doPosLevels and not doNegLevels:
      return
      
    ###GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    
    #for position, dataArray in self.getPlaneData(guiStrip):
    posContoursAll = negContoursAll = None
    for position, dataArray in self._getPlaneData():

      #print ("gotPlaneData", position, doPosLevels, doNegLevels, len(dataArray), dataArray)
      
      if doPosLevels:
        posContours = Contourer2d.contourer2d(dataArray, posLevelsArray)
        #print("posContours", posContours)
        if posContoursAll is None:
          posContoursAll = posContours
        else:
          for n, contourData in enumerate(posContours):
            if len(posContoursAll) == n: # this can happen (if no contours at a given level then contourer immediately exits)
              posContoursAll.append(contourData)
            else:
              posContoursAll[n].extend(contourData)
            # print(contourData)
        
      if doNegLevels:
        negContours = Contourer2d.contourer2d(dataArray, negLevelsArray)
        #print("negContours", len(negContours))
        if negContoursAll is None:
          negContoursAll = negContours
        else:
          for n, contourData in enumerate(negContours):
            if len(negContoursAll) == n: # this can happen (if no contours at a given level then contourer immediately exits)
              negContoursAll.append(contourData)
            else:
              negContoursAll[n].extend(contourData)
            # print(contourData)
        
    if posContoursAll:
      for n, contourData in enumerate(posContoursAll):
        self._addContoursToDisplayList(self.posDisplayLists[n], contourData, posLevels[n])

    if negContoursAll:
      for n, contourData in enumerate(negContoursAll):
        self._addContoursToDisplayList(self.negDisplayLists[n], contourData, negLevels[n])
      
    ###GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

  def _releaseDisplayLists(self, displayLists):

    for displayList in displayLists:
      GL.glDeleteLists(displayList, 1)
    displayLists[:] = []

  def _createDisplayLists(self, levels, displayLists):

    # could create them in one go but more likely to get fragmentation that way
    for level in levels:
      displayLists.append(GL.glGenLists(1))

  #def getPlaneData(self, guiStrip):
  def _getPlaneData(self):

    # NBNB TODO FIXME - Wayne, please check through the modified code

    spectrum = self.spectrum
    dimensionCount = spectrum.dimensionCount
    dimIndices = self._displayOrderSpectrumDimensionIndices
    xDim = dimIndices[0]
    yDim = dimIndices[1]
    orderedAxes = self._apiStripSpectrumView.strip.orderedAxes
    
    # apiSpectrumView = self._apiStripSpectrumView.spectrumView
    # orderedAxes = self._apiStripSpectrumView.strip.orderedAxes
    # dataDims = apiSpectrumView.orderedDataDims
    # ll = apiSpectrumView.dataSource.sortedDataDims()
    # # NB Not all dataDIms must match spectrum e.g. 2D spectra in a 3D display
    # dimIndices = [x and ll.index(x) for x in dataDims]
    # xDim = dimIndices[0]
    # yDim = dimIndices[1]
    # # xDim = dataDims[0].dim - 1  # -1 because dataDim.dim starts at 1
    # # yDim = dataDims[1].dim - 1
    # spectrum = self.spectrum
    # dimensionCount = spectrum.dimensionCount
        
    if dimensionCount == 2:
      planeData = spectrum.getPlaneData(xDim=xDim+1, yDim=yDim+1)
      position = [1, 1]
      yield position, planeData
    elif dimensionCount == 3:
      # zDim = dataDims[2].dim - 1
      # zDataDim = dataDims[2]
      # zPosition, width, zTotalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(2)
      valuePerPoint, zTotalPointCount, minAliasedFrequency, maxAliasedFrequency, zDataDim = self._getSpectrumViewParams(2)
      zPosition = orderedAxes[2].position
      width =  orderedAxes[2].width

      if not (minAliasedFrequency <= zPosition <= maxAliasedFrequency):
        return
        
      zRegionValue = (zPosition+0.5*width, zPosition-0.5*width) # Note + and - (axis backwards)
      # zPoint0, zPoint1 = spectrum.getDimPointFromValue(zDim, zRegionValue)
      valueToPoint = zDataDim.primaryDataDimRef.valueToPoint
      # -1 below because points start at 1 in data model
      zPointFloat0 = valueToPoint(zRegionValue[0]) - 1
      zPointFloat1 = valueToPoint(zRegionValue[1]) - 1
      
      zPoint0, zPoint1 = (int(zPointFloat0+1), int(zPointFloat1+1)) # this gives first and 1+last integer in range
      if zPoint0 == zPoint1:
        if zPointFloat0-(zPoint0-1) < zPoint1-zPointFloat1: # which is closest to an integer
          zPoint0 -= 1
        else:
          zPoint1 += 1
      
      if (zPoint1 - zPoint0) >= zTotalPointCount:
        zPoint0 = 0
        zPoint1 = zTotalPointCount
      else:
        zPoint0 %= zTotalPointCount
        zPoint1 %= zTotalPointCount
        if zPoint1 < zPoint0:
          zPoint1 += zTotalPointCount

      # zPointOffset = spectrum.pointOffsets[zDim]
      # zPointCount = spectrum.pointCounts[zDim]
      zPointOffset = zDataDim.pointOffset if hasattr(zDataDim, "pointOffset") else 0
      zPointCount = zDataDim.numPoints
            
      position = dimensionCount * [1]
      for z in range(zPoint0, zPoint1):
        zPosition = z % zTotalPointCount
        zPosition -= zPointOffset
        if 0 <= zPosition < zPointCount:
          position[dimIndices[2]] = zPosition + 1
          planeData = spectrum.getPlaneData(position, xDim=xDim+1, yDim=yDim+1)
          yield position, planeData

    elif dimensionCount == 4:
      # zDim = dataDims[2].dim - 1
      # zDataDim = dataDims[2]
      # zPosition, width, zTotalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(2)
      valuePerPoint, zTotalPointCount, minAliasedFrequency, maxAliasedFrequency, zDataDim = self._getSpectrumViewParams(2)
      zPosition = orderedAxes[2].position
      width =  orderedAxes[2].width
        
      if not (minAliasedFrequency <= zPosition <= maxAliasedFrequency):
        return
        
      zRegionValue = (zPosition+0.5*width, zPosition-0.5*width) # Note + and - (axis backwards)
      # zPoint0, zPoint1 = spectrum.getDimPointFromValue(zDim, zRegionValue)
      valueToPoint = zDataDim.primaryDataDimRef.valueToPoint
      # -1 below because points start at 1 in data model
      zPointFloat0 = valueToPoint(zRegionValue[0]) - 1
      zPointFloat1 = valueToPoint(zRegionValue[1]) - 1
      
      zPoint0, zPoint1 = (int(zPointFloat0+1), int(zPointFloat1+1)) # this gives first and 1+last integer in range
      if zPoint0 == zPoint1:
        if zPointFloat0-(zPoint0-1) < zPoint1-zPointFloat1: # which is closest to an integer
          zPoint0 -= 1
        else:
          zPoint1 += 1
      
      if (zPoint1 - zPoint0) >= zTotalPointCount:
        zPoint0 = 0
        zPoint1 = zTotalPointCount
      else:
        zPoint0 %= zTotalPointCount
        zPoint1 %= zTotalPointCount
        if zPoint1 < zPoint0:
          zPoint1 += zTotalPointCount
          
      # zPointOffset = spectrum.pointOffsets[zDim]
      # zPointCount = spectrum.pointCounts[zDim]
      zPointOffset = zDataDim.pointOffset if hasattr(zDataDim, "pointOffset") else 0
      zPointCount = zDataDim.numPoints
            
      # wDim = dataDims[3].dim - 1
      # wDataDim = dataDims[3]
      # wPosition, width, wTotalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim = self._getSpectrumViewParams(3)
      valuePerPoint, wTotalPointCount, minAliasedFrequency, maxAliasedFrequency, wDataDim = self._getSpectrumViewParams(3)
      wPosition = orderedAxes[3].position
      width =  orderedAxes[3].width
        
      if not (minAliasedFrequency <= wPosition <= maxAliasedFrequency):
        return
        
      wRegionValue = (wPosition+0.5*width, wPosition-0.5*width) # Note + and - (axis backwards)
      # wPoint0, wPoint1 = spectrum.getDimPointFromValue(wDim, wRegionValue)
      valueToPoint = wDataDim.primaryDataDimRef.valueToPoint
      # -1 below because points start at 1 in data model
      wPointFloat0 = valueToPoint(wRegionValue[0]) - 1
      wPointFloat1 = valueToPoint(wRegionValue[1]) - 1
      
      wPoint0, wPoint1 = (int(wPointFloat0+1), int(wPointFloat1+1)) # this gives first and 1+last integer in range
      if wPoint0 == wPoint1:
        if wPointFloat0-(wPoint0-1) < wPoint1-wPointFloat1: # which is closest to an integer
          wPoint0 -= 1
        else:
          wPoint1 += 1
          
      if (wPoint1 - wPoint0) >= wTotalPointCount:
        wPoint0 = 0
        wPoint1 = wTotalPointCount
      else:
        wPoint0 %= wTotalPointCount
        wPoint1 %= wTotalPointCount
        if wPoint1 < wPoint0:
          wPoint1 += wTotalPointCount
          
      # wPointOffset = spectrum.pointOffsets[wDim]
      # wPointCount = spectrum.pointCounts[wDim]
      wPointOffset = wDataDim.pointOffset if hasattr(zDataDim, "pointOffset") else 0
      wPointCount = wDataDim.numPoints
            
      position = dimensionCount * [1]
      for z in range(zPoint0, zPoint1):
        zPosition = z % zTotalPointCount
        zPosition -= zPointOffset
        if 0 <= zPosition < zPointCount:
          position[dimIndices[2]] = zPosition + 1
          for w in range(wPoint0, wPoint1):
            wPosition = w % wTotalPointCount
            wPosition -= wPointOffset
            if 0 <= wPosition < wPointCount:
              position[dimIndices[3]] = wPosition + 1
              planeData = spectrum.getPlaneData(position, xDim=xDim+1, yDim=yDim+1)
              yield position, planeData
          
  def _addContoursToDisplayList(self, displayList, contourData, level):
    """ contourData is list of [NumPy array with ndim = 1 and size = twice number of points] """
    
    GL.glNewList(displayList, GL.GL_COMPILE)
    xData = []
    yData = []
    for contour in contourData:
      GL.glBegin(GL.GL_LINE_LOOP)
      n = len(contour) // 2

      contour = contour.reshape((n, 2))

      for (x, y) in contour:
        xData.append(x)
        yData.append(y)
        GL.glVertex2f(x,y)

      GL.glEnd()

    GL.glEndList()

    
  # def getTranslateScale(self, dim, ind:int):
  def _getTranslateScale(self, ind:int, pixelViewBox0:float=None, pixelViewBox1:float=None):
    """Get translation data for X (ind==0) or Y (ind==1) dimension"""

    # dataDim = self._apiStripSpectrumView.spectrumView.orderedDataDims[ind]
    # valueToPoint = dataDim.primaryDataDimRef.valueToPoint

    axisIndex = self._displayOrderSpectrumDimensionIndices[ind]
    valueToPoint = self.spectrum.mainSpectrumReferences[axisIndex].valueToPoint
        
    strip = self.strip
    plotWidget = strip.plotWidget
    plotItem = plotWidget.plotItem
    viewBox = strip.viewBox
    viewRegion = plotWidget.viewRange()
    region1, region0 = viewRegion[ind]  # TBD: relies on axes being backwards

    if pixelViewBox0 is None: # should then also have pixelViewBox1 = None
      if ind == 0:
        pixelCount = plotWidget.width()
        pixelViewBox0 = plotItem.getAxis('left').width()
        pixelViewBox1 = pixelViewBox0 + viewBox.width()
      else:
        pixelCount = plotWidget.height()
        pixelViewBox0 = plotItem.getAxis('bottom').height()
        pixelViewBox1 = pixelViewBox0 + viewBox.height()

    # -1 below because points start at 1 in data model
    firstPoint = valueToPoint(region0) - 1
    lastPoint = valueToPoint(region1) - 1
    # (firstPoint, lastPoint) = self.spectrum.getDimPointFromValue(dim, (region0, region1))

    scale = (pixelViewBox1-pixelViewBox0) / (lastPoint-firstPoint)
    translate = pixelViewBox0 - firstPoint * scale

    # dataDim2 should be same as dataDim
    # position, width, totalPointCount, minAliasedFrequency, maxAliasedFrequency, dataDim2 = (
    #   self._getSpectrumViewParams(ind))
    viewParams = self._getSpectrumViewParams(ind)
    
    # -1 below because points start at 1 in data model
    clipPoint0 = int(math.floor(max(firstPoint, valueToPoint(viewParams.maxAliasedFrequency)-1)))
    clipPoint1 = int(math.ceil(min(lastPoint, valueToPoint(viewParams.minAliasedFrequency)-1)))

    return translate, scale, viewParams.totalPointCount, clipPoint0, clipPoint1

  def refreshData(self):

    if self.displayPositiveContours:
      posLevels = _getLevels(self.positiveContourCount, self.positiveContourBase, self.positiveContourFactor)
    else:
      posLevels = []

    if self.displayNegativeContours:
      negLevels = _getLevels(self.negativeContourCount, self.negativeContourBase, self.negativeContourFactor)
    else:
      negLevels = []

    if not posLevels and not negLevels:
      return

    # the makeCurrent() happens automatically when Qt itself calls paint() but here we need to do it
    self.strip.plotWidget.viewport().makeCurrent()

    self._constructContours(posLevels, negLevels, doRefresh=True)
