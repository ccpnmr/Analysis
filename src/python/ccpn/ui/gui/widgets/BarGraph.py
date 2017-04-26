import pyqtgraph as pg
from PyQt4 import QtCore, QtGui
import  numpy as np
from pyqtgraph.Point import Point
import ccpn.ui.gui.ViewBox as spectrumViewbox
from ccpn.core.NmrResidue import NmrResidue
from ccpn.ui.gui.widgets.Menu import Menu
from ccpn.ui.gui.widgets.CustomExportDialog import CustomExportDialog
current = []

labelsColor = 'b'
selectedLabelColor = 'g'

#TODO:LUCA: this is most likely yours; update with documentation and check for ViewBox __init__ as it has changed

class BarGraph(pg.BarGraphItem):
  def __init__(self,viewBox = None, xValues=None, yValues=None, objects=None, brush=None, **kw):
    super(BarGraph, self).__init__(**kw)
    '''
    This class allows top draw bars with or without objects.It Needs only xValues and yValues.
    The bar width is by default set to 1.
    The objects are linked to the bars through the label annotations (with setData).
    '''
    # TODO:
    # setObjects in a more general way. Initially implemented only for NmrResidues objects.

    self.viewBox = viewBox
    self.callback = None
    self.trigger = QtCore.pyqtSignal()
    self.xValues = xValues or []
    self.yValues = yValues or []
    self.brush = brush
    self.clicked = None
    self.objects = objects or []
    self.application = QtCore.QCoreApplication.instance()._ccpnApplication

    self.opts = dict(                # setting for BarGraphItem
                    x=self.xValues,
                    x0=self.xValues,
                    x1=self.xValues,
                    height=self.yValues,
                    width=1,
                    pen=self.brush,
                    brush=self.brush,
                    pens=None,
                    brushes=None,
                    )

    self.opts.update(self.opts)
    self.allValues = {}
    self.getValueDict()
    self.labels = []
    self.drawLabels()
    if self.objects:

      self.setObjects(self.objects)

  def setValues(self, xValues, yValues):
      opts = dict(  # setting for BarGraphItem
          x=xValues,
          x0=xValues,
          x1=xValues,
          height=yValues,
          width=1,
          pen=self.brush,
          brush=self.brush,
          pens=None,
          brushes=None,
          )
      self.opts.update(opts)

  def setObjects(self, objects):

    for label in self.labels:
      for object in objects:
        if isinstance(object, NmrResidue):
          nmrResidue = object
          if hasattr(nmrResidue, 'sequenceCode'):

            if nmrResidue.residue:
              if nmrResidue.sequenceCode is not None:
                if str(nmrResidue.sequenceCode) == label.text():
                  label.setData(int(nmrResidue.sequenceCode), object)

        else:
          print('Impossible to set this object to its label. Function implemented only for NmrResidue')



  def getValueDict(self):
    for x, y in zip(self.xValues, self.yValues):
      print(x,y)
      self.allValues.update({x:y})


  def mouseClickEvent(self, event):
    position = event.pos().x()

    self.clicked = int(position)
    if event.button() == QtCore.Qt.LeftButton:
      for label in self.labels:
        if label.text() == str(self.clicked):
          print(label.data(self.clicked))
          self.application.current.nmrResidue = label.data(self.clicked)
          label.setSelected(True)
      event.accept()

  def drawLabels(self):
    '''

    The label Text is the str of the x values and is used to find and set an object to it.
    NB, changing the text to any other str may not set the objects correctly!

    '''
    for key, value in self.allValues.items():
      label = CustomLabel(text=str(key))
      self.viewBox.addItem(label)
      label.setPos(int(key), value)
      self.labels.append(label)






class CustomLabel(QtGui.QGraphicsSimpleTextItem):
  """ A text annotation of a bar.
      """

  def __init__(self, text):

    QtGui.QGraphicsSimpleTextItem.__init__(self)

    self.setText(text)
    font = self.font()
    font.setPointSize(15)
    self.setRotation(-75)
    self.setFont(font)
    self.setFlag(self.ItemIgnoresTransformations+self.ItemIsSelectable)
    self.setToolTip(text)

    self.customObject = self.data(int(self.text()))
    self.application = QtCore.QCoreApplication.instance()._ccpnApplication



  def setCustomObject(self, obj):
    self.customObject = obj
    self.customObject.customLabel = self

  def getCustomObject(self):
    return self.customObject

  def paint(self, painter, option, widget):
    self._selectCurrentNmrResidue()
    QtGui.QGraphicsSimpleTextItem.paint(self, painter, option, widget)

  def _selectCurrentNmrResidue(self):

    if self.data(int(self.text())) is not None:

      if self.application is not None:

        if self.data(int(self.text())) in self.application.current.nmrResidues:

          self.setSelected(True)




