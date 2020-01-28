"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2020"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2020-01-28 03:15:19 +0000 (Tue, January 28, 2020) $"
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from functools import partial
from PyQt5 import QtWidgets, QtCore
from itertools import permutations
from collections import Iterable
from ccpn.core.Spectrum import MAXALIASINGRANGE, Spectrum
from collections import OrderedDict
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.ColourDialog import ColourDialog
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox, ScientificDoubleSpinBox
from ccpn.ui.gui.widgets.FilteringPulldownList import FilteringPulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.popups.ExperimentTypePopup import _getExperimentTypes
from ccpn.util.Colour import spectrumColours, addNewColour, fillColourPulldown, \
    colourNameNoSpace, _setColourPulldown, getSpectrumColour
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.ui.gui.widgets.Tabs import Tabs
from ccpn.util.Logging import getLogger
from ccpn.util.Constants import DEFAULT_ISOTOPE_DICT
from ccpn.util.OrderedSet import OrderedSet
from ccpn.ui.gui.guiSettings import getColours, DIVIDER
from ccpn.ui.gui.widgets.HLine import HLine
from ccpn.ui.gui.widgets.CompoundWidgets import PulldownListCompoundWidget
from ccpn.ui.gui.widgets.Spacer import Spacer
from ccpn.ui.gui.widgets.DialogButtonBox import DialogButtonBox
from ccpn.ui.gui.popups.Dialog import CcpnDialogMainWidget, handleDialogApply, \
    _verifyPopupApply, _verifyPopupTabApply, _verifyPopupChangesApply
from ccpn.core.lib.ContextManagers import undoStackBlocking
from ccpn.core.lib.SpectrumLib import getContourLevelsFromNoise
from ccpn.core.lib.ContextManagers import queueStateChange
from ccpn.ui.gui.popups.ValidateSpectraPopup import ValidateSpectraForSpectrumPopup

from PyQt5 import QtWidgets, QtGui
from ast import literal_eval
from typing import Tuple, Any
from collections import OrderedDict, Iterable
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
from ccpn.ui.gui.widgets.Tabs import Tabs
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.PulldownListsForObjects import SpectrumGroupPulldown
from ccpn.ui.gui.widgets.Spacer import Spacer
from ccpn.ui.gui.widgets.TextEditor import TextEditor, PlainTextEditor
from ccpn.ui.gui.popups._GroupEditorPopupABC import _GroupEditorPopupABC
from ccpn.ui.gui.popups.SpectrumPropertiesPopup import ColourTab, ContoursTab
from ccpn.util.AttrDict import AttrDict


DEFAULTSPACING = (3, 3)
TABMARGINS = (1, 10, 1, 5)  # l, t, r, b
INVALIDROWCOLOUR = QtGui.QColor('lightpink')


