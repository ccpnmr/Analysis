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

# import importlib, os

from PyQt5 import QtWidgets, QtCore

from ccpn.core.Project import Project
from ccpn.core.Peak import Peak
from ccpn.core.PeakList import PeakList
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
#from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.ToolBar import ToolBar

#import typing

from ccpn.ui.gui.widgets.Frame import Frame #, ScrollableFrame
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.PhasingFrame import PhasingFrame
from ccpn.ui.gui.widgets.SpectrumToolBar import SpectrumToolBar
from ccpn.ui.gui.widgets.SpectrumGroupToolBar import SpectrumGroupToolBar
#from ccpn.ui.gui.widgets.Widget import ScrollableWidget, Widget
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea

from ccpn.ui.gui.widgets.MessageDialog import showWarning, showInfo
#from ccpn.ui.gui.widgets.BasePopup import BasePopup
#from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.DropBase import DropBase
from ccpn.ui.gui.lib.GuiNotifier import GuiNotifier

from ccpn.util.Logging import getLogger
from ccpn.core.NmrAtom import NmrAtom
from ccpn.core.NmrResidue import NmrResidue

AXIS_WIDTH = 30


class GuiSpectrumDisplay(CcpnModule):
  """
  Main spectrum display Module object.

  This module inherits the following attributes from the SpectrumDisplay wrapper class:

  title             Name of spectrumDisplay;
                      :return <str>
  stripDirection    Strip axis direction
                      :return <str>:('X', 'Y', None) - None only for non-strip plots
  stripCount        Number of strips
                      :return <str>.
  comment           Free-form text comment
                      comment = <str>
                      :return <str>
  axisCodes         Fixed string Axis codes in original display order
                      :return <tuple>:(X, Y, Z1, Z2, ...)
  axisOrder         String Axis codes in display order, determine axis display order
                      axisOrder = <sequence>:(X, Y, Z1, Z2, ...)
                      :return <tuple>:(X, Y, Z1, Z2, ...)
  is1D              True if this is a 1D display
                      :return <bool>
  window            Gui window showing SpectrumDisplay
                      window = <Window>
                      :return <Window>
  nmrResidue        NmrResidue attached to SpectrumDisplay
                      nmrResidue = <NmrResidue>
                      :return <NmrResidue>
  positions         Axis centre positions, in display order
                      positions = <Tuple>
                      :return <Tuple>
  widths            Axis display widths, in display order
                      widths = <Tuple>
                      :return <Tuple>
  units             Axis units, in display order
                      :return <Tuple>

  parameters        Keyword-value dictionary of parameters.
                      NB the value is a copy - modifying it will not modify the actual data.
                      Values can be anything that can be exported to JSON,
                      including OrderedDict, numpy.ndarray, ccpn.util.Tensor,
                      or pandas DataFrame, Series, or Panel
                      :return <dict>
  setParameter      Add name:value to parameters, overwriting existing entries
                      setParameter(name:str, value)
                        :param name:<str> name of parameter
                        :param value: value to set
  deleteParameter   Delete parameter
                      deleteParameter(name:str)
                        :param name:<str> name of parameter to delete
  clearParameters   Delete all parameters
  updateParameters  Update list of parameters
                      updateParameters(value:dict)
                        :param value:<dict> parameter list

  resetAxisOrder    Reset display to original axis order
  findAxis          Find axis
                      findAxis(axisCode)
                        :param axisCode:
                        :return axis
  """

  # overide in specific module implementations
  includeSettingsWidget = False
  maxSettingsState = 2  # states are defined as: 0: invisible, 1: both visible, 2: only settings visible
  settingsPosition = 'top'
  settingsMinimumSizes = (250, 50)

  def __init__(self, mainWindow, name, useScrollArea=False):
    """
    Initialise the Gui spectrum display object
    
    :param mainWindow: MainWindow instance
    :param name: Title-bar name for the Module
    :param useScrollArea: Having a scrolled widget containing OpenGL and PyQtGraph widgets does not seem to work.
                          The leftmost strip is full of random garbage if it's not completely visible.
                          So for now add option below to have it turned off (False) or on (True).
    """

    getLogger().debug('GuiSpectrumDisplay>> mainWindow, name: %s %s' % (mainWindow, name))
    super(GuiSpectrumDisplay, self).__init__(mainWindow=mainWindow, name=name,
                                             size=(1100, 1300), autoOrientation=False
                                             )
    # print('GuiSpectrumDisplay>> self.layout:', self.layout)

    self.mainWindow = mainWindow
    self.application = mainWindow.application
    # derive current from application
    self.current = mainWindow.application.current
    # cannot set self.project because self is a wrapper object
    # self.project = mainWindow.application.project

    # self.mainWidget will be the parent of all the subsequent widgets
    self.qtParent = self.mainWidget

    # GWV: Not sure what the widget argument is for
    # LM: is the spectrumDisplay, used in the widget to set actions/callbacks to the buttons
    self.spectrumToolBar = SpectrumToolBar(parent=self.qtParent, widget=self,
                                           grid=(0, 0), gridSpan=(1, 6))
    self.spectrumToolBar.setFixedHeight(30)

    # spectrumGroupsToolBar
    self.spectrumGroupToolBar = SpectrumGroupToolBar(parent=self.qtParent, spectrumDisplay=self,
                                                  grid=(0, 0), gridSpan=(1, 6))
    self.spectrumGroupToolBar.setFixedHeight(30)
    self.spectrumGroupToolBar.hide()

    # Utilities Toolbar; filled in Nd/1d classes
    self.spectrumUtilToolBar = ToolBar(parent=self.qtParent, iconSizes=(24,24),
                                       grid=(0, 6), gridSpan=(1, 1),
                                       hPolicy='minimal', hAlign='right')
    #self.spectrumUtilToolBar.setFixedWidth(150)
    self.spectrumUtilToolBar.setFixedHeight(self.spectrumToolBar.height())
    if self.application.preferences.general.showToolbar:
      self.spectrumUtilToolBar.show()
    else:
      self.spectrumUtilToolBar.hide()

    self.stripFrame = Frame(setLayout=True, showBorder=True, spacing=(5,0), stretch=(1,1))

    if useScrollArea:
      # scroll area for strips
      # This took a lot of sorting-out; better leave as is or test thoroughly
      self._stripFrameScrollArea = ScrollArea(parent=self.qtParent, setLayout=False,
                                              scrollBarPolicies = ('always', 'asNeeded'),
                                              acceptDrops=True
                                              )
      self._stripFrameScrollArea.setWidget(self.stripFrame)
      self._stripFrameScrollArea.setWidgetResizable(True)
      self._stripFrameScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      self._stripFrameScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
      self.qtParent.getLayout().addWidget(self._stripFrameScrollArea, 1, 0, 1, 7)
      self.stripFrame.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                    QtWidgets.QSizePolicy.Expanding)
    else:
      self.qtParent.getLayout().addWidget(self.stripFrame, 1, 0, 1, 7)

    includeDirection = not self.is1D
    self.phasingFrame = PhasingFrame(parent=self.qtParent,
                                     showBorder=True,
                                     includeDirection=includeDirection,
                                     callback=self._updatePhasing,
                                     returnCallback=self._updatePivot,
                                     directionCallback=self._changedPhasingDirection,
                                     grid=(2, 0), gridSpan=(1, 7), hAlign='top',
                                     margins=(0,0,0,0), spacing=(0,0))
    self.phasingFrame.setVisible(False)

    self.stripFrame.setAcceptDrops(True)
    self.droppedNotifier = GuiNotifier(self.stripFrame,
                                       [GuiNotifier.DROPEVENT], [DropBase.URLS, DropBase.PIDS],
                                       self._processDroppedItems)

    # GWV: This assures that a 'hoverbar' is visible over the strip when dragging
    # the module to another location
    self.hoverEvent = self._hoverEvent
    self.lastAxisOnly = True

  def _hoverEvent(self, event):
    event.accept()

  def _processDroppedItems(self, data):
    """
    CallBack for Drop events
    
    CCPN INTERNAL: Also called from GuiStrip
    """
    theObject = data.get('theObject')

    if DropBase.URLS in data:
      self.mainWindow.sideBar._processDroppedItems(data)

    # for url in data.get('urls',[]):
    #   getLogger().debug('dropped: %s' % url)
    #   objects = self.project.loadData(url)
    #
    #   if objects is not None:
    #     for obj in objects:
    #       if isinstance(obj, Spectrum):
    #         self._handlePid(obj.pid, theObject)  # pass the object as its pid so we use
    #                                   # the same method used to process the pids

    for pid in data.get('pids',[]):
      getLogger().debug('dropped:', pid)
      self._handlePid(pid, theObject)

  def _handlePid(self, pid, strip=None):
    "handle a; return True in case it is a Spectrum or a SpectrumGroup"
    success = False
    obj = self.project.getByPid(pid)
    if obj is not None and isinstance(obj, Spectrum):
      if self.isGrouped:
        showWarning('Forbidden drop','A Single spectrum cannot be dropped onto grouped displays. Open a new Blank Display (N,D)')
        return success
      self.displaySpectrum(obj)
      if strip in self.strips:
        self.current.strip = strip
      elif self.current.strip not in self.strips:
        self.current.strip = self.strips[0]
      success = True
    elif obj is not None and isinstance(obj, PeakList):
      self._handlePeakList(obj)
    elif obj is not None and isinstance(obj, SpectrumGroup):
      self._handleSpectrumGroup(obj)
    elif obj is not None and isinstance(obj, NmrAtom):
      self._handleNmrAtom(obj)
    elif obj is not None and isinstance(obj, NmrResidue):
      self._handleNmrResidue(obj)
    else:
      showWarning('Dropped item "%s"' % obj.pid, 'Wrong kind; drop Spectrum, SpectrumGroup or PeakList')
    return success

  def _handlePeakList(self, peakList):
    "See if peaklist can be copied"
    spectrum = peakList.spectrum
    #TODO:GEERTEN: Ask rasmus how to match axis codes
    if spectrum.dimensionCount != self.strips[0].spectra[0].dimensionCount or \
      not True: # peakList.spectrum.axisCodes match
      showWarning('Dropped PeakList "%s"' % peakList.pid, 'Cannot copy: Axes do not match')
      return
    else:
      from ccpn.ui.gui.popups.CopyPeakListPopup import CopyPeakListPopup
      popup = CopyPeakListPopup(application=self.application)
      popup.sourcePeakListPullDown.select(peakList.pid)
      popup.exec_()
    # showInfo(title='Copy PeakList "%s"' % peakList.pid, message='Copy to selected spectra')

  def _handleSpectrumGroup(self, spectrumGroup):
    '''
    Add spectrumGroup on the display and its button on the toolBar
    '''
    self.spectrumGroupToolBar._addAction(spectrumGroup)
    for spectrum in spectrumGroup.spectra:
      self.displaySpectrum(spectrum)
    if self.current.strip not in self.strips:
      self.current.strip = self.strips[0]

  def _handleNmrResidue(self, nmrResidue):
    if not self.current.peak:
      self._createNmrResidueMarks(nmrResidue)

    # FIXME THIS IS ONLY A TEST FOR FUN
    if self.current.strip:
      if len(self.current.peaks) ==1:
        peak = self.current.peaks[0]
        xs = self.current.strip.orderedAxes
        for atom in nmrResidue.nmrAtoms:
          for x in xs:
            if x.code == atom.name:
              peak.assignDimension(x.code, atom)

    # if self.current.cursorPosition

  def _processDragEnterEvent(self, data):
    event = data['event']
    mousePosition = event.pos()
    if self.current.strip:
      position = list(self.current.strip._testCcpnOpenGLWidget.mapMouseToAxis(mousePosition))
      orderedAxes = self.current.strip.orderedAxes
      if self.current.peak:
        peakPosition = self.current.peak.position
        minPeakPos = min(peakPosition)
        bw = self.current.strip._testCcpnOpenGLWidget.boxWidth
        bh = self.current.strip._testCcpnOpenGLWidget.boxHeight
        pW = 0
        pH = 0
        if len(peakPosition) > 0:
          pW = peakPosition[0]
        if len(peakPosition)>1:
          pH = peakPosition[1]
        boxW = (pW + bw, pW - bw)
        boxH = (pH + bh, pH - bh)
        if pW + bw>position[0]>pW - bw and  pH + bh >position[1]>pH - bh:
         print()






  def _createNmrResidueMarks(self, nmrResidue):
    """
    Mark a list of nmrAtoms in the spectrum displays
    """
    # showInfo(title='Mark nmrResidue "%s"' % nmrResidue.pid, message='mark nmrResidue in strips')

    from ccpn.AnalysisAssign.modules.BackboneAssignmentModule import nmrAtomsFromResidue, markNmrAtoms

    # get the strips
    # nmrResidue = nmrResidue.mainNmrResidue
    # nmrResidues = []
    # previousNmrResidue = nmrResidue.previousNmrResidue
    # if previousNmrResidue:
    #   nmrResidues.append(previousNmrResidue)
    # nmrResidues.append(nmrResidue)
    # nextNmrResidue = nmrResidue.nextNmrResidue
    # if nextNmrResidue:
    #   nmrResidues.append(nextNmrResidue)
    #
    # nmrAtoms=[]
    #
    # for nr in nmrResidues:
    #   nmrAtoms.extend(nr.nmrAtoms)

    # ejb - just a test, could pass data: if data['shiftLeftMouse']: then clear marks first

    # the below commented code matches backboneassignment, but don't want to do this
    # want to just show what's actually in the nmrResidue
    # if '-1' in nmrResidue.pid:
    #   # -1 residue so need to split the CA, CB from thr N, H
    #   nmrAtomsMinus = nmrAtomsFromResidue(nmrResidue)
    #   nmrAtomsCentre = nmrAtomsFromResidue(nmrResidue.mainNmrResidue)
    #
    #   nmrAtoms = []
    #   # this should check the experiment type and choose the correct atoms
    #   for nac in nmrAtomsMinus:
    #     if '..CA' in nac.pid or '..CB' in nac.pid:
    #       nmrAtoms.append(nac)
    #   for nac in nmrAtomsCentre:
    #     if '..N' in nac.pid or '..H' in nac.pid:
    #       nmrAtoms.append(nac)
    #
    #   markNmrAtoms(mainWindow=self.mainWindow, nmrAtoms=nmrAtoms)
    # else:
    #   nmrAtoms = nmrAtomsFromResidue(nmrResidue.mainNmrResidue)
    #   markNmrAtoms(mainWindow=self.mainWindow, nmrAtoms=nmrAtoms)

    nmrAtoms = nmrAtomsFromResidue(nmrResidue)
    if nmrAtoms:
      markNmrAtoms(self.mainWindow, nmrAtoms)

  def _handleNmrAtom(self, nmrAtom):
    """
    Mark an nmrAtom in the spectrum displays with horizontal/vertical bars
    """
    # showInfo(title='Mark nmrAtom "%s"' % nmrAtom.pid, message='mark nmrAtom in strips')

    from ccpn.AnalysisAssign.modules.BackboneAssignmentModule import markNmrAtoms

    markNmrAtoms(self.mainWindow, [nmrAtom])

  def setScrollbarPolicies(self, horizontal='asNeeded', vertical='asNeeded'):
    "Set the scrolbar policies; convenience to expose to the user"
    from ccpn.ui.gui.widgets.ScrollArea import SCROLLBAR_POLICY_DICT

    if horizontal not in SCROLLBAR_POLICY_DICT or \
       vertical not in SCROLLBAR_POLICY_DICT:
      getLogger().warning('Invalid scrollbar policy (%s, %s)' %(horizontal, vertical))
    self.stripFrame.setScrollBarPolicies((horizontal, vertical))

  def _updatePivot(self):
    """Updates pivot in all strips contained in the spectrum display."""
    for strip in self.strips:
      strip._updatePivot()
    
  def _updatePhasing(self):
    """Updates phasing in all strips contained in the spectrum display."""
    for strip in self.strips:
      strip._updatePhasing()
    
  def _changedPhasingDirection(self):
    """Changes direction of phasing from horizontal to vertical or vice versa."""
    for strip in self.strips:
      strip._changedPhasingDirection()
    
  def togglePhaseConsole(self):
    """Toggles whether phasing console is displayed.
    """
    isVisible = not self.phasingFrame.isVisible()
    self.phasingFrame.setVisible(isVisible)
    for strip in self.strips:
      if isVisible:
        strip.turnOnPhasing()
      else:
        strip.turnOffPhasing()
    self._updatePhasing()

  def showToolbar(self):
    """show the toolbar"""
    # showing the toolbar, but we need to update the checkboxes of all strips as well.
    self.spectrumUtilToolBar.show()
    for strip in self.strips:
      strip.toolbarAction.setChecked(True)

  def hideToolbar(self):
    """hide the toolbar"""
    # hiding the toolbar, but we need to update the checkboxes of all strips as well.
    self.spectrumUtilToolBar.hide()
    for strip in self.strips:
      strip.toolbarAction.setChecked(False)

  def toggleToolbar(self):
    """Toggle the toolbar """
    if not self.spectrumUtilToolBar.isVisible():
      self.showToolbar()
    else:
      self.hideToolbar()

  def _closeModule(self):
    """
    Closes spectrum display and deletes it from the project.
    """
    for strip in self.strips:
      strip._unregisterStrip()
    # self.module.close()
    #self.delete()
    CcpnModule._closeModule(self)
    self.delete()

  def _unDelete(self, strip):
    _undo = self.project._undo
    self._startCommandEchoBlock('removeStrip')
    try:
      strip._unDelete()
    finally:
      self._endCommandEchoBlock()
      self.showAxes()

  def _removeIndexStrip(self, value):
    self.removeStrip(self.strips[value])

  def removeStrip(self, strip):
    "Remove strip if it belongs to self"

    if strip is None:
      showWarning('Remove strip', 'Invalid strip' )
      return

    if strip not in self.strips:
      showWarning('Remove strip', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                  % (strip.pid, self.pid))
      return

    if len(self.orderedStrips) == 1:
      showWarning('Remove strip', 'Last strip of SpectrumDisplay "%s" cannot be removed' \
                  % (self.pid,))
      return

    _undo = self.project._undo
    self._startCommandEchoBlock('removeStrip')

    # if _undo is not None:
    #   _undo.increaseBlocking()

    try:
      # strip._unregisterStrip()
      self.current.strip = None
      self.setColumnStretches(stretchValue=False)      # set to 0 so they disappear
      # this removes it too early
      # strip.setParent(None)           # need to remove the rogue widget from the widgetArea
      strip.delete()
      self.setColumnStretches(stretchValue=True)      # set to 0 so they disappear

      # update the 'orderedSpectra' list
      # TODO:ED update the orderedSpectra list
      # self.removeSpectrumView(None)

    finally:
      self._endCommandEchoBlock()

    # if _undo is not None:
    #   _undo.decreaseBlocking()
    #
    #   # TODO:ED this may not be the correct strip to Redo:remove
    #   _undo.newItem(self.addStrip, self._removeIndexStrip, redoArgs=(-1,))

    self.showAxes()

  def removeCurrentStrip(self):
    "Remove current.strip if it belongs to self"
    if self.current.strip is None:
      showWarning('Remove current strip', 'Select first in SpectrumDisplay by clicking')
      return
    self.removeStrip(self.current.strip)

  # def duplicateStrip(self):
  #   """
  #   Creates a new strip identical to the last one created and adds it to right of the display.
  #   """
  #   newStrip = self.strips[-1].clone()

  # def addStrip(self, stripIndex=-1) -> 'GuiStripNd':

  def setLastAxisOnly(self, lastAxisOnly:bool=True):
    self.lastAxisOnly = lastAxisOnly

  def showAxes(self):
    if self.strips:
      if self.lastAxisOnly:
        for ss in self.strips[:-1]:
          ss.plotWidget.plotItem.axes['right']['item'].hide()
          try:
            ss._testCcpnOpenGLWidget.setRightAxisVisible(axisVisible=False)
          except Exception as es:
            getLogger().debug('Error: OpenGL widget not instantiated')

        self.strips[-1].plotWidget.plotItem.axes['right']['item'].show()

        try:
          self.strips[-1]._testCcpnOpenGLWidget.setRightAxisVisible(axisVisible=True)
        except Exception as es:
          getLogger().debug('Error: OpenGL widget not instantiated')

      else:
        for ss in self.strips:
          ss.plotWidget.plotItem.axes['right']['item'].show()
          try:
            ss._testCcpnOpenGLWidget.setRightAxisVisible(axisVisible=True)
          except Exception as es:
            getLogger().debug('Error: OpenGL widget not instantiated')

      self.setColumnStretches(True)

  def increaseStripWidth(self):
    currentWidth = self.strips[0].width() * (100.0+self.application.preferences.general.stripWidthZoomPercent) / 100.0
    for strip in self.strips:
      strip.hide()
      strip.setMinimumWidth(currentWidth)
      strip.show()

  def decreaseStripWidth(self):
    currentWidth = self.strips[0].width() * 100.0 / (100.0+self.application.preferences.general.stripWidthZoomPercent)
    for strip in self.strips:
      strip.hide()
      strip.setMinimumWidth(currentWidth)
      strip.show()

    # cols = self.stripFrame.layout().columnCount()
    # for col in range(cols):
    #   self.stripFrame.layout().setColumnMinimumWidth(col, 50)

  def addStrip(self) -> 'GuiStripNd':
    """
    Creates a new strip by cloning strip with index (default the last) in the display.
    """
    stripIndex = -1   # ejb - just here for the minute
    newStrip = self.strips[stripIndex].clone()

    newStrip.copyOrderedSpectrumViews(self.strips[stripIndex-1])

    self.showAxes()

    # do setColumnStretches here or in Gui.py (422)
    self.setColumnStretches(True)

    mainWindow = self.mainWindow
    mainWindow.pythonConsole.writeConsoleCommand("strip.clone()", strip=newStrip)
    getLogger().info("spectrumDisplay = ui.getByGid(%r); spectrumDisplay.addStrip(%d)" \
                     % (self.pid, stripIndex))
    return newStrip

  def _addObjStrip(self, strip=None) -> 'GuiStripNd':
    """
    Creates a new strip by cloning strip with index (default the last) in the display.
    """
    stripIndex = self.strips.index(strip)
    newStrip = strip.clone()

    self.showAxes()

    # do setColumnStretches here or in Gui.py (422)
    self.setColumnStretches(True)

    mainWindow = self.mainWindow
    mainWindow.pythonConsole.writeConsoleCommand("strip.clone()", strip=newStrip)
    getLogger().info("spectrumDisplay = ui.getByGid(%r); spectrumDisplay.addStrip(%d)" \
                     % (self.pid, stripIndex))
    return newStrip

  def setColumnStretches(self, stretchValue=False):
    # crude routine to set the stretch of all columns upto the last widget to stretchValue
    widgets = self.stripFrame.children()
    if widgets:
      thisLayout = self.stripFrame.layout()
      thisLayoutWidth = self.stripFrame.width()
      firstStripWidth = thisLayout.itemAt(0).widget().width()

      # TODO:ED doesn't update when resizing
      if not self.lastAxisOnly or True:
        maxCol = 0
        for wid in widgets[1:]:
          index = thisLayout.indexOf(wid)
          row, column, cols, rows = thisLayout.getItemPosition(index)
          maxCol = max(maxCol, column)

        for col in range(0, maxCol+1):
          thisLayout.setColumnStretch(col, 1 if stretchValue else 0)
          thisLayout.itemAt(col).widget().setMinimumWidth(firstStripWidth)
      else:
        maxCol = 0
        for wid in widgets[1:]:
          index = thisLayout.indexOf(wid)
          row, column, cols, rows = thisLayout.getItemPosition(index)
          maxCol = max(maxCol, column)

        leftWidth = (thisLayoutWidth - AXIS_WIDTH) / (maxCol+1)
        endWidth = leftWidth + AXIS_WIDTH
        for col in range(0, maxCol):
          thisLayout.setColumnStretch(col, leftWidth if stretchValue else 0)
          thisLayout.itemAt(col).widget().setMinimumWidth(firstStripWidth)

        thisLayout.setColumnStretch(maxCol, endWidth if stretchValue else 0)
        thisLayout.itemAt(maxCol).widget().setMinimumWidth(firstStripWidth)

  def resetYZooms(self):
    """Zooms Y axis of current strip to show entire region"""
    for strip in self.strips:
      strip.resetYZoom()

  def resetXZooms(self):
    """Zooms X axis of current strip to show entire region"""
    for strip in self.strips:
      strip.resetXZoom()

  def _restoreZoom(self):
    """Restores last saved zoom of current strip."""
    try:
      if not self.current.strip:
        showWarning('Restore Zoom', 'No strip selected')
        return
      if self.current.strip not in self.strips:
        showWarning('Restore Zoom', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                    % (self.current.strip.pid, self.pid))
        return
      else:
        self.current.strip._restoreZoom()
    except:
      getLogger().warning('Error restoring zoom')

  def _storeZoom(self):
    """Saves zoomed region of current strip."""
    try:
      if not self.current.strip:
        showWarning('Store Zoom', 'No strip selected')
        return
      if self.current.strip not in self.strips:
        showWarning('Store Zoom', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                    % (self.current.strip.pid, self.pid))
        return
      else:
        self.current.strip._storeZoom()
    except:
      getLogger().warning('Error storing zoom')

  def _zoomIn(self):
    """zoom in to the current strip."""
    try:
      if not self.current.strip:
        showWarning('Zoom In', 'No strip selected')
        return
      if self.current.strip not in self.strips:
        showWarning('Zoom In', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                    % (self.current.strip.pid, self.pid))
        return
      else:
        self.current.strip._zoomIn()
    except:
      getLogger().warning('Error zooming in')

  def _zoomOut(self):
    """zoom out of current strip."""
    try:
      if not self.current.strip:
        showWarning('Zoom Out', 'No strip selected')
        return
      if self.current.strip not in self.strips:
        showWarning('Zoom Out', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                    % (self.current.strip.pid, self.pid))
        return
      else:
        self.current.strip._zoomOut()
    except:
      getLogger().warning('Error zooming out')

  def toggleCrossHair(self):
    """Toggles whether cross hair is displayed in all strips of spectrum display."""
    # toggle crosshairs for strips in this spectrumDisplay
    for strip in self.strips:
      strip._toggleCrossHair()
    
  def toggleGrid(self):
    """Toggles whether grid is displayed in all strips of spectrum display."""
    # toggle grid for strips in this spectrumDisplay
    for strip in self.strips:
      strip.toggleGrid()

  def _cyclePeakLabelling(self):
    """toggles peak labelling of current strip."""
    try:
      if not self.current.strip:
        showWarning('Cycle Peak Labelling', 'No strip selected')
        return
      if self.current.strip not in self.strips:
        showWarning('Cycle Peak Labelling', 'Selected strip "%s" is not part of SpectrumDisplay "%s"' \
                    % (self.current.strip.pid, self.pid))
        return
      else:
        self.current.strip.cyclePeakLabelling()
    except:
      getLogger().warning('Error cycling peak labelling')

  def _deletedPeak(self, peak):
    apiPeak = peak._wrappedData
    # NBNB TBD FIXME rewrite this to not use API peaks
    # ALSO move this machinery from subclasses to this class.
    for peakListView in self.activePeakItemDict:
      peakItemDict = self.activePeakItemDict[peakListView]
      peakItem = peakItemDict.get(apiPeak)
      if peakItem:
        peakListView.spectrumView.strip.plotWidget.scene().removeItem(peakItem)
        del peakItemDict[apiPeak]
        inactivePeakItems = self.inactivePeakItemDict.get(peakListView)
        if inactivePeakItems:
          inactivePeakItems.add(peakItem)

  # def _resetRemoveStripAction(self):
  #   """
  #   # CCPNINTERNAL - called from GuiMainWindow and from GuiStrip to manage removeStrip button enabling,
  #   and from Framework to set up initial state
  #   """
  #   #TODO:WAYNE: FrameWork should not have anything to do with this
  #   strip = self.current.strip
  #   # # Rasmus HACK!
  #   # # This code broke because it got triggered (via a current notifier) when strips
  #   # # were deleted but self was not. A bigger fix is needed (TODO), but for now try this
  #   myStrips = [self.project._data2Obj.get(x) for x in self._wrappedData.strips]
  #   if len(myStrips) <= 1 or not strip in myStrips:
  #     # current.strip not in display, or only 1 strip in display, so disable removeStrip button
  #     enabled = False
  #   else:
  #     enabled = True
  #   self.removeStripAction.setEnabled(enabled)
  #
  #   # strips = set(self._appBase.current.strips)
  #   # # Rasmus HACK!
  #   # # This code broke because it got triggered (via a current notifier) when strips
  #   # # were deleted but self was not. A bigger fix is needed, but for now try this
  #   # myStrips = [self._project._data2Obj.get(x) for x in self._wrappedData.strips]
  #   # myStrips = [x for x in myStrips if x is not None]
  #   # if len(myStrips) <= 1 or not strips.intersection(myStrips):
  #   # # if not strips.intersection(self.strips) or len(self.strips) == 1:
  #   #   # no strip in display is in current.strips, or only 1 strip in display, so disable removeStrip button
  #   #   enabled = False
  #   # else:
  #   #   enabled = True
  #   # self.removeStripAction.setEnabled(enabled)

  def displaySpectrum(self, spectrum, axisOrder:(str,)=()):
    """Display additional spectrum, with spectrum axes ordered according ton axisOrder
    """
    spectrum = self.getByPid(spectrum) if isinstance(spectrum, str) else spectrum

    self._startCommandEchoBlock('displaySpectrum', spectrum, values=locals(),
                                defaults={'axisOrder':()})
    try:
      newSpectrum = self.strips[0].displaySpectrum(spectrum, axisOrder=axisOrder)
      if newSpectrum:
        # self._orderedSpectra.append(spectrum)
        for strip in self.strips:

          # displaySpectrum above creates a new spectrum for each strip in the display
          # but only returns the first one
          # this loops through the strips and adds each to the strip ordered list
          existingViews = set(strip.orderedSpectrumViews())
          newViews = set(strip.spectrumViews)
          dSet = set(newViews).difference(existingViews)

          # append those not found
          for spInDSet in dSet:
            strip.appendSpectrumView(spInDSet)

    except Exception as es:
      getLogger().warning('Error appending newSpectrum: %s' % spectrum)
    finally:
      self._endCommandEchoBlock()

  def _removeSpectrum(self, spectrum):
    try:
      # self._orderedSpectra.remove(spectrum)
      self.removeSpectrumView(spectrum)
    except:
      getLogger().warning('Error, %s does not exist' % spectrum)

