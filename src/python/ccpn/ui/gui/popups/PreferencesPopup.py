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
__dateModified__ = "$dateModified: 2017-07-07 16:32:49 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtWidgets, QtCore

import os
from functools import partial
from ccpnmodel.ccpncore.api.memops import Implementation
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.guiSettings import COLOUR_SCHEMES, getColours, DIVIDER
from ccpn.framework.Translation import languages
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets import MessageDialog
from ccpn.ui.gui.widgets.Tabs import Tabs
from ccpn.ui.gui.widgets.Spacer import Spacer
from ccpn.ui.gui.widgets.HLine import HLine
from ccpn.util.Logging import getLogger


# FIXME separate pure GUI to project/preferences properites
# The code sets Gui Parameters assuming that  Preference is not None and has a bunch of attributes.


PulldownListsMinimumWidth = 200
LineEditsMinimumWidth = 195
NotImplementedTipText = 'This option has not been implemented yet'


class PreferencesPopup(CcpnDialog):
    def __init__(self, parent=None, mainWindow=None, preferences=None, title='Preferences', **kw):
        CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, size=(300, 100), **kw)

        self.mainWindow = mainWindow
        if self.mainWindow:
            self.application = mainWindow.application
            self.project = mainWindow.application.project
        else:
            self.application = None
            self.project = None

        if not self.project:  # ejb - should always be loaded
            MessageDialog.showWarning(title, 'No project loaded')
            self.close()
            return

        self.preferences = preferences
        self.oldPreferences = preferences

        self.mainLayout = self.getLayout()
        self._setTabs()

        # self.buttonBox = Button(self, text='Close', callback=self._accept, grid=(1, 2))
        self.buttonBox = ButtonList(self, texts=['Close', 'Apply'],
                                    callbacks=[self._accept, self._applyChanges],
                                    tipTexts=['Close and update preferences', 'Apply changes to all strips'],
                                    direction='h', hAlign='r', grid=(1, 2))

    def _applyChanges(self):
        for display in self.project.spectrumDisplays:
            for strip in display.strips:
                strip.peakLabelling = self.preferences.general.annotationType
                strip.peakSymbolType = self.preferences.general.peakSymbolType
                strip.peakSymbolSize = self.preferences.general.peakSymbolSize
                strip.peakSymbolThickness = self.preferences.general.peakSymbolThickness
                strip.gridVisible = self.preferences.general.showGrid
                strip.crosshairVisible = self.preferences.general.showCrosshair
        self._accept()

    def _accept(self):
        self.accept()

        # prompt the GLwidgets to update
        from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier

        GLSignals = GLNotifier(parent=self)
        GLSignals.emitEvent(triggers=[GLNotifier.GLALLPEAKS])

    def _setTabs(self):

        ''' Creates the tabs as Frame Widget. All the children widgets will go in the Frame.
         Each frame will be the widgets parent.
         Tabs are displayed by the order how appear here. '''

        self.tabWidget = Tabs(self, grid=(0, 0), gridSpan=(1, 3))

        ## 1 Tab
        self.generalTabFrame = Frame(self, setLayout=True)
        # self.generalTabFrame.getLayout().setAlignment(QtCore.Qt.AlignTop)
        self.generalTabFrame.setContentsMargins(1, 10, 1, 10)
        self._setGeneralTabWidgets(parent=self.generalTabFrame)
        self.tabWidget.addTab(self.generalTabFrame, 'General')
        # self.generalTabFrame.layout().setSpacing(2)

        ## 2 Tab
        self.spectrumTabFrame = Frame(self, setLayout=True)
        self.spectrumTabFrame.getLayout().setAlignment(QtCore.Qt.AlignTop)
        self.spectrumTabFrame.setContentsMargins(1, 10, 1, 10)  # l,t,r,b
        self._setspectrumTabWidgets(parent=self.spectrumTabFrame)
        self.tabWidget.addTab(self.spectrumTabFrame, 'Spectrum')
        # self.spectrumTabFrame.layout().setSpacing(2)

        # 3 Tab Disabled. # Keep the code for future additions
        self.externalProgramsTabFrame = Frame(self, setLayout=True)
        self.externalProgramsTabFrame.getLayout().setAlignment(QtCore.Qt.AlignTop)
        self.externalProgramsTabFrame.setContentsMargins(1, 10, 1, 10)  # l,t,r,b
        self._setExternalProgramsTabWidgets(parent=self.externalProgramsTabFrame)
        self.tabWidget.addTab(self.externalProgramsTabFrame, 'External Programs')
        # self.externalProgramsTabFrame.layout().setSpacing(2)

    def _setGeneralTabWidgets(self, parent):
        ''' Insert a widget in here to appear in the General Tab  '''

        row = 0

        self.languageLabel = Label(parent, text="Language", grid=(row, 0))
        self.languageBox = PulldownList(parent, grid=(row, 1), hAlign='l')
        self.languageBox.addItems(languages)
        self.languageBox.setMinimumWidth(PulldownListsMinimumWidth)
        self.languageBox.setCurrentIndex(self.languageBox.findText(self.preferences.general.language))
        self.languageBox.currentIndexChanged.connect(self._changeLanguage)

        # disabled for 3.0.B3
        # row += 1
        # self.colourSchemeLabel = Label(parent, text="Colour Scheme ", grid=(row, 0))
        # self.colourSchemeBox = PulldownList(parent, grid=(row, 1), hAlign='l')
        # self.colourSchemeBox.setMinimumWidth(PulldownListsMinimumWidth)
        # self.colourSchemeBox.addItems(COLOUR_SCHEMES)
        # self.colourSchemeBox.setCurrentIndex(self.colourSchemeBox.findText(
        #   self.preferences.general.colourScheme))
        # self.colourSchemeBox.currentIndexChanged.connect(self._changeColourScheme)

        row += 1
        self.useNativeLabel = Label(parent, text="Use Native File Dialogs: ", grid=(row, 0))
        self.useNativeBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.useNative)
        self.useNativeBox.toggled.connect(partial(self._toggleGeneralOptions, 'useNative'))

        row += 1
        self.useNativeLabel = Label(parent, text="Use Native Web Browser: ", grid=(row, 0))
        self.useNativeBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.useNativeWebbrowser)
        self.useNativeBox.toggled.connect(partial(self._toggleGeneralOptions, 'useNativeWebbrowser'))

        row += 1
        self.autoSaveLayoutOnQuitLabel = Label(parent, text="Auto Save Layout On Quit: ", grid=(row, 0))
        self.autoSaveLayoutOnQuitBox = CheckBox(parent, grid=(row, 1),
                                                checked=self.preferences.general.autoSaveLayoutOnQuit)
        self.autoSaveLayoutOnQuitBox.toggled.connect(partial(self._toggleGeneralOptions, 'autoSaveLayoutOnQuit'))

        row += 1
        self.restoreLayoutOnOpeningLabel = Label(parent, text="Restore Layout On Opening: ", grid=(row, 0))
        self.restoreLayoutOnOpeningBox = CheckBox(parent, grid=(row, 1),
                                                  checked=self.preferences.general.restoreLayoutOnOpening)
        self.restoreLayoutOnOpeningBox.toggled.connect(partial(self._toggleGeneralOptions, 'restoreLayoutOnOpening'))

        row += 1
        self.autoBackupEnabledLabel = Label(parent, text="Auto Backup On: ", grid=(row, 0))
        self.autoBackupEnabledBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.autoBackupEnabled)
        self.autoBackupEnabledBox.toggled.connect(partial(self._toggleGeneralOptions, 'autoBackupEnabled'))

        row += 1
        self.autoBackupFrequencyLabel = Label(parent, text="Auto Backup Freq (mins)", grid=(row, 0))
        self.autoBackupFrequencyData = LineEdit(parent, grid=(row, 1), hAlign='l')
        self.autoBackupFrequencyData.setMinimumWidth(LineEditsMinimumWidth)
        self.autoBackupFrequencyData.setText('%.0f' % self.preferences.general.autoBackupFrequency)
        self.autoBackupFrequencyData.editingFinished.connect(self._setAutoBackupFrequency)

        row += 1
        HLine(parent, grid=(row, 0), gridSpan=(1, 3), colour=getColours()[DIVIDER], height=15)

        # row += 1
        # self.dataPathLabel = Label(parent, "Data Path", grid=(row, 0),)
        # self.dataPathText = LineEdit(parent, grid=(row, 1), hAlign='l')
        # self.dataPathText.setMinimumWidth(LineEditsMinimumWidth)
        # self.dataPathText.editingFinished.connect(self._setDataPath)
        # self.dataPathText.setText(self.preferences.general.dataPath)
        # self.dataPathButton = Button(parent, grid=(row, 2), callback=self._getDataPath, icon='icons/directory', hPolicy='fixed')

        row += 1
        self.auxiliaryFilesLabel = Label(parent, text="Auxiliary Files Path ", grid=(row, 0))
        self.auxiliaryFilesData = LineEdit(parent, grid=(row, 1), hAlign='l')
        self.auxiliaryFilesData.setMinimumWidth(LineEditsMinimumWidth)
        self.auxiliaryFilesDataButton = Button(parent, grid=(row, 2), callback=self._getAuxiliaryFilesPath,
                                               icon='icons/directory', hPolicy='fixed')
        self.auxiliaryFilesData.setText(self.preferences.general.auxiliaryFilesPath)
        self.auxiliaryFilesData.editingFinished.connect(self._setAuxiliaryFilesPath)

        row += 1
        self.macroPathLabel = Label(parent, text="Macro Path", grid=(row, 0))
        self.macroPathData = LineEdit(parent, grid=(row, 1), hAlign='l')
        self.macroPathData.setMinimumWidth(LineEditsMinimumWidth)
        self.macroPathData.setText(self.preferences.general.userMacroPath)
        self.macroPathDataButton = Button(parent, grid=(row, 2), callback=self._getMacroFilesPath,
                                          icon='icons/directory', hPolicy='fixed')
        self.macroPathData.editingFinished.connect(self._setMacroFilesPath)

        row += 1
        self.pluginPathLabel = Label(parent, text="Plugin Path", grid=(row, 0))
        self.pluginPathData = LineEdit(parent, grid=(row, 1), hAlign='l', tipText=NotImplementedTipText)
        self.pluginPathData.setMinimumWidth(LineEditsMinimumWidth)
        self.pluginPathData.setText(self.preferences.general.userPluginPath)
        self.pluginPathDataButton = Button(parent, grid=(row, 2), callback=self._getPluginFilesPath,
                                           icon='icons/directory', hPolicy='fixed')
        self.pluginPathData.editingFinished.connect(self._setPluginFilesPath)
        # TODO enable plugin PathData
        self.pluginPathData.setDisabled(True)
        self.pluginPathDataButton.setDisabled(True)

        row += 1
        self.pipesPathLabel = Label(parent, text="Pipes Path", grid=(row, 0), )
        self.pipesPathData = LineEdit(parent, grid=(row, 1), hAlign='l', tipText=NotImplementedTipText)
        self.pipesPathData.setMinimumWidth(LineEditsMinimumWidth)
        self.pipesPathData.setText(self.preferences.general.userExtensionPath)
        self.pipesPathDataButton = Button(parent, grid=(row, 2), callback=self._getExtensionFilesPath,
                                          icon='icons/directory', hPolicy='fixed')
        self.pipesPathData.editingFinished.connect(self._setPipesFilesPath)
        # TODO enable pipes PathData
        self.pipesPathData.setDisabled(True)
        self.pipesPathDataButton.setDisabled(True)

        # row += 1
        # self.annotationsLabel = Label(parent, text="Annotations", grid=(row, 0))
        # try:
        #   annType = self.preferences.general.annotationType
        # except:
        #   annType = 0
        #   self.preferences.general.annotationType = annType
        # self.annotationsData = RadioButtons(parent, texts=['Short', 'Full', 'Pid'],
        #                                                    selectedInd=annType,
        #                                                    callback=self._setAnnotations,
        #                                                    direction='horizontal',
        #                                                    grid=(row, 1), hAlign='l',
        #                                                    tipTexts=None,
        #                                                    )

        # row += 1
        Spacer(parent, row, 1,
               QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding,
               grid=(row, 0), gridSpan=(row, 1))

    def _setspectrumTabWidgets(self, parent):
        ''' Insert a widget in here to appear in the Spectrum Tab. Parent = the Frame obj where the widget should live'''

        row = 0
        self.dataPathLabel = Label(parent, "User Data Path", grid=(row, 0), )
        self.dataPathText = LineEdit(parent, grid=(row, 1), hAlign='l')
        self.dataPathText.setMinimumWidth(LineEditsMinimumWidth)
        self.dataPathText.editingFinished.connect(self._setDataPath)
        self.dataPathText.setText(self.preferences.general.dataPath)
        self.dataPathButton = Button(parent, grid=(row, 2), callback=self._getDataPath, icon='icons/directory',
                                     hPolicy='fixed')

        row += 1
        self.regionPaddingLabel = Label(parent, text="Spectral Padding (%)", grid=(row, 0))
        self.regionPaddingData = DoubleSpinbox(parent, grid=(row, 1), hAlign='l', decimals=1, step=0.1, min=0, max=100)
        self.regionPaddingData.setMinimumWidth(LineEditsMinimumWidth)
        self.regionPaddingData.setValue(float('%.1f' % (100 * self.preferences.general.stripRegionPadding)))
        self.regionPaddingData.editingFinished.connect(self._setRegionPadding)

        row += 1
        self.dropFactorLabel = Label(parent, text="Peak Picking Drop (%)", grid=(row, 0))
        self.dropFactorData = DoubleSpinbox(parent, grid=(row, 1), hAlign='l', decimals=1, step=0.1, min=0, max=100)
        self.dropFactorData.setMinimumWidth(LineEditsMinimumWidth)
        self.dropFactorData.setValue(float('%.1f' % (100 * self.preferences.general.peakDropFactor)))
        self.dropFactorData.editingFinished.connect(self._setDropFactor)

        ### Not fully Tested, Had some issues with $Path routines in setting the path of the copied spectra.
        ###  Needs more testing for different spectra formats etc. Disabled until completion.
        # row += 1
        # self.keepSPWithinProjectTipText = 'Keep a copy of spectra inside the project directory. Useful when changing the original spectra location path'
        # self.keepSPWithinProject = Label(parent, text="Keep a Copy Inside Project: ", grid=(row, 0))
        # self.keepSPWithinProjectBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.keepSpectraInsideProject,
        #                                        tipText=self.keepSPWithinProjectTipText)
        # self.keepSPWithinProjectBox.toggled.connect(partial(self._toggleGeneralOptions, 'keepSpectraInsideProject'))

        row += 1
        self.showToolbarLabel = Label(parent, text="Show ToolBar(s): ", grid=(row, 0))
        self.showToolbarBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.showToolbar)
        self.showToolbarBox.toggled.connect(partial(self._toggleGeneralOptions, 'showToolbar'))

        row += 1
        self.spectrumBorderLabel = Label(parent, text="Show Spectrum Border: ", grid=(row, 0))
        self.spectrumBorderBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.showSpectrumBorder)
        self.spectrumBorderBox.toggled.connect(partial(self._toggleGeneralOptions, 'showSpectrumBorder'))

        row += 1
        self.showGridLabel = Label(parent, text="Show Grids: ", grid=(row, 0))
        self.showGridBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.showGrid)
        self.showGridBox.toggled.connect(partial(self._toggleGeneralOptions, 'showGrid'))

        row += 1
        self.showLastAxisOnlyLabel = Label(parent, text="Share Y Axis: ", grid=(row, 0))
        self.showLastAxisOnlyBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.lastAxisOnly)
        self.showLastAxisOnlyBox.toggled.connect(partial(self._toggleGeneralOptions, 'lastAxisOnly'))

        row += 1
        self.matchAxisCodeLabel = Label(parent, text="Match Axis Codes", grid=(row, 0))
        matchAxisCode = self.preferences.general.matchAxisCode
        self.matchAxisCode = RadioButtons(parent, texts=['Atom Type', 'Full Axis Code'],
                                          selectedInd=matchAxisCode,
                                          callback=self._setMatchAxisCode,
                                          direction='h',
                                          grid=(row, 1), hAlign='l',
                                          tipTexts=None,
                                          )
        row += 1
        HLine(parent, grid=(row, 0), gridSpan=(1, 3), colour=getColours()[DIVIDER], height=15)

        # row += 1
        #self.showDoubleCursorLabel = Label(parent, text="Show Double Cursor: ", grid=(row, 0))
        #self.showDoubleCursorBox = CheckBox(parent, grid=(row, 1), tipText=NotImplementedTipText)#, checked=self.preferences.general.showDoubleCursor)
        # TODO enable DoubleCursor
        #self.showDoubleCursorBox.setDisabled(True)
        ## self.showDoubleCursorBox.toggled.connect(partial(self._toggleGeneralOptions, 'showDoubleCursor'))

        # row += 1
        # Spacer(parent, row, 1
        #        , QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        #        , grid=(row , 0), gridSpan=(row, 1))

        # row += 1
        # self.peakSymbolsLabel = Label(parent, text="Peak Symbols", grid=(row, 0))
        # peakSymbol = self.preferences.general.peakSymbolType
        # self.peakSymbol = RadioButtons(parent, texts=['Cross', 'lineWidths', 'Filled lineWidths'],
        #                                 selectedInd=peakSymbol,
        #                                 callback=self._setPeakSymbol,
        #                                 direction='v',
        #                                 grid=(row, 1), hAlign='l',
        #                                 tipTexts=None,
        #                                 )
        # row += 1
        # self.peakSymbolSizeLabel = Label(parent, text="Peak Symbol Size (ppm)", grid=(row, 0))
        # self.peakSymbolSizeData = DoubleSpinbox(parent, decimals=3, step=0.01
        #                                         , min=0.01, max=1.0, grid=(row, 1), hAlign='l')
        # self.peakSymbolSizeData.setMinimumWidth(LineEditsMinimumWidth)
        # symbolSize = self.preferences.general.peakSymbolSize
        # self.peakSymbolSizeData.setValue(float('%.3f' % symbolSize))
        # self.peakSymbolSizeData.editingFinished.connect(self._setPeakSymbolSize)
        #
        # row += 1
        # self.peakSymbolThicknessLabel = Label(parent, text="Peak Symbol Thickness (point)", grid=(row, 0))
        # self.peakSymbolThicknessData = Spinbox(parent, step=1
        #                                         , min=1, max=20, grid=(row, 1), hAlign='l')
        # self.peakSymbolThicknessData.setMinimumWidth(LineEditsMinimumWidth)
        # symbolThickness = self.preferences.general.peakSymbolThickness
        # self.peakSymbolThicknessData.setValue(int(symbolThickness))
        # self.peakSymbolThicknessData.editingFinished.connect(self._setPeakSymbolThickness)

        row += 1
        self.zoomCentreLabel = Label(parent, text="Zoom Centre", grid=(row, 0))
        zoomCentre = self.preferences.general.zoomCentreType
        self.zoomCentre = RadioButtons(parent, texts=['Mouse', 'Screen'],
                                       selectedInd=zoomCentre,
                                       callback=self._setZoomCentre,
                                       direction='h',
                                       grid=(row, 1), hAlign='l',
                                       tipTexts=None,
                                       )
        # self.zoomCentre.setEnabled(False)

        row += 1
        zoomPercent = self.preferences.general.zoomPercent
        self.zoomPercentLabel = Label(parent, text="Manual Zoom (%)", grid=(row, 0))
        self.zoomPercentData = DoubleSpinbox(parent, step=1
                                             , min=1, max=100, grid=(row, 1), hAlign='l')
        self.zoomPercentData.setValue(int(zoomPercent))
        self.zoomPercentData.setMinimumWidth(LineEditsMinimumWidth)
        self.zoomPercentData.editingFinished.connect(self._setZoomPercent)

        row += 1
        stripWidthZoomPercent = self.preferences.general.stripWidthZoomPercent
        self.stripWidthZoomPercentLabel = Label(parent, text="Strip Width Zoom (%)", grid=(row, 0))
        self.stripWidthZoomPercentData = DoubleSpinbox(parent, step=1
                                                       , min=1, max=100, grid=(row, 1), hAlign='l')
        self.stripWidthZoomPercentData.setValue(int(stripWidthZoomPercent))
        self.stripWidthZoomPercentData.setMinimumWidth(LineEditsMinimumWidth)
        self.stripWidthZoomPercentData.editingFinished.connect(self._setStripWidthZoomPercent)

        # row += 1
        # self.matchAxisCodeLabel = Label(parent, text="Match Axis Codes", grid=(row, 0))
        # matchAxisCode = self.preferences.general.matchAxisCode
        # self.matchAxisCode = RadioButtons(parent, texts=['Atom Type', 'Full Axis Code'],
        #                                 selectedInd=matchAxisCode,
        #                                 callback=self._setMatchAxisCode,
        #                                 direction='v',
        #                                 grid=(row, 1), hAlign='l',
        #                                 tipTexts=None,
        #                                 )

        # row += 1
        # self.showGridLabel = Label(parent, text="Show Grids: ", grid=(row, 0))
        # self.showGridBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.showGrid)
        # self.showGridBox.toggled.connect(partial(self._toggleGeneralOptions, 'showGrid'))
        #
        # row += 1
        # self.showLastAxisOnlyLabel = Label(parent, text="Share Y Axis: ", grid=(row, 0))
        # self.showLastAxisOnlyBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.lastAxisOnly)
        # self.showLastAxisOnlyBox.toggled.connect(partial(self._toggleGeneralOptions, 'lastAxisOnly'))

        row += 1
        self.lockAspectRatioLabel = Label(parent, text="Aspect Ratios: ", grid=(row, 0))
        # self.lockAspectRatioBox = CheckBox(parent, grid=(row, 1), checked=self.preferences.general.lockAspectRatio)
        # self.lockAspectRatioBox.toggled.connect(partial(self._toggleGeneralOptions, 'lockAspectRatio'))

        self.aspectLabel = {}
        self.aspectData = {}
        for aspect in sorted(self.preferences.general.aspectRatios.keys()):
            aspectValue = self.preferences.general.aspectRatios[aspect]
            self.aspectLabel[aspect] = Label(parent, text=aspect, grid=(row, 0), hAlign='r')
            self.aspectData[aspect] = DoubleSpinbox(parent, step=1
                                                    , min=1, grid=(row, 1), hAlign='l')
            self.aspectData[aspect].setValue(aspectValue)
            self.aspectData[aspect].setMinimumWidth(LineEditsMinimumWidth)
            self.aspectData[aspect].editingFinished.connect(partial(self._setAspect, aspect))
            row += 1

        row += 1
        HLine(parent, grid=(row, 0), gridSpan=(1, 3), colour=getColours()[DIVIDER], height=15)

        row += 1
        self.annotationsLabel = Label(parent, text="Peak Annotations", grid=(row, 0))
        try:
            annType = self.preferences.general.annotationType
        except:
            annType = 0
            self.preferences.general.annotationType = annType
        self.annotationsData = RadioButtons(parent, texts=['Short', 'Full', 'Pid'],
                                            selectedInd=annType,
                                            callback=self._setAnnotations,
                                            direction='horizontal',
                                            grid=(row, 1), hAlign='l',
                                            tipTexts=None,
                                            )
        row += 1
        self.peakSymbolsLabel = Label(parent, text="Peak Symbols", grid=(row, 0))
        peakSymbol = self.preferences.general.peakSymbolType
        self.peakSymbol = RadioButtons(parent, texts=['Cross', 'lineWidths', 'Filled lineWidths'],
                                       selectedInd=peakSymbol,
                                       callback=self._setPeakSymbol,
                                       direction='h',
                                       grid=(row, 1), hAlign='l',
                                       tipTexts=None,
                                       )
        row += 1
        self.peakSymbolSizeLabel = Label(parent, text="Peak Symbol Size (ppm)", grid=(row, 0))
        self.peakSymbolSizeData = DoubleSpinbox(parent, decimals=3, step=0.01
                                                , min=0.01, max=1.0, grid=(row, 1), hAlign='l')
        self.peakSymbolSizeData.setMinimumWidth(LineEditsMinimumWidth)
        symbolSize = self.preferences.general.peakSymbolSize
        self.peakSymbolSizeData.setValue(float('%.3f' % symbolSize))
        self.peakSymbolSizeData.editingFinished.connect(self._setPeakSymbolSize)

        row += 1
        self.peakSymbolThicknessLabel = Label(parent, text="Peak Symbol Thickness (point)", grid=(row, 0))
        self.peakSymbolThicknessData = Spinbox(parent, step=1
                                               , min=1, max=20, grid=(row, 1), hAlign='l')
        self.peakSymbolThicknessData.setMinimumWidth(LineEditsMinimumWidth)
        symbolThickness = self.preferences.general.peakSymbolThickness
        self.peakSymbolThicknessData.setValue(int(symbolThickness))
        self.peakSymbolThicknessData.editingFinished.connect(self._setPeakSymbolThickness)

    def _setExternalProgramsTabWidgets(self, parent):
        """
        Insert a widget in here to appear in the externalPrograms Tab
        """

        row = 0

        self.dataPathLabel = Label(parent, "Pymol Path", grid=(row, 0), )
        self.pymolPath = LineEdit(parent, text='', grid=(row, 1), hAlign='l')
        self.pymolPath.setMinimumWidth(LineEditsMinimumWidth)
        self.pymolPath.editingFinished.connect(self._setPymolPath)
        self.pymolPath.setText(self.preferences.externalPrograms.pymol)
        self.pymolPathButton = Button(parent, grid=(row, 2), callback=self._getPymolPath, icon='icons/directory',
                                      hPolicy='fixed')

        self.testPymolPathButton = Button(parent, grid=(row, 3), callback=self._testPymol,
                                          text='test', hPolicy='fixed')

    def _testPymol(self):
        program = self.pymolPath.get()
        if not self._testExternalProgram(program):
            self.sender().setText('Failed')
        else:
            self.sender().setText('Success')

    def _testExternalProgram(self, program):
        import subprocess
        try:
            # TODO:ED check whether relative or absolute path and test
            # import ccpn.framework.PathsAndUrls as PAU
            # pathCwd = PAU.ccpnCodePath
            # programPath = os.path.abspath(os.path.join(pathCwd, program))

            p = subprocess.Popen(program,
                                 shell=False,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            return True

        except Exception as e:
            getLogger().warning('Testing External program: Failed.' + str(e))
            return False

    def _getDataPath(self):
        if os.path.exists('/'.join(self.dataPathText.text().split('/')[:-1])):
            currentDataPath = '/'.join(self.dataPathText.text().split('/')[:-1])
        else:
            currentDataPath = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Data File', directory=currentDataPath, fileMode=2, acceptMode=0,
                            preferences=self.preferences.general)
        directory = dialog.selectedFiles()
        if directory:
            self.dataPathText.setText(directory[0])
            self.preferences.general.dataPath = directory[0]

    def _setDataPath(self):
        if self.dataPathText.isModified():
            newPath = self.dataPathText.text()
            self.preferences.general.dataPath = newPath
            dataUrl = self.project._apiNmrProject.root.findFirstDataLocationStore(
                    name='standard').findFirstDataUrl(name='remoteData')
            dataUrl.url = Implementation.Url(path=newPath)

    def _getAuxiliaryFilesPath(self):
        if os.path.exists(os.path.expanduser(self.auxiliaryFilesData.text())):
            currentDataPath = os.path.expanduser(self.auxiliaryFilesData.text())
        else:
            currentDataPath = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Data File', directory=currentDataPath, fileMode=2, acceptMode=0,
                            preferences=self.preferences.general)
        directory = dialog.selectedFiles()
        if len(directory) > 0:
            self.auxiliaryFilesData.setText(directory[0])
            self.preferences.general.auxiliaryFilesPath = directory[0]

    def _setAuxiliaryFilesPath(self):
        newPath = self.auxiliaryFilesData.text()
        self.preferences.general.auxiliaryFilesPath = newPath

    def _getMacroFilesPath(self):
        if os.path.exists(os.path.expanduser(self.macroPathData.text())):
            currentDataPath = os.path.expanduser(self.macroPathData.text())
        else:
            currentDataPath = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Data File', directory=currentDataPath, fileMode=2, acceptMode=0,
                            preferences=self.preferences.general)
        directory = dialog.selectedFiles()
        if len(directory) > 0:
            self.macroPathData.setText(directory[0])
            self.preferences.general.userMacroPath = directory[0]

    def _getPluginFilesPath(self):
        if os.path.exists(os.path.expanduser(self.pluginPathData.text())):
            currentDataPath = os.path.expanduser(self.pluginPathData.text())
        else:
            currentDataPath = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Data File', directory=currentDataPath, fileMode=2, acceptMode=0,
                            preferences=self.preferences.general)
        directory = dialog.selectedFiles()
        if len(directory) > 0:
            self.pluginPathData.setText(directory[0])
            self.preferences.general.pluginMacroPath = directory[0]

    def _getExtensionFilesPath(self):
        if os.path.exists(os.path.expanduser(self.pipesPathData.text())):
            currentDataPath = os.path.expanduser(self.pipesPathData.text())
        else:
            currentDataPath = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Data File', directory=currentDataPath, fileMode=2, acceptMode=0,
                            preferences=self.preferences.general)
        directory = dialog.selectedFiles()
        if len(directory) > 0:
            self.pipesPathData.setText(directory[0])
            self.preferences.general.userExtensionPath = directory[0]

    def _setMacroFilesPath(self):
        newPath = self.macroPathData.text()
        self.preferences.general.userMacroPath = newPath

    def _setPluginFilesPath(self):
        newPath = self.pluginPathData.text()
        self.preferences.general.userPluginPath = newPath

    def _setPipesFilesPath(self):
        newPath = self.pipesPathData.text()
        self.preferences.general.userExtensionPath = newPath

    def _changeLanguage(self, value):
        self.preferences.general.language = (languages[value])

    def _changeColourScheme(self, value):
        self.preferences.general.colourScheme = (COLOUR_SCHEMES[value])

    def _toggleGeneralOptions(self, preference, checked):
        self.preferences.general[preference] = checked
        if preference == 'showToolbar':
            for spectrumDisplay in self.project.spectrumDisplays:
                spectrumDisplay.spectrumUtilToolBar.setVisible(checked)
        elif preference == 'showSpectrumBorder':
            for strip in self.project.strips:
                for spectrumView in strip.spectrumViews:
                    spectrumView._setBorderItemHidden(checked)
        elif preference == 'autoBackupEnabled':
            self.application.updateAutoBackup()

    def _setPymolPath(self):
        pymolPath = self.pymolPath.get()
        if 'externalPrograms' in self.preferences:
            if 'pymol' in self.preferences.externalPrograms:
                self.preferences.externalPrograms.pymol = pymolPath
        self.testPymolPathButton.setText('test')

    def _getPymolPath(self):

        dialog = FileDialog(self, text='Select File', preferences=self.preferences.general)
        file = dialog.selectedFile()
        if file:
            self.pymolPath.setText(file)

    def _setAutoBackupFrequency(self):
        try:
            frequency = int(self.autoBackupFrequencyData.text())
        except:
            return
        self.preferences.general.autoBackupFrequency = frequency
        self.application.updateAutoBackup()

    def _setRegionPadding(self):
        try:
            padding = 0.01 * float(self.regionPaddingData.text())
        except:
            return
        self.preferences.general.stripRegionPadding = padding

    def _setDropFactor(self):
        try:
            dropFactor = 0.01 * float(self.dropFactorData.text())
        except:
            return
        self.preferences.general.peakDropFactor = dropFactor

    def _setPeakSymbolSize(self):
        """
        Set the size of the peak symbols (ppm)
        """
        try:
            peakSymbolSize = float(self.peakSymbolSizeData.text())
        except:
            return
        self.preferences.general.peakSymbolSize = peakSymbolSize

    def _setPeakSymbolThickness(self):
        """
        Set the Thickness of the peak symbols (ppm)
        """
        try:
            peakSymbolThickness = int(self.peakSymbolThicknessData.text())
        except:
            return
        self.preferences.general.peakSymbolThickness = peakSymbolThickness

    def _toggleSpectralOptions(self, preference, checked):
        self.preferences.spectra[preference] = str(checked)

    def _setAnnotations(self):
        """
        Set the annotation type for the pid labels
        """
        try:
            annotationType = self.annotationsData.getIndex()
        except:
            return
        self.preferences.general.annotationType = annotationType

    def _setPeakSymbol(self):
        """
        Set the peak symbol type - current a cross or lineWidths
        """
        try:
            peakSymbol = self.peakSymbol.getIndex()
        except:
            return
        self.preferences.general.peakSymbolType = peakSymbol

    def _setZoomCentre(self):
        """
        Set the zoom centring method to either mouse position or centre of the screen
        """
        try:
            zoomCentre = self.zoomCentre.getIndex()
        except:
            return
        self.preferences.general.zoomCentreType = zoomCentre

    def _setZoomPercent(self):
        """
        Set the value for manual zoom
        """
        try:
            zoomPercent = float(self.zoomPercentData.text())
        except:
            return
        self.preferences.general.zoomPercent = zoomPercent

    def _setStripWidthZoomPercent(self):
        """
        Set the value for increasing/decreasing width of strips
        """
        try:
            stripWidthZoomPercent = float(self.stripWidthZoomPercentData.text())
        except:
            return
        self.preferences.general.stripWidthZoomPercent = stripWidthZoomPercent

    def _setMatchAxisCode(self):
        """
        Set the matching of the axis codes across different strips
        """
        try:
            matchAxisCode = self.matchAxisCode.getIndex()
        except:
            return
        self.preferences.general.matchAxisCode = matchAxisCode

    def _setAspect(self, aspect):
        """
        Set the aspect ratio for the axes
        """
        try:
            aspectValue = float(self.aspectData[aspect].text())
        except Exception as es:
            return
        self.preferences.general.aspectRatios[aspect] = aspectValue