class SpectrumGroupEditor(_GroupEditorPopupABC):
    """
    A popup to create and manage SpectrumGroups

    Used in 'New' or 'Edit' mode:
    - For creating new SpectrumGroup (editMode==False); optionally uses passed in spectra list
      i.e. NewSpectrumGroup of SideBar and Context menu of SideBar

    - For editing existing SpectrumGroup (editMode==True); requires spectrumGroup argument
      i.e. Edit of SpectrumGroup of SideBar
    or
      For selecting and editing SpectrumGroup (editMode==True)
      i.e. Menu Spectrum->Edit SpectrumGroup...

    """
    KLASS = SpectrumGroup
    KLASS_ITEM_ATTRIBUTE = 'spectra'  # Attribute in KLASS containing items
    KLASS_PULLDOWN = SpectrumGroupPulldown

    PROJECT_NEW_METHOD = 'newSpectrumGroup'  # Method of Project to create new KLASS instance
    PROJECT_ITEM_ATTRIBUTE = 'spectra'  # Attribute of Project containing items
    PLURAL_GROUPED_NAME = 'Spectrum Groups'
    SINGULAR_GROUP_NAME = 'Spectrum Group'

    GROUP_PID_KEY = 'SG'
    ITEM_PID_KEY = 'SP'

    def _applyChanges(self):
        """
        The apply button has been clicked
        Define an undo block for setting the properties of the object
        If there is an error setting any values then generate an error message
          If anything has been added to the undo queue then remove it with application.undo()
          repopulate the popup widgets

        This is controlled by a series of dicts that contain change functions - operations that are scheduled
        by changing items in the popup. These functions are executed when the Apply or OK buttons are clicked

        Return True unless any errors occurred
        """

        _colourTabs = [self._colourTabs.widget(tt) for tt in range(self._colourTabs.count())]
        if not _colourTabs:
            raise RuntimeError("Code error: tabs not implemented")

        _allTabs = self.getActiveTabList()

        # get the list of widgets that have been changed - exit if all empty
        allChanges = any(t._changes for t in _allTabs if t is not None) or (True if self._currentEditorState() else False)
        if not allChanges:
            return True

        # handle clicking of the Apply/OK button
        with handleDialogApply(self) as error:

            # get the list of spectra that have changed - for refreshing the displays
            spectrumList = []
            for t in _colourTabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        spectrumList.append(t.spectrum)

            # add an undo item to redraw these spectra
            with undoStackBlocking() as addUndoItem:
                addUndoItem(undo=partial(self._updateGl, spectrumList))

            # call the _groupEditor _applyChanges method which sets the group items
            super()._applyChanges()

            # add a redo item to redraw these spectra
            with undoStackBlocking() as addUndoItem:
                addUndoItem(redo=partial(self._updateGl, spectrumList))

            # rebuild the contours as required
            for spec in spectrumList:
                for specViews in spec.spectrumViews:
                    specViews.buildContours = True
            self._updateGl(spectrumList)

        # everything has happened - disable the apply button
        self._applyButton.setEnabled(False)

        # check for any errors
        if error.errorValue:
            # repopulate popup on an error
            self._populate()
            return False

        # remove all changes
        for tab in _colourTabs:
            tab._changes = {}

        # self._currentNumApplies += 1
        # self._revertButton.setEnabled(True)
        return True

    def _groupInit(self):
        # apply the changes to the listed spectra spectraTab._changes
        if self.spectraTab._changes:
            self._applyAllChanges(self.spectraTab._changes)

        for tt in range(self._colourTabs.count()):
            _changes = self._colourTabs.widget(tt)._changes
            if _changes:
                self._applyAllChanges(_changes)

        self._spectrumGroupSeriesEdited = OrderedDict()
        self._spectrumGroupSeriesValues = list(self.obj.series)
        self._spectrumGroupSeriesUnitsEdited = None

        # set the series values - this may crash
        if self.seriesTab._changes:
            self._applyAllChanges(self.seriesTab._changes)

        specList = self._currentEditorState()[self.obj.id]
        for dim, specPid in enumerate(specList):
            spec = self.project.getByPid(specPid)

            # read the value from the edits dict - bit of a hack from _changeSpectrumSeriesValues
            if spec and dim in self._spectrumGroupSeriesEdited:
                self._spectrumGroupSeriesValues[dim] = self._spectrumGroupSeriesEdited[dim]
        if self._spectrumGroupSeriesEdited:
            try:
                self.obj.series = tuple(self._spectrumGroupSeriesValues)
            except Exception as es:
                showWarning('Error settings seriesValues', str(es))

        if self._spectrumGroupSeriesUnitsEdited is not None:
            self.obj.seriesUnits = self._spectrumGroupSeriesUnitsEdited

    GROUPEDITOR_INIT_METHOD = _groupInit

    # make this a tabbed dialog, with the default widget going into tab 0
    USE_TAB = 0
    NUMBER_TABS = 3  # create the first tab

    def __init__(self, parent=None, mainWindow=None, editMode=True, obj=None, defaultItems=None, **kwds):
        """
        Initialise the widget, note defaultItems is only used for create
        """
        super().__init__(parent=parent, mainWindow=mainWindow, editMode=editMode, obj=obj, defaultItems=defaultItems, **kwds)

        self.TAB_NAMES = (('Spectra', self._initSpectraTab),
                          ('General', self._initGeneralTab),
                          ('Series', self._initSeriesTab))

        # TODO:ED - order this a little better

        if obj and editMode:
            defaultItems = obj.spectra
        # replace the tab widget with a new seriesWidget
        seriesTabContents = SeriesFrame(parent=self, mainWindow=self.mainWindow, spectrumGroup=obj, editMode=editMode,
                                        showCopyOptions=True if len(defaultItems) > 1 else False,
                                        defaultItems=defaultItems)
        self._tabWidget.widget(2).setWidget(seriesTabContents)

        # get pointers to the tabs
        self.spectraTab = self._tabWidget.widget(0)._scrollContents
        self.generalTab = self._tabWidget.widget(1)._scrollContents
        self.seriesTab = self._tabWidget.widget(2)._scrollContents

        self.currentSpectra = self._getSpectraFromList()

        for tNum, (tabName, tabFunc) in enumerate(self.TAB_NAMES):
            self._tabWidget.setTabText(tNum, tabName)
            if tabFunc:
                tabFunc()

        # TODO:ED set to the size of the first tab - or a fixed size so the first tab looks nice

        self._populate()
        self.setMinimumSize(600, 550)  # change to a calculation rather than a guess

        self.connectSignals()
        self.setSizeGripEnabled(False)

    def connectSignals(self):
        # connect to changes in the spectrumGroup
        self.leftListWidget.model().dataChanged.connect(self._spectraChanged)
        self.leftListWidget.model().rowsRemoved.connect(self._spectraChanged)
        self.leftListWidget.model().rowsInserted.connect(self._spectraChanged)
        self.leftListWidget.model().rowsMoved.connect(self._spectraChanged)

    def getActiveTabList(self):
        """Return the list of active tabs
        """
        # test the colour tabs for the moment
        tabs = tuple(self._colourTabs.widget(ii) for ii in range(self._colourTabs.count())) + \
               (self._tabWidget.widget(0)._scrollContents, self._tabWidget.widget(2)._scrollContents)
        return tabs

    def _initSpectraTab(self):
        thisTab = self.spectraTab
        thisTab._changes = OrderedDict()

    def _initGeneralTab(self):
        thisTab = self.generalTab
        self._colourTabs = Tabs(thisTab, grid=(0, 0))

        # TODO:ED need to get the list of spectra from the first tab

        # self.orderedSpectrumViews = orderedSpectrumViews
        # self.orderedSpectra = OrderedSet([spec.spectrum for spec in self.orderedSpectrumViews])

        # remember the state when switching tabs
        self.copyCheckBoxState = []

        for specNum, thisSpec in enumerate(self.currentSpectra or []):
            contoursTab = ContoursTab(parent=self, mainWindow=self.mainWindow, spectrum=thisSpec,
                                      showCopyOptions=True if len(self.currentSpectra) > 1 else False,
                                      copyToSpectra=self.currentSpectra)
            self._colourTabs.addTab(contoursTab, thisSpec.name)
            contoursTab.setContentsMargins(*TABMARGINS)

        self._colourTabs.setTabClickCallback(self._tabClicked)

        # self._colourTabs.setTabsClosable(True)
        self._colourTabs.tabCloseRequested.connect(self._closeColourTab)
        self._oldTabs = OrderedDict()

    def _initSeriesTab(self):
        thisTab = self.seriesTab
        thisTab._changes = OrderedDict()

        # TODO:ED setup a pandas table for the spectra as the first column
        #       or another simple way to edit the spectrum seriesValue, textEditor?
        thisTab._populate()

    def _populate(self):
        """Populate the widgets in the tabs
        """
        with self.blockWidgetSignals():
            for aTab in tuple(self._colourTabs.widget(ii) for ii in range(self._colourTabs.count())):
                aTab._populateColour()

    def _tabClicked(self, index):
        """Callback for clicking a tab - needed for refilling the checkboxes and populating the pulldown
        """
        aTabs = tuple(self._colourTabs.widget(ii) for ii in range(self._colourTabs.count()))
        if hasattr(aTabs[index], '_populateCheckBoxes'):
            aTabs[index]._populateCheckBoxes()

    def _getSpectraFromList(self):
        """Get the list of spectra from the list
        """
        return [spec for spec in [self.project.getByPid(spectrum) if isinstance(spectrum, str) else spectrum for spectrum in self._groupedObjects] if spec]

    def _cleanColourTab(self, spectrum):
        """Remove the unwanted queue items from spectra reomved from the spectrumQueue
        """
        with self.blockWidgetSignals():
            for aTab in tuple(self._colourTabs.widget(ii) for ii in range(self._colourTabs.count())):
                if aTab.spectrum == spectrum:
                    aTab._cleanWidgetQueue()

    def _removeTab(self, spectrum):
        """Remove the unwanted queue items from spectra reomved from the spectrumQueue
        """
        for aTab in tuple(self._colourTabs.widget(ii) for ii in range(self._colourTabs.count())):
            if aTab.spectrum == spectrum:
                pass

    def _closeColourTab(self, index):
        tab = self._colourTabs.widget(index)
        # tab.deleteLater()
        self._colourTabs.removeTab(index)
        pass

    def _spectraChanged(self, *args):
        """Respond to a change in the list of spectra to add the spectrumGroup
        """
        self._newSpectra = self._getSpectraFromList()

        # TODO:ED remove tabs for spectra removed from list
        #           add new tabs in correct place
        #           remember to remove any _queue settings from updated colour tabs
        #           populate new tabs
        #           POPULATE SERIES TAB

        deleteSet = (set(self.currentSpectra) - set(self._newSpectra))
        newSet = (set(self.currentSpectra) - set(self._newSpectra))

        for spec in deleteSet:
            # remove tab widget
            self._cleanColourTab(spec)
            if spec in self.seriesTab._currentSeriesValues:
                del self.seriesTab._currentSeriesValues[spec]

        # remove all in reverse order, keep old ones
        for ii in range(self._colourTabs.count() - 1, -1, -1):
            tab = self._colourTabs.widget(ii)
            self._oldTabs[tab.spectrum] = tab
            self._colourTabs.removeTab(ii)

        for spec in self._newSpectra:
            # add new tab widget here
            if spec in self._oldTabs:
                self._colourTabs.addTab(self._oldTabs[spec], spec.name)
                self._oldTabs[spec].setCopyOptionsVisible(True if len(self._newSpectra) > 1 else False)
            else:
                contoursTab = ContoursTab(parent=self, mainWindow=self.mainWindow, spectrum=spec,
                                          showCopyOptions=True if len(self._newSpectra) > 1 else False,
                                          copyToSpectra=self._newSpectra)
                self._colourTabs.addTab(contoursTab, spec.name)
                contoursTab.setContentsMargins(*TABMARGINS)
                contoursTab._populateColour()

        self.seriesTab._fillSeriesFrame(self._newSpectra)

        # update the current list
        self.currentSpectra = self._newSpectra

    def copySpectra(self, fromSpectrum, toSpectra):
        """Copy the contents of tabs to other spectra
        """
        colourTabs = [self._colourTabs.widget(ii) for ii in range(self._colourTabs.count())]
        for aTab in colourTabs:
            if aTab.spectrum == fromSpectrum:
                fromSpectrumTab = aTab
                for aTab in [tab for tab in colourTabs if tab != fromSpectrumTab and tab.spectrum in toSpectra]:
                    aTab._copySpectrumAttributes(fromSpectrumTab)

    # def getChangesDict(self):
    #     """Define the required widgets with storing changes
    #     returns Popup containing buttons
    #             dict containing current changes
    #     """
    #     return self, self.seriesTab._changes