class CustomViewBox(pg.ViewBox):
  def __init__(self, *args, **kwds):
    pg.ViewBox.__init__(self, *args, **kwds)
    self.exportDialog = None
    self.addSelectionBox()
    self.application = QtCore.QCoreApplication.instance()._ccpnApplication




  def addSelectionBox(self):
    self.selectionBox = QtGui.QGraphicsRectItem(0, 0, 1, 1)
    self.selectionBox.setPen(pg.functions.mkPen((255, 0, 255), width=1))
    self.selectionBox.setBrush(pg.functions.mkBrush(255, 100, 255, 100))
    self.selectionBox.setZValue(1e9)
    self.addItem(self.selectionBox, ignoreBounds=True)
    self.selectionBox.hide()


  def mouseClickEvent(self, event):

    if event.button() == QtCore.Qt.RightButton :
      event.accept()
      self._raiseContextMenu(event)

    # elif controlLeftMouse(ev):
      # Control-left-click; (de-)select peak and add/remove to selection
      # ev.accept()

    elif event.button() == QtCore.Qt.LeftButton :
      if self.application.current.nmrResidues:
        self.application.current.clearNmrresidues()
      event.accept()
      # self.deselectLabels()



  def mouseDragEvent(self, event):
    """
    Re-implementation of PyQtGraph mouse drag event to allow custom actions off of different mouse
    drag events. Same as spectrum Display. Check Spectrum Display View Box for more documentation.

    """

    xStartPosition = self.mapSceneToView(event.buttonDownPos()).x()
    xEndPosition = self.mapSceneToView(event.pos()).x()
    yStartPosition = self.mapSceneToView(event.buttonDownPos()).y()
    yEndPosition = self.mapSceneToView(event.pos()).y()


    if spectrumViewbox.leftMouse(event):
      # Left-drag: Panning of the view
      pg.ViewBox.mouseDragEvent(self, event)
    elif spectrumViewbox.controlLeftMouse(event):
      labels = [label for label in self.childGroup.childItems() if isinstance(label, CustomLabel)]
      # Control(Cmd)+left drag: selects label
      for label in labels:
        if int(label.pos().x()) in range(int(xStartPosition), int(xEndPosition)):
          if self.inYRange(label.pos().y(), yEndPosition, yStartPosition, ):
            self.application.current.addNmrresidue(label.data(int(label.pos().x())))
            # label.setSelected(True)


      event.accept()
      if not event.isFinish():
        self._resetBoxes()
        spectrumViewbox.ViewBox._updateSelectionBox(self, p1=event.buttonDownPos(), p2=event.pos())
      else:
        self._resetBoxes()

    elif spectrumViewbox.middleMouse(event) or \
        spectrumViewbox.shiftLeftMouse(event) or spectrumViewbox.shiftMiddleMouse(event) \
        or spectrumViewbox.shiftRightMouse(event):
      event.accept()
      if not event.isFinish():
        self._resetBoxes()
        self.updateScaleBox(event.buttonDownPos(), event.pos())
      else:
        self._resetBoxes()
        spectrumViewbox.ViewBox._setView(self, point1=Point(event.buttonDownPos()), point2=Point(event.pos()))

    else:
      self._resetBoxes()
      event.ignore()

  def inYRange(self, yValue, y1, y2):
    if round(y1,3) <= round(yValue,3) <= round(y2,3) :
      return True
    return False

  def getLabels(self):
    return [label for label in self.childGroup.childItems() if isinstance(label, CustomLabel)]

  def updateSelectionFromCurrent(self, current):
    if self.getLabels():
      if self.current.nmrResidues:
         for label in self.getLabels():
           for nmrResidue in self.current.nmrResidues:
             if nmrResidue.sequenceCode is not None:
               if label.data(int(nmrResidue.sequenceCode)):
                 label.setSelected(True)

  def upDateSelections(self, positions):
    if self.getLabels():
      for label in self.getLabels():
        for position in positions:
          print('Not impl')


  def _resetBoxes(self):
    "Reset/Hide the boxes "
    self._successiveClicks = None
    self.selectionBox.hide()
    self.rbScaleBox.hide()

  def _raiseContextMenu(self, ev):

    from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu

    self.contextMenu = Menu('', None, isFloatWidget=True)

    self.addLabelMenu()
    self.viewBoxMenu = ViewBoxMenu(self)
    self.contextMenu._addQMenu(self.viewBoxMenu)

    self.contextMenu.addSeparator()
    self.contextMenu.addAction('Export', self.showExportDialog)
    self.contextMenu.exec_(ev.screenPos().toPoint())

  def addLabelMenu(self):
    self.labelMenu = Menu(parent=self.contextMenu, title='Label Menu')
    self.labelMenu.addItem('Show All',callback=self.showAllLAbels,
                         checked=False, checkable=True,)
    self.labelMenu.addItem('Hide All', callback=self.hideAllLAbels,
                           checked=False, checkable=True,)
    self.labelMenu.addItem('Show Above Threshold', callback=self.showAboveThreshold,
                           checked=False, checkable=True, )

    self.contextMenu._addQMenu(self.labelMenu)


  def getthreshouldLine(self):
    return [tl for tl in self.childGroup.childItems() if isinstance(tl, pg.InfiniteLine)]

  def hideAllLAbels(self):
    if self.getLabels():
      for label in self.getLabels():
        label.hide()

  def showAllLAbels(self):
    if self.getLabels():
      for label in self.getLabels():
        label.show()

  def showAboveThreshold(self):
    if self.getthreshouldLine():
      tl = self.getthreshouldLine()[0]
      yTlPos = tl.pos().y()
      if self.getLabels():
        for label in self.getLabels():
          if label.pos().y() >= yTlPos:
            label.show()
          else:
            label.hide()

  def showExportDialog(self):
      if self.exportDialog is None:
          ### parent() is the graphicsScene
          self.exportDialog = CustomExportDialog(self.scene())
      self.exportDialog.show(self)



