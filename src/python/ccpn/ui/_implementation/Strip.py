"""
GUI Display Strip class
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:41 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from typing import Sequence, Tuple, List
from PyQt4 import QtGui, Qt, QtCore
from ccpn.util import Common as commonUtil
from ccpn.core.Peak import Peak
from ccpn.core.Spectrum import Spectrum
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.ui._implementation.SpectrumDisplay import SpectrumDisplay
from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import BoundStrip as ApiBoundStrip
from ccpn.util.Logging import getLogger

class Strip(AbstractWrapperObject):
  """Display Strip for 1D or nD spectrum"""
  
  #: Short class name, for PID.
  shortClassName = 'GS'
  # Attribute it necessary as subclasses must use superclass className
  className = 'Strip'

  _parentClass = SpectrumDisplay

  #: Name of plural link to instances of class
  _pluralLinkName = 'strips'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = ApiBoundStrip._metaclass.qualifiedName()
  

  # CCPN properties  
  @property
  def _apiStrip(self) -> ApiBoundStrip:
    """ CCPN Strip matching Strip"""
    return self._wrappedData

  @property
  def _key(self) -> str:
    """id string - serial number converted to string"""
    return str(self._wrappedData.serial)

  @property
  def serial(self) -> int:
    """serial number of Strip, used in Pid and to identify the Strip. """
    return self._wrappedData.serial
    
  @property
  def _parent(self) -> SpectrumDisplay:
    """SpectrumDisplay containing strip."""
    return self._project._data2Obj.get(self._wrappedData.spectrumDisplay)

  spectrumDisplay = _parent

  @property
  def axisCodes(self) ->  Tuple[str, ...]:
    """Fixed string Axis codes in original display order (X, Y, Z1, Z2, ...)"""
    # TODO axisCodes shold be unique, but I am not sure this is enforced
    return self._wrappedData.axisCodes

  @property
  def axisOrder(self) ->  Tuple[str, ...]:
    """String Axis codes in display order (X, Y, Z1, Z2, ...), determine axis display order"""
    return self._wrappedData.axisOrder

  @axisOrder.setter
  def axisOrder(self, value:Sequence):
    self._wrappedData.axisOrder = value

  @property
  def positions(self) ->  Tuple[float, ...]:
    """Axis centre positions, in display order"""
    return self._wrappedData.positions

  @positions.setter
  def positions(self, value):
    self._wrappedData.positions = value

  @property
  def widths(self) ->  Tuple[float, ...]:
    """Axis display widths, in display order"""
    return self._wrappedData.widths

  @widths.setter
  def widths(self, value):
    self._wrappedData.widths = value

  @property
  def units(self) ->  Tuple[str, ...]:
    """Axis units, in display order"""
    return self._wrappedData.units

  @property
  def spectra(self) -> Tuple[Spectrum]:
    """The spectra attached to the strip (whether display is currently turned on  or not)"""
    return tuple (x.spectrum for x in self.spectrumViews)

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:SpectrumDisplay)-> list:
    """get wrappedData (ccpnmr.gui.Task.Strip) in serial number order"""
    return parent._wrappedData.sortedStrips()

  def _getWidgetFromLayout(self):
    ccpnStrip = self._wrappedData
    n = len(ccpnStrip.spectrumDisplay.strips)
    if n > 1:
      index = ccpnStrip.index
      spectrumDisplay = self.spectrumDisplay
      layout = spectrumDisplay.stripFrame.layout()

      if layout:
        lRows = layout.rowCount()
        currentStripItem = None

        for r in range(layout.rowCount()):
          items = []
          if spectrumDisplay.stripDirection == 'Y':
            currentStripItem = layout.itemAtPosition(r, index)
          elif spectrumDisplay.stripDirection == 'X':
            currentStripItem = layout.itemAtPosition(index, 0)

        return currentStripItem
    else:
      raise ValueError("The last strip in a display cannot be deleted")

  def _removeFromLayout(self):

    ccpnStrip = self._wrappedData
    n = len(ccpnStrip.spectrumDisplay.orderedStrips)
    if n > 1:

      _undo = self.project._undo
      if _undo is not None:
        _undo.increaseBlocking()

      index = ccpnStrip.index
      spectrumDisplay = self.spectrumDisplay
      layout = spectrumDisplay.stripFrame.layout()

      if layout:  # should always be the case but play safe
        # remove the item for this strip from the layout
        # and shuffle "higher" items down in the layout
        # (by removing them and then adding them back in)

        lRows = layout.rowCount()
        currentStripItem = None   # use these for undelete
        currentStripDirection = None
        currentRow = 0
        currentIndex = 0
        currentPlotWidget = None
        currentToolbar = None
        currentParent = None
        currentScene = None
        currentViewBox = None

        for r in range(layout.rowCount()):
          self._widgets = []
          if spectrumDisplay.stripDirection == 'Y':

            currentStripItem = self
            currentRow = r
            currentIndex = index
            currentParent = self.parent()
            currentStripDirection = spectrumDisplay.stripDirection

            widgets = [oS for oS in self.spectrumDisplay.orderedStrips]
            widgets.remove(self)
            while layout.count():     # clear the layout
              layout.takeAt(0)
            for m, widgStrip in enumerate(widgets):   # make again
              layout.addWidget(widgStrip, r, m)
            self._project._appBase.ui.mainWindow._TESTFRAME.layout().addWidget(self)
            self.setParent(self._project._appBase.ui.mainWindow._TESTFRAME)

            # currentStripItem = layout.itemAtPosition(r, index)    # hmm, should be None
            # if currentStripItem:
            #   currentParent = self.parent()
            #   # self._project._appBase.ui.mainWindow._TESTFRAME.layout().addItem(currentStripItem)
            #   # self.setParent(self._project._appBase.ui.mainWindow._TESTFRAME)              # completely remove from layout
            #
            #   currentRow = r
            #   currentIndex = index
            #   currentStripDirection = spectrumDisplay.stripDirection
            #   layout.removeItem(currentStripItem)
            #   self._project._appBase.ui.mainWindow._TESTFRAME.layout().addWidget(currentStripItem.widget())
            #   self.setParent(self._project._appBase.ui.mainWindow._TESTFRAME)
            #
            # for m in range(index, n):
            #   item = layout.itemAtPosition(r, m)
            #   if m > index and item:
            #     self._widgets.append(item.widget())
            #     layout.removeItem(item)               # remove items to the right
            # for m, widg in enumerate(self._widgets):        # re-insert them one to the left
            #   layout.addWidget(widg, r, m + index)
            #   # layout.addWidget(item.widget(), r, m + index)

          elif spectrumDisplay.stripDirection == 'X':
            pass

            # currentStripItem = layout.itemAtPosition(index, 0)
            # self._project._appBase.ui.mainWindow._TESTFRAME.layout().addItem(currentStripItem)
            # if currentStripItem:
            #
            #   # TODO:ED this needs to match above
            #   currentParent = currentStripItem.parent()
            #   currentRow = index
            #   currentIndex = 0
            #   currentStripDirection = spectrumDisplay.stripDirection
            #
            # for m in range(index, n):
            #   item = layout.itemAtPosition(m, 0)
            #   if m > index:
            #     if item:
            #       items.append(item)
            #   layout.removeItem(item)               # remove items below
            # for m, item in enumerate(items):        # re-insert them one above
            #   layout.addItem(item, m + index, 0)

        # currentScene = self.plotWidget.scene()
        # # self.plotWidget.setScene(None)
        # currentPlotWidget = self.plotWidget
        # # self.plotWidget = None
        # currentViewBox = self.viewBox
        # # self.viewBox = None

        ###self.spinSystemLabel.deleteLater()
        # if hasattr(self, 'planeToolbar'):
        #   # self.planeToolbar.deleteLater()
        #   currentToolbar = self.planeToolbar
        #   self.planeToolbar = None

        _stripDeleteDict = {'currentRow': currentRow
                            , 'currentIndex': currentIndex
                            , 'currentStripDirection': currentStripDirection
                            , 'currentPlotWidget': currentPlotWidget
                            , 'currentScene': currentScene
                            , 'currentStripItem': currentStripItem
                            , 'currentParent': currentParent
                            , 'currentToolbar':currentToolbar
                            , 'currentViewBox':currentViewBox}

        # store the old information
        ccpnStrip.__dict__['_stripDeleteDict'] = _stripDeleteDict
        if currentStripItem:
          print ('>>> removeFromLayout')
          print ('>>> currentRow:           ', currentRow)
          print ('>>> currentIndex:         ', currentIndex)
          print ('>>> currentStripDirection:', currentStripDirection)
          print ('>>> currentPlotWidget:    ', currentPlotWidget)
          print ('>>> currentScene:         ', currentScene)
          print ('>>> currentStripItem:     ', currentStripItem)
          print ('>>> currentParent:        ', currentParent)
          print ('>>> currentToolbar:       ', currentToolbar)
          print ('>>> currentViewBox:       ', currentViewBox)

      _undo = self.project._undo
      if _undo is not None:
        _undo.decreaseBlocking()

    else:
      raise ValueError("The last strip in a display cannot be deleted")

  def _restoreToLayout(self):
    ccpnStrip = self._wrappedData
    n = len(ccpnStrip.spectrumDisplay.orderedStrips)

    index = ccpnStrip.index
    spectrumDisplay = self.spectrumDisplay
    layout = spectrumDisplay.stripFrame.layout()

    if layout:

      _undo = self.project._undo
      if _undo is not None:
        _undo.increaseBlocking()

      _stripDeleteDict = ccpnStrip.__dict__['_stripDeleteDict']

      currentStripItem = _stripDeleteDict['currentStripItem']
      currentStripDirection = _stripDeleteDict['currentStripDirection']
      currentRow = _stripDeleteDict['currentRow']
      currentIndex = _stripDeleteDict['currentIndex']
      currentPlotWidget = _stripDeleteDict['currentPlotWidget']
      currentScene = _stripDeleteDict['currentScene']
      currentToolbar = _stripDeleteDict['currentToolbar']
      currentParent = _stripDeleteDict['currentParent']
      currentViewBox = _stripDeleteDict['currentViewBox']

      if currentStripItem:
        print('>>> RestoreFromLayout')
        print('>>> currentRow:           ', currentRow)
        print('>>> currentIndex:         ', currentIndex)
        print('>>> currentStripDirection:', currentStripDirection)
        print('>>> currentPlotWidget:    ', currentPlotWidget)
        print('>>> currentScene:         ', currentScene)
        print('>>> currentStripItem:     ', currentStripItem)
        print('>>> currentParent:        ', currentParent)
        print('>>> currentToolbar:       ', currentToolbar)
        print('>>> currentViewBox:       ', currentViewBox)

      for r in range(layout.rowCount()):
        self._widgets = []
        if spectrumDisplay.stripDirection == 'Y' and currentStripDirection == 'Y':

          self._project._appBase.ui.mainWindow._TESTFRAME.layout().removeWidget(self)
          self.setParent(currentParent)

          widgets = [oS for oS in self.spectrumDisplay.orderedStrips]
          widgets.insert(index, self)
          while layout.count():  # clear the layout
            layout.takeAt(0)
          for m, widgStrip in enumerate(widgets):  # make again
            layout.addWidget(widgStrip, r, m)

          # reinsert back into the orderedStrips
          # self.spectrumDisplay.stripCount += 1
          # self.spectrumDisplay.orderedStrips = widgets

          count = ccpnStrip.spectrumDisplay.__dict__
          field = ccpnStrip.spectrumDisplay._fieldNames
          strippy = ccpnStrip.spectrumDisplay.getOrderedStrips()
          print ('>>> count')
          print ('>>> orderedStrips')
          ccpnStrip.spectrumDisplay.newBoundStrip = [appWidg._wrappedData for appWidg in widgets]
          # self.spectrumDisplay.orderedStrips = widgets

            # # TODO:ED check why columnCount is too big
          # # col = layout.columnCount()
          # for m in range(currentIndex, n):
          #   item = layout.itemAtPosition(r, m)
          #   if item:
          #     self._widgets.append(item.widget())
          #     print ('>>> moving', m, item)
          #     layout.removeItem(item)               # remove items to the right
          # for m, item in reversed(list(enumerate(self._widgets))):
          #   # layout.addItem(item, r, m + index + 1)
          #   layout.addWidget(item, r, m + index + 1)
          #
          # # layout.addItem(currentStripItem, r, m+index)
          # # textLabel = QtGui.QLabel(text="HERE")
          # # currentStripItem.setWidget(textLabel)
          #
          # widgetStore = self._project._appBase.ui.mainWindow._TESTFRAME.layout()
          # currentStripWidget = widgetStore.itemAt(widgetStore.count()-1).widget()
          # layout.addWidget(currentStripWidget, currentRow, currentIndex)
          # self.setParent(currentParent)

          #TODO:ED error here?
          # currentStripItem.setParent(currentParent)

        elif spectrumDisplay.stripDirection == 'X' and currentStripDirection == 'X':

          for m in range(currentIndex, n):
            item = layout.itemAtPosition(m, 0)
            if item:
              items.append(item)
              print ('>>> moving', m, item)
              layout.removeItem(item)               # remove items below
          for m, item in reversed(list(enumerate(items))):
            layout.addItem(item, m + index + 1, 0)
          layout.addItem(currentStripItem, currentRow, currentIndex)

          #TODO:ED error here?
          # currentStripItem.setParent(currentParent)

      # self.plotWidget = currentPlotWidget
      # ###self.spinSystemLabel.deleteLater()
      # if hasattr(self, 'planeToolbar'):
      #   self.planeToolbar = currentToolbar
      # self.viewBox = currentViewBox
      # self.plotWidget.setScene(currentScene)
      # # self.setParent(currentParent)

      _undo = self.project._undo
      if _undo is not None:
        _undo.decreaseBlocking()

  #TODO:RASMUS: most of this below belongs in the Gui class or even the GuiSpectrumDisplay class (like adding, removing strips)
  #TODO:ED: confer with rasmus and me to refactor while writing tests
  def delete(self):
    """Overrides normal delete"""
    # currentStripItem = self._getWidgetFromLayout()
    # self.setParent(None)

    ccpnStrip = self._wrappedData
    n = len(ccpnStrip.spectrumDisplay.strips)
    if n > 1:
      spectrumDisplay = self.spectrumDisplay
      layout = spectrumDisplay.stripFrame.layout()

      if layout:  # should always be the case but play safe

        self._removeFromLayout()    # adds nothing to the undo stack, so add it below

        _undo = self.project._undo
        if _undo is not None:
          _undo.newItem(self._restoreToLayout, self._removeFromLayout)
        ccpnStrip.delete()

    else:
      raise  ValueError("The last strip in a display cannot be deleted")

  #CCPN functions
  def clone(self):
    """create new strip that duplicates this one, appending it at the end"""
    _undo = self.project._undo
    self._startCommandEchoBlock('cloneStrip')

    if _undo is not None:
      _undo.increaseBlocking()
    stripPos = self.spectrumDisplay.strips.index(self)
    if stripPos == self.spectrumDisplay.stripCount-1:
      stripPos = -1

    try:
      newStrip = self._project._data2Obj.get(self._wrappedData.clone())
    finally:
      self._endCommandEchoBlock()

    if _undo is not None:
      _undo.decreaseBlocking()
      _undo.newItem(self.spectrumDisplay._removeIndexStrip, self.spectrumDisplay.addStrip
                    , undoArgs=(-1,))

      # TODO:ED could include ccpnStrip.delete, ccpnStrip._undelete
      # _undo.newItem(self._wrappedData.delete, self._wrappedData._singleUnDelete)

    return newStrip

  def moveTo(self, newIndex:int):
    """Move strip to index newIndex in orderedStrips"""
    
    currentIndex = self._wrappedData.index
    if currentIndex == newIndex:
      return

    stripCount = self.spectrumDisplay.stripCount

    if newIndex >= stripCount:
      # Put strip at the right, which means newIndex should be stripCount - 1
      if newIndex > stripCount:
        # warning
        self._project._logger.warning(
          "Attempt to copy strip to position %s in display with only %s strips"
          % (newIndex, stripCount))
      newIndex = stripCount - 1

    self._startCommandEchoBlock('moveTo', newIndex)
    try:
      # management of API objects
      self._wrappedData.moveTo(newIndex)
    finally:
      self._endCommandEchoBlock()

    # NB - no echo blocking below, as none of the layout stuff is modeled (?)

    # NBNB TODO - should the stuff below not be moved to the corresponding GUI class?
    # Is there always a layout, regardless of application?

    # management of Qt layout
    # TBD: need to soup up below with extra loop when have tiles
    spectrumDisplay = self.spectrumDisplay
    layout = spectrumDisplay.stripFrame.layout()
    if not layout: # should always exist but play safe:
      return

    for r in range(layout.rowCount()):
      items = []
      if spectrumDisplay.stripDirection == 'Y':
        if currentIndex < newIndex:
          for n in range(currentIndex, newIndex+1):
            item = layout.itemAtPosition(r, n)
            items.append(item)
            layout.removeItem(item)
          items = items[1:] + [items[0]]
          for m, item in enumerate(items):
            layout.addItem(item, r, m+currentIndex, )
        else:
          for n in range(newIndex, currentIndex+1):
            item = layout.itemAtPosition(r, n)
            items.append(item)
            layout.removeItem(item)
          items = [items[-1]] + items[:-1]
          for m, item in enumerate(items):
            layout.addItem(item, r, m+newIndex, )

      elif spectrumDisplay.stripDirection == 'X':
        if currentIndex < newIndex:
          for n in range(currentIndex, newIndex+1):
            item = layout.itemAtPosition(n, 0)
            items.append(item)
            layout.removeItem(item)
          items = items[1:] + [items[0]]
          for m, item in enumerate(items):
            layout.addItem(item, m+currentIndex, 0)
        else:
          for n in range(newIndex, currentIndex+1):
            item = layout.itemAtPosition(n, 0)
            items.append(item)
            layout.removeItem(item)
          items = [items[-1]] + items[:-1]
          for m, item in enumerate(items):
            layout.addItem(item, m+newIndex, 0)

  def resetAxisOrder(self):
    """Reset display to original axis order"""
    self._startCommandEchoBlock('resetAxisOrder')
    try:
      self._wrappedData.resetAxisOrder()
    finally:
      self._endCommandEchoBlock()


  def findAxis(self, axisCode):
    """Find axis"""
    return self._project._data2Obj.get(self._wrappedData.findAxis(axisCode))

  def displaySpectrum(self, spectrum:Spectrum, axisOrder:Sequence=()):
    """
    Display additional spectrum on strip, with spectrum axes ordered according to axisOrder
    """
    # print('Strip.displaySpectrum>>> _finaliseDone', self._finaliseDone, spectrum)
    getLogger().debug('Strip.displaySpectrum>>> _finaliseDone '
                      +str(self._finaliseDone)+' '
                      +str(spectrum))
    if not self._finaliseDone: return

    spectrum = self.getByPid(spectrum) if isinstance(spectrum, str) else spectrum

    dataSource = spectrum._wrappedData
    apiStrip = self._wrappedData
    if apiStrip.findFirstSpectrumView(dataSource=dataSource) is not None:
      getLogger().debug('Strip.displaySpectrum>>> spectrumView is not None')
      return

    displayAxisCodes = apiStrip.axisCodes

    # make axis mapping indices
    if axisOrder and axisOrder != displayAxisCodes:
      # Map axes to axisOrder, and remap to original setting
      ll = commonUtil._axisCodeMapIndices(spectrum.axisCodes, axisOrder)
      mapIndices = [ll[axisOrder.index(x)] for x in displayAxisCodes]
    else:
      # Map axes to original display setting
      mapIndices = commonUtil._axisCodeMapIndices(spectrum.axisCodes, displayAxisCodes)

    if mapIndices is None:
      getLogger().debug('Strip.displaySpectrum>>> mapIndices is None')
      return
      
    # if None in mapIndices[:2]: # make sure that x/y always mapped
    #   return
    if mapIndices[0] is None or mapIndices[1] is None and displayAxisCodes[1] != 'intensity':
      getLogger().debug('Strip.displaySpectrum>>> mapIndices, x/y not mapped')
      return
      
    if mapIndices.count(None) + spectrum.dimensionCount != len(mapIndices):
      getLogger().debug('Strip.displaySpectrum>>> mapIndices, dimensionCount not matching')
      return
      
    # Make dimensionOrdering
    sortedDataDims = dataSource.sortedDataDims()
    dimensionOrdering = []
    for index in mapIndices:
      if index is None:
        dimensionOrdering.append(0)
      else:
        dimensionOrdering.append(sortedDataDims[index].dim)

    # Set stripSerial
    if 'Free' in apiStrip.className:
      # Independent strips
      stripSerial = apiStrip.serial
    else:
      stripSerial = 0


    self._startCommandEchoBlock('displaySpectrum', spectrum, values=locals(),
                                defaults={'axisOrder':()})
    try:
      # Make spectrumView
      obj = apiStrip.spectrumDisplay.newSpectrumView(spectrumName=dataSource.name,
                                                     stripSerial=stripSerial, dataSource=dataSource,
                                                     dimensionOrdering=dimensionOrdering)
    finally:
      self._endCommandEchoBlock()
    result =  self._project._data2Obj[apiStrip.findFirstStripSpectrumView(spectrumView=obj)]
    #
    return result

  def peakIsInPlane(self, peak:Peak) -> bool:
    """is peak in currently displayed planes for strip?"""

    spectrumView = self.findSpectrumView(peak.peakList.spectrum)
    if spectrumView is None:
      return False
    displayIndices = spectrumView._displayOrderSpectrumDimensionIndices
    orderedAxes = self.orderedAxes[2:]

    for ii,displayIndex in enumerate(displayIndices[2:]):
      if displayIndex is not None:
        # If no axis matches the index may be None
        zPosition = peak.position[displayIndex]
        zPlaneSize = 0.
        zRegion = orderedAxes[ii].region
        if zPosition < zRegion[0]-zPlaneSize or zPosition > zRegion[1]+zPlaneSize:
          return False
    #
    return True

    # apiSpectrumView = self._wrappedData.findFirstSpectrumView(
    #   dataSource=peak._wrappedData.peakList.dataSource)
    #
    # if apiSpectrumView is None:
    #   return False
    #
    #
    # orderedAxes = self.orderedAxes
    # for ii,zDataDim in enumerate(apiSpectrumView.orderedDataDims[2:]):
    #   if zDataDim:
    #     zPosition = peak.position[zDataDim.dimensionIndex]
    #     # NBNB W3e do not think this should add anything - the region should be set correctly.
    #     # RHF, WB
    #     # zPlaneSize = zDataDim.getDefaultPlaneSize()
    #     zPlaneSize = 0.
    #     zRegion = orderedAxes[2+ii].region
    #     if zPosition < zRegion[0]-zPlaneSize or zPosition > zRegion[1]+zPlaneSize:
    #       return False
    # #
    # return True

  def peakIsInFlankingPlane(self, peak:Peak) -> bool:
    """is peak in planes flanking currently displayed planes for strip?"""

    spectrumView = self.findSpectrumView(peak.peakList.spectrum)
    if spectrumView is None:
      return False
    displayIndices = spectrumView._displayOrderSpectrumDimensionIndices
    orderedAxes = self.orderedAxes[2:]

    for ii,displayIndex in enumerate(displayIndices[2:]):
      if displayIndex is not None:
        # If no axis matches the index may be None
        zPosition = peak.position[displayIndex]
        zRegion = orderedAxes[ii].region
        zWidth = orderedAxes[ii].width
        if zRegion[0]-zWidth < zPosition < zRegion[0] or zRegion[1] < zPosition < zRegion[1]+zWidth:
          return True
    #
    return False

  def peakPickPosition(self, position:List[float]) -> Tuple[Peak]:
    """Pick peak at position for all spectra currently displayed in strip"""

    result = []

    self._startCommandEchoBlock('peakPickPosition', position)
    self._project.blankNotification()
    try:
      for spectrumView in self.spectrumViews:
        if not spectrumView.peakListViews: # this can happen if no peakLists, so create one
          self._project.unblankNotification() # need this otherwise SideBar does not get updated
          spectrumView.spectrum.newPeakList()
          self._project.blankNotification()
        peakListView = spectrumView.peakListViews[0]
        # TODO: is there some way of specifying which peakListView
        if not peakListView.isVisible():
          continue
        peakList = peakListView.peakList

        peak = peakList.newPeak(position=position)
        # note, the height below is not derived from any fitting
        # but is a weighted average of the values at the neighbouring grid points
        peak.height = spectrumView.spectrum.getPositionValue(peak.pointPosition)
        result.append(peak)
    finally:
      self._endCommandEchoBlock()
      self._project.unblankNotification()

    for peak in result:
      peak._finaliseAction('create')
    #
    return tuple(result)

  def peakPickRegion(self, selectedRegion:List[List[float]]) -> Tuple[Peak]:
    """Peak pick all spectra currently displayed in strip in selectedRegion """

    result = []

    project = self.project
    minDropfactor = project._appBase.preferences.general.peakDropFactor

    self._startCommandEchoBlock('peakPickRegion', selectedRegion)
    self._project.blankNotification()
    try:

      for spectrumView in self.spectrumViews:
        if not spectrumView.isVisible():
          continue
        if not spectrumView.peakListViews: # this can happen if no peakLists, so create one
          self._project.unblankNotification() # need this otherwise SideBar does not get updated
          spectrumView.spectrum.newPeakList()
          self._project.blankNotification()
        peakListView = spectrumView.peakListViews[0]
        # TODO: is there some way of specifying which peakListView
        if not peakListView.isVisible():
          continue
        peakList = peakListView.peakList

        if spectrumView.spectrum.dimensionCount > 1:
          sortedSelectedRegion =[list(sorted(x)) for x in selectedRegion]
          spectrumAxisCodes = spectrumView.spectrum.axisCodes
          stripAxisCodes = self.axisCodes
          sortedSpectrumRegion = [0] * spectrumView.spectrum.dimensionCount

          remapIndices = commonUtil._axisCodeMapIndices(stripAxisCodes, spectrumAxisCodes)
          for n, axisCode in enumerate(spectrumAxisCodes):
            # idx = stripAxisCodes.index(axisCode)
            idx = remapIndices[n]
            sortedSpectrumRegion[n] = sortedSelectedRegion[idx]
          newPeaks = peakList.pickPeaksNd(sortedSpectrumRegion,
                                          doPos=spectrumView.displayPositiveContours,
                                          doNeg=spectrumView.displayNegativeContours,
                                          fitMethod='gaussian', minDropfactor=minDropfactor)
        else:
          # 1D's
          # NBNB This is a change - valuea are now rounded to three decimal places. RHF April 2017
          newPeaks = peakList.pickPeaks1d(selectedRegion[0], sorted(selectedRegion[1]))
          # y0 = startPosition.y()
          # y1 = endPosition.y()
          # y0, y1 = min(y0, y1), max(y0, y1)
          # newPeaks = peakList.pickPeaks1d([startPosition.x(), endPosition.x()], [y0, y1])

        result.extend(newPeaks)

        # # Add the new peaks to selection
        # for peak in newPeaks:
        #   # peak.isSelected = True
        #   self.current.addPeak(peak)

        # for window in project.windows:
        #   for spectrumDisplay in window.spectrumDisplays:
        #     for strip in spectrumDisplay.strips:
        #       spectra = [spectrumView.spectrum for spectrumView in strip.spectrumViews]
        #       if peakList.spectrum in spectra:
        #               strip.showPeaks(peakList)

    finally:
      self._endCommandEchoBlock()
      self._project.unblankNotification()

    for peak in result:
      peak._finaliseAction('create')
    #
    return tuple(result)


# newStrip functions
# We should NOT have any newStrip function, except possibly for FreeStrips
def _copyStrip(self:SpectrumDisplay, strip:Strip, newIndex=None) -> Strip:
  """Make copy of strip in self, at position newIndex - or rightmost"""

  strip = self.getByPid(strip) if isinstance(strip, str) else strip

  stripCount = self.stripCount
  if newIndex and newIndex >= stripCount:
    # Put strip at the right, which means newIndex should be None
    if newIndex > stripCount:
      # warning
      self._project._logger.warning(
        "Attempt to copy strip to position %s in display with only %s strips"
        % (newIndex, stripCount))
    newIndex = None

  self._startCommandEchoBlock('copyStrip', strip, values=locals(), defaults={'newIndex':None},
                              parName='newStrip')
  try:
    if strip.spectrumDisplay is self:
      # Within same display. Not that useful, but harmless
      newStrip = strip.clone()
      if newIndex is not None:
        newStrip.moveTo(newIndex)

    else:
      mapIndices = commonUtil._axisCodeMapIndices(strip.axisOrder, self.axisOrder)
      if mapIndices is None:
        raise ValueError("Strip %s not compatible with window %s" % (strip.pid, self.pid))
      else:
        positions = strip.positions
        widths = strip.widths
        newStrip = self.orderedStrips[0].clone()
        if newIndex is not None:
          newStrip.moveTo(newIndex)
        for ii,axis in enumerate(newStrip.orderedAxes):
          ind = mapIndices[ii]
          if ind is not None and axis._wrappedData.axis.stripSerial != 0:
            # Override if there is a mapping and axis is not shared for all strips
            axis.position = positions[ind]
            axis.widths = widths[ind]
  finally:
    self._endCommandEchoBlock()
  #
  return newStrip
SpectrumDisplay.copyStrip = _copyStrip
del _copyStrip

#TODO:RASMUS: if this is a SpectrumDisplay thing, it should not be here
# SpectrumDisplay.orderedStrips property
def getter(self) -> Tuple[Strip, ...]:
  ff = self._project._data2Obj.get
  return tuple(ff(x) for x in self._wrappedData.orderedStrips)
def setter(self, value:Sequence):
  value = [self.getByPid(x) if isinstance(x, str) else x for x in value]
  self._wrappedData.orderedStrips = tuple(x._wrappedData for x in value)
SpectrumDisplay.orderedStrips = property(getter, setter, None,
                                         "ccpn.Strips in displayed order ")
del getter
del setter

# SHOULD NOT BE HERE like this
# Drag-n-drop functions:
#Strip.processSpectrum = Strip.displaySpectrum