class SeriesFrame(Widget):
    EDITMODE = False

    def __init__(self, parent=None, mainWindow=None, spectrumGroup=None, editMode=False,
                 showCopyOptions=False, defaultItems=None):

        super().__init__(parent, setLayout=True, spacing=DEFAULTSPACING)

        self._parent = parent
        self.mainWindow = mainWindow
        self.application = mainWindow.application
        self.preferences = self.application.preferences
        self.EDITMODE = editMode

        # check that the spectrum and the copyToSpectra list are correctly defined
        getByPid = self.application.project.getByPid
        self.spectrumGroup = getByPid(spectrumGroup) if isinstance(spectrumGroup, str) else spectrumGroup
        if not isinstance(self.spectrumGroup, (SpectrumGroup, type(None))):
            raise TypeError('spectrumGroup must be of type spectrumGroup or None')

        if not isinstance(defaultItems, (Iterable, type(None))):
            raise TypeError('copyToSpectra must be of type Iterable/None')
        if defaultItems:
            self._copyToSpectra = [getByPid(spectrum) if isinstance(spectrum, str) else spectrum for spectrum in defaultItems]
            for spec in self._copyToSpectra:
                if not isinstance(spec, (Spectrum, type(None))):
                    raise TypeError('copyToSpectra is not defined correctly.')
        else:
            self._copyToSpectra = None

        self._changes = OrderedDict()
        self._editors = OrderedDict()
        self._currentSeriesValues = OrderedDict()

        if self.EDITMODE:
            self.defaultObject = spectrumGroup
        else:
            # create a dummy object that SHOULD contain the required attributes
            self.defaultObject = _SpectrumGroupContainer()
            self.defaultObject.spectra = defaultItems

        row = 0
        col = 0
        seriesLabel = Label(self, text="Spectrum SeriesValues - use python literals", grid=(row, col), gridSpan=(1, 2), hAlign='l')
        seriesLabel.setFixedHeight(30)
        seriesLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        row += 1
        self._seriesFrameRow = row
        self._seriesFrameCol = col

        # self._seriesFrame = Frame(self, setLayout=True, showBorder=False, grid=(self._seriesFrameRow, self._seriesFrameCol), gridSpan=(1, 3))
        self._seriesFrame = None
        self._fillSeriesFrame(defaultItems=defaultItems)

        row += 1
        unitsLabel = Label(self, text='Series Units', grid=(row, col), hAlign='l')
        self.unitsEditor = LineEdit(self, grid=(row, col + 1))
        unitsLabel.setFixedHeight(30)
        self.unitsEditor.textChanged.connect(partial(self._queueChangeSpectrumSeriesUnits, self.unitsEditor, self.defaultObject))

        row += 1
        Spacer(self, 1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding,
               grid=(row, col + 2))
        self.getLayout().setRowStretch(row, 10)

        # get colours from the lineEdit and copy to the plainTextEdit
        # yourWidget.palette().highlight().color().name()?

    def _fillSeriesFrame(self, defaultItems):
        """Reset the contents of the series frame for changed spectrum list
        """
        # remove previous editor values
        for spec, editor in self._editors.items():
            editor.textChanged.disconnect()
            self._currentSeriesValues[spec] = editor.get()

        self._changes = OrderedDict()
        self._editors = OrderedDict()

        # empty the frame
        if self._seriesFrame:
            self._seriesFrame.hide()
            self._seriesFrame.deleteLater()

        self._seriesFrame = Frame(self, setLayout=True, showBorder=False, grid=(self._seriesFrameRow, self._seriesFrameCol), gridSpan=(1, 3))

        # add new editors with the new values
        for sRow, spec in enumerate(defaultItems):
            seriesLabel = Label(self._seriesFrame, text=spec.pid, grid=(sRow, 0), hAlign='left', vAlign='top')
            seriesLabel.setFixedHeight(30)
            seriesLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

            seriesEditor = PlainTextEditor(self._seriesFrame, grid=(sRow, 1))
            # seriesEditor._setFocusColour()
            seriesEditor.textChanged.connect(partial(self._queueChangeSpectrumSeriesValues,
                                                     seriesEditor, self.defaultObject,
                                                     spec, sRow))

            seriesEditor.setMinimumSize(50, 25)
            seriesEditor.setMaximumHeight(30)
            seriesEditor._minimumWidth = 50
            seriesEditor._minimumHeight = 25

            if spec in self._currentSeriesValues and self._currentSeriesValues[spec] is not None:
                seriesEditor.set(self._currentSeriesValues[spec])

            self._editors[spec] = seriesEditor

        self._seriesFrame.setMaximumHeight(self._seriesFrame.sizeHint().height())

    def _populate(self):
        """Populate the texteditors - seriesValues and seriesUnits for the spectrumGroup
        """
        series = self.defaultObject.series
        if series:
            for spec, textEditor in self._editors.items():
                ii = self.defaultObject.spectra.index(spec)
                textEditor.set(repr(series[ii]))
        self.unitsEditor.set(self.defaultObject.seriesUnits)

    def _getValuesFromTextEdit(self):
        # read the values from the textEditors and put in dict for later
        for spec, editor in self._editors.items():
            self._currentSeriesValues[spec] = editor.get()

    def _cleanSpacers(self, widget):
        # remove unneeded spacers
        layout = widget.getLayout()
        spacers = [layout.itemAt(itmNum) for itmNum in range(layout.count()) if isinstance(layout.itemAt(itmNum), Spacer)]
        for sp in spacers:
            layout.removeItem(sp)

    @queueStateChange(_verifyPopupChangesApply)
    def _queueChangeSpectrumSeriesValues(self, editor, spectrumGroup, spectrum, dim):
        # if value >= 0 and list(spectrumColours.keys())[value] != spectrum.sliceColour:
        #     return partial(self._changedSliceComboIndex, spectrum, value)
        value = editor.get()
        palette = editor.viewport().palette()
        colour = editor._background
        try:
            seriesValue = literal_eval(value)

        except Exception as es:
            # catch exception raised by bad literals
            if value:
                colour = INVALIDROWCOLOUR

        else:
            # if isinstance(seriesValue, dict):
            #     # if a dict is used, it should be an ordered dict to help with checking
            #     seriesValue = OrderedDict(seriesValue)

            specValue = spectrum._getSeriesItemsById(spectrumGroup.pid)
            if seriesValue != specValue:
                return partial(self._changeSpectrumSeriesValues, spectrumGroup, spectrum, dim, seriesValue)

        finally:
            palette.setColor(editor.viewport().backgroundRole(), colour)
            editor.viewport().setPalette(palette)

            rowHeight = QtGui.QFontMetrics(editor.document().defaultFont()).height()
            lineCount = editor.document().lineCount()

            minHeight = (rowHeight + 1) * (lineCount + 1)
            height = max(editor._minimumHeight, minHeight)
            editor.setMaximumHeight(height)
            editor.updateGeometry()

            sum = 0.0
            for ee in self._editors.values():
                sum += ee.maximumHeight()
            self._seriesFrame.setMaximumHeight(self._seriesFrame.sizeHint().height())

    def _changeSpectrumSeriesValues(self, spectrumGroup, spectrum, dim, value):
        # set the spectrum series value from here
        # spectrum.seriesValue = value

        # bit of a hack here - called by _groupInit which builds the spectrumGroup series
        self._parent._spectrumGroupSeriesEdited[dim] = value

    @queueStateChange(_verifyPopupChangesApply)
    def _queueChangeSpectrumSeriesUnits(self, editor, spectrumGroup):
        """callback from editing the seriesUnits
        """
        value = editor.get()
        specValue = spectrumGroup.seriesUnits
        if value != specValue:
            return partial(self._changeSpectrumSeriesUnits, spectrumGroup, value)

    def _changeSpectrumSeriesUnits(self, spectrumGroup, value):
        """set the spectrumGroup seriesUnits
        """
        self._parent._spectrumGroupSeriesUnitsEdited = value

    def getChangesDict(self):
        """Define the required widgets with storing changes
        returns Popup containing then apply/close buttons
                dict containing current changes
                stateValue, an overriding boolean that needs to be true for all else to be true
        """
        return self._parent, self._changes, True if self._parent._currentEditorState() else False


