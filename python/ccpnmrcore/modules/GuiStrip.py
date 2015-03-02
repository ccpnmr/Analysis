__author__ = 'simon'

import pyqtgraph as pg
import os
from functools import partial

from PySide import QtGui, QtCore

from ccpn import Spectrum
from ccpncore.gui.Label import Label
from ccpncore.gui import ViewBox

from ccpncore.gui.PlotWidget import PlotWidget

from ccpnmrcore.gui.Axis import Axis
from ccpnmrcore.DropBase import DropBase



class GuiStrip(DropBase, PlotWidget): # DropBase needs to be first, else the drop events are not processed

  sigClicked = QtCore.Signal(object, object)

  def __init__(self):
    self.stripFrame = self._parent.stripFrame
    self.guiSpectrumDisplay = self._parent  # NBNB TBD is it worth keeping both?



    # DropBase.__init__(self, self._appBase, self.dropCallback)
    PlotWidget.__init__(self, self.stripFrame, grid=(0, self.guiSpectrumDisplay.stripCount)) #, gridSpan=(1, 1))

    # if self.appBase.preferences.general.colourScheme == 'light':
    #   background = 'w'
    #   foreground = 'k'
    #   print(background)
    # else:
    background = 'k'
    foreground = 'w'
    pg.setConfigOption('background', background)
    pg.setConfigOption('foreground', foreground)
    self.plotWidget.setBackground(background)
    self.setAcceptDrops(True)
    self._appBase = self.guiSpectrumDisplay._appBase
    # self.setForegroundBrush(foreground)

    self.plotItem = self.plotWidget.plotItem
    self.plotItem.setMenuEnabled(enableMenu=True, enableViewBoxMenu=False)
    self.plotItem.setAcceptDrops(True)
    self.axes = self.plotItem.axes
    self.viewBox = self.plotItem.vb
    self.xRegion = self.orderedAxes[0].region
    self.yRegion = self.orderedAxes[1].region
    self.viewBox.setXRange(*self.xRegion)
    self.viewBox.setYRange(*self.yRegion)
    self.xAxis = Axis(self, orientation='top')
    self.yAxis = Axis(self, orientation='left')
    self.gridShown = True
    self.axes['left']['item'].hide()
    self.axes['right']['item'].show()
    self.axes['bottom']['item'].orientation = 'top'
    self.axes['right']['item'].orientation = 'left'
    self.axes['bottom']['item'].setPen(pg.functions.mkPen('w'))
    self.axes['right']['item'].setPen(pg.functions.mkPen('w'))
    self.textItem = pg.TextItem(text=self.orderedAxes[0].code, color=(255, 255, 255), anchor=(0, 1))
    self.textItem.setPos(self.viewBox.boundingRect().bottomLeft())
    self.textItem2 = pg.TextItem(text=self.orderedAxes[1].code, color=(255, 255, 255), anchor=(1, 0))
    self.textItem2.setPos(self.viewBox.boundingRect().topRight())
    self.viewBox.sigStateChanged.connect(self.moveAxisCodeLabels)
    self.plotWidget.scene().addItem(self.textItem)
    self.plotWidget.scene().addItem(self.textItem2)
    self.grid = pg.GridItem()
    self.plotWidget.addItem(self.grid)
    self.setMinimumWidth(200)
    self.createCrossHair()
    proxy = pg.SignalProxy(self.plotWidget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
    self.plotWidget.scene().sigMouseMoved.connect(self.mouseMoved)
    self.plotWidget.scene().sigMouseMoved.connect(self.showMousePosition)
    self.storedZooms = []
    self.addSpinSystemLabel()

  # def addAStrip(self):
  #
  #   newStrip = self.strips[0].clone()
  #   print(newStrip.pid)

  def addSpinSystemLabel(self):
    self.spinSystemLabel = Label(self, grid=(1, 0), hAlign='center', dragDrop=True, pid=self.pid)
    self.spinSystemLabel.setText("Spin systems shown here")
    self.spinSystemLabel.setFixedHeight(30)
    # self.spinSystemLabel.pid = self.pid
    # print(self.pid)

  def moveAxisCodeLabels(self):
    self.textItem.setPos(self.viewBox.boundingRect().bottomLeft())
    self.textItem2.setPos(self.viewBox.boundingRect().topRight())

  def hideCrossHairs(self):
    for strip in self.guiSpectrumDisplay.guiStrips:
      strip.hideCrossHair()

  def createCrossHair(self):
    self.vLine = pg.InfiniteLine(angle=90, movable=False, pen='w')
    self.hLine = pg.InfiniteLine(angle=0, movable=False, pen='w')
    self.plotWidget.addItem(self.vLine, ignoreBounds=True)
    self.plotWidget.addItem(self.hLine, ignoreBounds=True)
    self.guiSpectrumDisplay._appBase.hLines.append(self.hLine)
    self.guiSpectrumDisplay._appBase.vLines.append(self.vLine)

  def toggleCrossHair(self):
    if self.crossHairShown:
      self.hideCrossHair()
    else:
      self.showCrossHair()

  def showCrossHair(self):
      for vLine in self.guiSpectrumDisplay._appBase.vLines:
        vLine.show()
      for hLine in self.guiSpectrumDisplay._appBase.hLines:
        hLine.show()
      self.crossHairAction.setChecked(True)
      self.crossHairShown = True

  def hideCrossHair(self):
    for vLine in self.guiSpectrumDisplay._appBase.vLines:
        vLine.hide()
    for hLine in self.guiSpectrumDisplay._appBase.hLines:
        hLine.hide()
    self.crossHairAction.setChecked(False)
    self.crossHairShown = False

  def toggleGrid(self):
    if self.grid.isVisible():
      self.grid.hide()
    else:
      self.grid.show()

  def mouseMoved(self, event):
    position = event
    if self.plotWidget.sceneBoundingRect().contains(position):
        self.mousePoint = self.viewBox.mapSceneToView(position)
        for vLine in self.guiSpectrumDisplay._appBase.vLines:
          vLine.setPos(self.mousePoint.x())
        for hLine in self.guiSpectrumDisplay._appBase.hLines:
          hLine.setPos(self.mousePoint.y())
    return self.mousePoint

  def showMousePosition(self, pos):
    position = self.viewBox.mapSceneToView(pos).toTuple()
    self.guiSpectrumDisplay.positionBox.setText("X: %.3f  Y: %.3f" % position)

  def zoomToRegion(self, region):
    self.setXRange(region[0],region[1])
    self.setYRange(region[2],region[3])

  def zoomX(self, region):
    self.setXRange(region[0],region[1])

  def zoomY(self, region):
    self.setYRange(region[0],region[1])

  def zoomAll(self):
    self.autoRange()

  def zoomTo(self, x1, x2, y1, y2):
    self.zoomToRegion([float(x1.text()),float(x2.text()),float(y1.text()),float(y2.text())])
    self.zoomPopup.close()

  def raiseZoomPopup(self):
    self.zoomPopup = QtGui.QDialog()
    layout = QtGui.QGridLayout()
    layout.addWidget(QtGui.QLabel(text='x1'), 0, 0)
    x1 = QtGui.QLineEdit()
    layout.addWidget(x1, 0, 1, 1, 1)
    layout.addWidget(QtGui.QLabel(text='x2'), 0, 2)
    x2 = QtGui.QLineEdit()
    layout.addWidget(x2, 0, 3, 1, 1)
    layout.addWidget(QtGui.QLabel(text='y1'), 1, 0,)
    y1 = QtGui.QLineEdit()
    layout.addWidget(y1, 1, 1, 1, 1)
    layout.addWidget(QtGui.QLabel(text='y2'), 1, 2)
    y2 = QtGui.QLineEdit()
    layout.addWidget(y2, 1, 3, 1, 1)
    okButton = QtGui.QPushButton(text="OK")
    okButton.clicked.connect(partial(self.zoomTo,x1,x2,y1,y2))
    cancelButton = QtGui.QPushButton(text='Cancel')
    layout.addWidget(okButton,2, 1)
    layout.addWidget(cancelButton, 2, 3)
    cancelButton.clicked.connect(self.zoomPopup.close)
    self.zoomPopup.setLayout(layout)
    self.zoomPopup.exec_()

  def storeZoom(self):
    self.storedZooms.append(self.viewBox.viewRange())

  def restoreZoom(self):
    if len(self.storedZooms) != 0:
      restoredZoom = self.storedZooms.pop()
      self.setXRange(restoredZoom[0][0], restoredZoom[0][1])
      self.setYRange(restoredZoom[1][0], restoredZoom[1][1])

  def showSpectrum(self, guiSpectrumView):
    raise Exception('should be implemented in subclass')

  def dropCallback(self, dropObject):

    if isinstance(dropObject, Spectrum):
      self.displaySpectrum(dropObject)

    else:
      print(self.guiSpectrumDisplay.strips)
      self.guiSpectrumDisplay.copyStrip(dropObject, newIndex=0)
      print(self.guiSpectrumDisplay.strips)
      # print(dropObject._parent)
      # print('dropObject',dropObject)
      dropObject.deleteLater()
      dropObject.clone()
      # # print(newStrip)
      # print('strip cloned')
    # else:
    #   print('not a spectrum')

