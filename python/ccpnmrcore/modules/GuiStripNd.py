"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = "$Revision: 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================
__author__ = 'simon'

#from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4 import QtGui, QtCore

from ccpncore.memops import Notifiers

from ccpncore.gui.Icon import Icon
from ccpncore.gui.Button import Button
from ccpncore.gui.Label import Label
from ccpncore.gui.LineEdit import LineEdit
from ccpncore.gui.ToolBar import ToolBar

from ccpncore.util import Colour

from ccpnmrcore.modules.GuiStrip import GuiStrip
###from ccpnmrcore.modules.spectrumItems.GuiPeakListView import PeakNd

class GuiStripNd(GuiStrip):

  def __init__(self):
    GuiStrip.__init__(self, useOpenGL=True)

    ###self.plotWidget.plotItem.setAcceptDrops(True)
    ###self.viewportWidget = QtOpenGL.QGLWidget()
    ###self.plotWidget.setViewport(self.viewportWidget)
    ###self.guiSpectrumDisplay.viewportDict[self.viewportWidget] = self
    ###self.plotWidget.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
    # self.viewBox.menu = self.get2dContextMenu()
    self.viewBox.invertX()
    self.viewBox.invertY()
    
    ###self.region = guiSpectrumDisplay.defaultRegion()
    self.planeLabel = None
    self.axesSwapped = False
    self.colourIndex = 0
    # print(guiSpectrumDisplay)
    # self.fillToolBar()
    self.addSpinSystemLabel()
    self.addPlaneToolbar()
    ###self.setShortcuts()
    for spectrumView in self.spectrumViews:
    #   newSpectrumView = spectrumView
      #if spectrumView not in self.plotWidget.scene().items():
        # newItem = spectrumView
        #self.plotWidget.scene().addItem(spectrumView)
      spectrumView.addSpectrumItem(self)

    # the scene knows which items are in it but they are stored as a list and the below give fast access from API object to QGraphicsItem
    self.peakLayerDict = {}  # peakList --> peakLayer
    self.peakItemDict = {}  # peak --> peakItem
    Notifiers.registerNotify(self.newPeak, 'ccp.nmr.Nmr.Peak', '__init__')
    Notifiers.registerNotify(self.deletedPeak, 'ccp.nmr.Nmr.Peak', 'delete')
    for func in ('setPosition', 'setWidth'):
      Notifiers.registerNotify(self.axisRegionChanged, 'ccpnmr.gui.Task.Axis', func)
    
  """
  def showSpectrum(self, guiSpectrumView):
    orderedAxes = self.strip.orderedAxes
    self.xAxis = orderedAxes[0]
    self.yAxis = orderedAxes[1]
    self.zAxis = orderedAxes[2:]
    apiDataSource = guiSpectrumView.dataSource

    newItem = self.scene().addItem(guiSpectrumView)
"""

  def mouseDragEvent(self, event):
    if event.button() == QtCore.Qt.RightButton:
        print(event)
    else:
        self.viewBox.mouseDragEvent(self, event)

  # def displayASpectrum(self, guiSpectrumView):
  #
  #   # resetAllAxisCodes(self.project._wrappedData)
  #   # spectrum = self.getObject(spectrumVar)
  #   # if spectrum.dimensionCount < 1:
  #   #   # TBD: logger message
  #   #   return
  #   #
  #   # # TBD: check if dimensions make sense
  #   # self.posColors = list(SPECTRUM_COLOURS.keys())[self.colourIndex]
  #   # self.negColors = list(SPECTRUM_COLOURS.keys())[self.colourIndex+1]
  #   # # if len(self.spectrumItems) >= 1:
  #   # #   if self.spectrumItems[0].spectrum.axisCodes == spectrum.axisCodes:
  #   # #     spectrumItem = SpectrumNdItem(self, spectrum, self.spectrumItems[0].dimMapping, self.region, self.posColors, self.negColors)
  #   # #     self.spectrumItems[0].spectrum.axisCodes
  #   # #   else:
  #   # #     print('Axis codes do not match pane')
  #   # #     return
  #   # #
  #   # # else:
  #   # spectrumItem = GuiSpectrumViewNd(self, spectrum, dimMapping, self.region, self.posColors, self.negColors)
  #
  #   # Changed to guiSpectrumView.positiveContourColour, which picks up from either
  #   # SpectrumView or DataSource
  #   if not guiSpectrumView.positiveContourColour:
  #     apiDataSource.positiveContourColour = Colour.spectrumHexColours[self.colourIndex]
  #     self.colourIndex += 1
  #     self.colourIndex %= len(Colour.spectrumHexColours)
  #
  #   if not guiSpectrumView.negativeContourColour:
  #   # Changed to guiSpectrumView.negativeContourColour, which picks up from either
  #   # SpectrumView or DataSource
  #     apiDataSource.negativeContourColour = Colour.spectrumHexColours[self.colourIndex]
  #     self.colourIndex += 1
  #     self.colourIndex %= len(Colour.spectrumHexColours)
  #
  #   self.scene().addItem(guiSpectrumView)

    # resetAllAxisCodes(self.project._wrappedData)
    # spectrum = self.getObject(spectrumVar)
    # if spectrum.dimensionCount < 1:
    #   # TBD: logger message
    #   return
    #
    # # TBD: check if dimensions make sense
    # self.posColors = list(SPECTRUM_COLOURS.keys())[self.colourIndex]
    # self.negColors = list(SPECTRUM_COLOURS.keys())[self.colourIndex+1]
    # # if len(self.spectrumItems) >= 1:
    # #   if self.spectrumItems[0].spectrum.axisCodes == spectrum.axisCodes:
    # #     spectrumItem = SpectrumNdItem(self, spectrum, self.spectrumItems[0].dimMapping, self.region, self.posColors, self.negColors)
    # #     self.spectrumItems[0].spectrum.axisCodes
    # #   else:
    # #     print('Axis codes do not match pane')
    # #     return
    # #
    # # else:
    # spectrumItem = GuiSpectrumViewNd(self, spectrum, dimMapping, self.region, self.posColors, self.negColors)

  def changeZPlane(self, planeCount=None, position=None):

    zAxis = self.orderedAxes[2]
    smallest = None
    #take smallest inter-plane distance
    for spectrumItem in self._parent.spectrumViews:
      zPlaneSize = spectrumItem.zPlaneSize()
      if zPlaneSize is not None:
        if smallest is None or zPlaneSize < smallest:
          smallest = zPlaneSize

    if smallest is None:
      smallest = 1.0 # arbitrary
    #
    if planeCount:
      delta = smallest * planeCount
      zAxis.position = zAxis.position+delta
    if position:
      zAxis.position = position
    self.planeLabel.setText('%.3f' % zAxis.position)

  def nextZPlane(self):

    self.changeZPlane(planeCount=-1) # -1 because ppm units are backwards

  def prevZPlane(self):

    self.changeZPlane(planeCount=1) # -1 because ppm units are backwards

  # def fillToolBar(self):
  #   spectrumUtilToolBar =  self.guiSpectrumDisplay.spectrumUtilToolBar
  #   plusOneAction = spectrumUtilToolBar.addAction("+1", self.addOne)
  #   plusOneIcon = Icon('icons/contourAdd')
  #   plusOneAction.setIcon(plusOneIcon)
  #   plusOneAction.setToolTip('Add One Level')
  #   minusOneAction = spectrumUtilToolBar.addAction("+1", self.subtractOne)
  #   minusOneIcon = Icon('icons/contourRemove')
  #   minusOneAction.setIcon(minusOneIcon)
  #   minusOneAction.setToolTip('Remove One Level ')
  #   upBy2Action = spectrumUtilToolBar.addAction("*1.4", self.upBy2)
  #   upBy2Icon = Icon('icons/contourBaseUp')
  #   upBy2Action.setIcon(upBy2Icon)
  #   upBy2Action.setToolTip('Raise Contour Base Level')
  #   downBy2Action = spectrumUtilToolBar.addAction("*1.4", self.downBy2)
  #   downBy2Icon = Icon('icons/contourBaseDown')
  #   downBy2Action.setIcon(downBy2Icon)
  #   downBy2Action.setToolTip('Lower Contour Base Level')
  #   storeZoomAction = spectrumUtilToolBar.addAction("Store Zoom", self.storeZoom)
  #   storeZoomIcon = Icon('icons/zoom-store')
  #   storeZoomAction.setIcon(storeZoomIcon)
  #   storeZoomAction.setToolTip('Store Zoom')
  #   restoreZoomAction = spectrumUtilToolBar.addAction("Restore Zoom", self.restoreZoom)
  #   restoreZoomIcon = Icon('icons/zoom-restore')
  #   restoreZoomAction.setIcon(restoreZoomIcon)
  #   restoreZoomAction.setToolTip('Restore Zoom')
  #
  # def upBy2(self):
  #   for spectrumItem in self.spectrumItems:
  #     spectrumItem.baseLevel*=1.4
  #     spectrumItem.levels = spectrumItem.getLevels()
  #
  # def downBy2(self):
  #   for spectrumItem in self.spectrumItems:
  #     spectrumItem.baseLevel/=1.4
  #     spectrumItem.levels = spectrumItem.getLevels()
  #
  # def addOne(self):
  #   self.current.spectrum.spectrumItem.numberOfLevels +=1
  #   self.current.spectrum.spectrumItem.levels = self.current.spectrum.spectrumItem.getLevels()
  #
  #
  # def subtractOne(self):
  #   self.current.spectrum.spectrumItem.numberOfLevels -=1
  #   self.current.spectrum.spectrumItem.levels = self.current.spectrum.spectrumItem.getLevels()

  def addPlaneToolbar(self):

    # if self._parent.spectrumViews[0]
    if len(self.orderedAxes) > 2:
      for i in range(len(self.orderedAxes)-2):
        self.planeToolbar = ToolBar(self.stripFrame, grid=(1+i, self.guiSpectrumDisplay.orderedStrips.index(self)), hAlign='center')
        self.planeToolbar.setMinimumWidth(200)
        # self.spinSystemLabel = Label(self)
        # self.spinSystemLabel.setMaximumWidth(1150)
        # self.spinSystemLabel.setScaledContents(True)
        prevPlaneButton = Button(self,'<', callback=self.prevZPlane)
        prevPlaneButton.setFixedWidth(30)
        prevPlaneButton.setFixedHeight(30)
        self.planeLabel = LineEdit(self)
        self.planeLabel.setFixedHeight(30)
        self.planeLabel.setText('%.3f' % self.positions[2])
        # self.axisCodeLabel = Label(self, text=spectrum.axisCodes[spectrumItem.dimMapping[2]])
        # self.planeLabel.textChanged.connect(self.changeZPlane)
        nextPlaneButton = Button(self,'>', callback=self.nextZPlane)
        nextPlaneButton.setFixedWidth(30)
        nextPlaneButton.setFixedHeight(30)
        self.planeToolbar.setContentsMargins(0,0,0,0)
        self.planeToolbar.addWidget(prevPlaneButton)
        self.planeToolbar.addWidget(self.planeLabel)
        self.planeToolbar.addWidget(nextPlaneButton)

  def showPeaks(self, peakList, peaks=None):
    from ccpnmrcore.modules.spectrumItems.GuiPeakListView import GuiPeakListView
    
    if not peaks:
      peaks = peakList.peaks
      
    peakLayer = self.peakLayerDict.get(peakList)
    if not peakLayer:
      peakLayer = GuiPeakListView(self.plotWidget.scene(), self, peakList)
      self.viewBox.addItem(peakLayer)
      self.peakLayerDict[peakList] = peakLayer
    #rectItem = QtGui.QGraphicsRectItem(5, 120, 2, 10, peakLayer, self.plotWidget.scene())
    ##color = QtGui.QColor('red')
    #rectItem.setBrush(QtGui.QBrush(color))
    #rectItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
    #rectItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
    ##lineItem = QtGui.QGraphicsLineItem(5, 120, 7, 130, peakLayer, self.plotWidget.scene())
    ##pen = QtGui.QPen()
    ##pen.setWidth(0.1)
    ##pen.setBrush(color)
    ##lineItem.setPen(pen)
    ##lineItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
    
    peaks = [peak for peak in peaks if self.peakIsInPlane(peak)]
    self.stripFrame.guiSpectrumDisplay.showPeaks(peakLayer, peaks)
    
    ###for peak in peaks:
    ###  if peak not in self.peakItemDict:
    ###    peakItem = PeakNd(self, peak, peakLayer)
    ###    self.peakItemDict[peak] = peakItem
        
     # peakItem = PeakNd(self, peak)
    ###self.plotWidget.addItem(peakLayer)
     # self.plotWidget.addItem((peakItem.annotation))
     
  def peakIsInPlane(self, peak):

    if len(self.orderedAxes) > 2:
      zDim = self.spectrumViews[0].dimensionOrdering[2] - 1
      zPlaneSize = self.spectrumViews[0].zPlaneSize()
      zPosition = peak.position[zDim]

      zRegion = self.orderedAxes[2].region
      if zRegion[0]-zPlaneSize <= zPosition <= zRegion[1]+zPlaneSize:
        return True
      else:
        return False
    else:
      return True
    
  def newPeak(self, apiPeak):
    peak = self._appBase.project._data2Obj[apiPeak]
    if None in peak.position:
      return
    peakList = peak.parent
    self.showPeaks(peakList, [peak])
    
  def deletedPeak(self, apiPeak):
    peak = self._appBase.project._data2Obj[apiPeak]
    peakItem = self.peakItemDict.get(peak)
    if peakItem:
      self.plotWidget.scene().removeItem(peakItem)
      del self.peakItemDict[peak]
      
  def axisRegionChanged(self, apiAxis):
    
    # TBD: other axes
    axis = self._appBase.project._data2Obj[apiAxis]
    if len(self.orderedAxes) == 3 and axis is self.orderedAxes[2]:
      peakLists = self.peakLayerDict.keys()
      for peakList in peakLists:
        peakLayer = self.peakLayerDict[peakList]
        peaks = [peak for peak in peakList.peaks if self.peakIsInPlane(peak)]
        self.stripFrame.guiSpectrumDisplay.showPeaks(peakLayer, peaks)
         