class _SpectrumGroupContainer(AttrDict):
    """
    Class to simulate a spectrumGroup in popup.
    """

    def __init__(self):
        super(_SpectrumGroupContainer, self).__init__()
        self.pid = id(self)
        self.spectra = []
        self._modifiedSpectra = set()
        self._setDefaultSeriesValues()
        self._seriesUnits = None

    @property
    def series(self) -> Tuple[Any, ...]:
        """Returns a tuple of series items for the attached spectra

        series = (val1, val2, ..., valN)

        where val1-valN correspond to the series items in the attached spectra associated with this group
        For a spectrum with no values, returns None in place of Item

        Duplicated from spectrumGroup.series
        """
        series = ()
        for spectrum in self.spectra:
            series += (spectrum._getSeriesItemsById(self.pid),)

        return series

    @property
    def seriesUnits(self):
        """Return the seriesUnits for the simulated spectrumGroup
        """
        return self._seriesUnits

    def _setDefaultSeriesValues(self):
        for spec in self.spectra:
            spec._setSeriesItemsById(self.pid, None)

    def _removeDefaultSeriesValues(self):
        for spec in self.spectra:
            spec._removeSeriesItemsById(self.pid)

    def __del__(self):
        """destructor required to cleanup ids in altered spectra
        """
        self._removeDefaultSeriesValues()