#######################################################################################################
####################################      Mock DATA    ################################################
#######################################################################################################

from collections import namedtuple
import random

nmrResidues = []
for i in range(30):
  nmrResidue = namedtuple('nmrResidue', ['sequenceCode'])
  nmrResidue.__new__.__defaults__ = (0,)
  nmrResidue.sequenceCode = int(random.randint(1,300))
  nmrResidues.append(nmrResidue)

x1 = [nmrResidue.sequenceCode for nmrResidue in nmrResidues]
y1 = [(i**random.random())/10 for i in range(len(x1))]


xLows = []
yLows = []

xMids = []
yMids = []

xHighs = []
yHighs = []


for x, y in zip(x1,y1):
    if y <= 0.5:
        xLows.append(x)
        yLows.append(y)
    if y > 0.5 and y <= 1:
        xMids.append(x)
        yMids.append(y)
    if y > 1:
        xHighs.append(x)
        yHighs.append(y)

#######################################################################################################
#################################### Start Application ################################################
#######################################################################################################
#
# app = pg.mkQApp()
#
# customViewBox = CustomViewBox()
#
# plotWidget = pg.PlotWidget(viewBox=customViewBox, background='w')
# customViewBox.setParent(plotWidget)
#
#
#
# xLow = BarGraph(viewBox=customViewBox, xValues=xLows, yValues=yLows, objects=[nmrResidues], brush='r')
# xMid = BarGraph(viewBox=customViewBox, xValues=xMids, yValues=yMids, objects=[nmrResidues], brush='b')
# xHigh = BarGraph(viewBox=customViewBox, xValues=xHighs, yValues=yHighs,objects=[nmrResidues],  brush='g')
#
# customViewBox.addItem(xLow)
# customViewBox.addItem(xMid)
# customViewBox.addItem(xHigh)
#
# xLine = pg.InfiniteLine(pos=max(yLows), angle=0, movable=True, pen='b')
# customViewBox.addItem(xLine)
#
# l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
# l.setParentItem(customViewBox.graphicsItem())
#
# c1 = plotWidget.plot(pen='r', name='low')
# c2 = plotWidget.plot(pen='b', name='mid')
# c3 = plotWidget.plot(pen='g', name='high')
#
# l.addItem(c1, 'low')
# l.addItem(c2, 'mid')
# l.addItem(c3, 'high')
#
# customViewBox.setLimits(xMin=0, xMax=max(x1) + (max(x1) * 0.5), yMin=0, yMax=max(y1) + (max(y1) * 0.5))
#
# customViewBox.setMenuEnabled(enableMenu=False)

# plotWidget.show()
#
#
#
# # Start Qt event
# if __name__ == '__main__':
#   import sys
#   if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#     QtGui.QApplication.instance().exec_()
#
#
#