def _deletedPeak(peak:Peak):
  """Function for notifiers.
  #CCPNINTERNAL """

  for spectrumView in peak.peakList.spectrum.spectrumViews:
    spectrumView.strip.spectrumDisplay._deletedPeak(peak)

def _spectrumHasChanged(spectrum:Spectrum):
  project = spectrum.project
  apiDataSource = spectrum._wrappedData
  for spectrumDisplay in project.spectrumDisplays:
    action = spectrumDisplay.spectrumActionDict.get(apiDataSource)
    if action: # spectrum might not be in all displays
      # update toolbar button name
      action.setText(spectrum.name)

def _deletedSpectrumView(project:Project, apiSpectrumView):
  """tear down SpectrumDisplay when new SpectrumView is deleted - for notifiers"""
  spectrumDisplay = project._data2Obj[apiSpectrumView.spectrumDisplay]
  apiDataSource = apiSpectrumView.dataSource

  # remove toolbar action (button)
  # NBNB TBD FIXME get rid of API object from code
  action = spectrumDisplay.spectrumActionDict.get(apiDataSource)  # should always be not None
  if action:
    spectrumDisplay.spectrumToolBar.removeAction(action)
    del spectrumDisplay.spectrumActionDict[apiDataSource]

GuiSpectrumDisplay.processSpectrum = GuiSpectrumDisplay.displaySpectrum   # ejb - from SpectrumDisplay
