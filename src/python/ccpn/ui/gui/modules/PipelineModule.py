"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:14 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"

__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#====================================




import collections
import json
import time
import os

from collections import OrderedDict
from ccpn.core.lib.Notifiers import Notifier
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
from ccpn.framework.lib.Pipeline import Pipeline
import pandas as pd
from PyQt4 import QtCore, QtGui
from ccpn.ui.gui.lib.GuiNotifier import GuiNotifier
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.FileDialog import FileDialog, LineEditButtonDialog
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.PipelineWidgets import PipelineDropArea
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, AutoGeneratedGuiPipe


Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence
DropHereLabel = 'Drop here SP or SG'
# styleSheets
transparentStyle = "background-color: transparent; border: 0px solid transparent"
selectPipeLabel = '< Select Pipe >'
preferredPipeLabel = '-- Preferred Pipes --'
otherPipeLabel =     '-- Other Pipes --'

class PipelineWorker(QtCore.QObject):
  'Object managing the  auto run pipeline simulation'

  stepIncreased = QtCore.pyqtSignal(int)

  def __init__(self):
    super(PipelineWorker, self).__init__()
    self._step = 0
    self._isRunning = True
    self._maxSteps = 200000

  def task(self):
    if not self._isRunning:
      self._isRunning = True
      self._step = 0

    while self._step < self._maxSteps and self._isRunning == True:
      self._step += 1
      self.stepIncreased.emit(self._step)
      time.sleep(0.1)  # if this time is too small or disabled you won't be able to stop the thread!

  def stop(self):
    self._isRunning = False
    print('Pipeline Thread stopped')



class GuiPipeline(CcpnModule, Pipeline):

  includeSettingsWidget = True
  maxSettingsState = 2
  settingsPosition = 'left'
  className = 'GuiPipeline'
  moduleName = 'Pipeline-'



  def __init__(self, mainWindow, name='', pipes=None, templates=None, **kw):
    super(GuiPipeline, self)


    # this guarantees to open the module as Gui testing
    self.project = None
    self.application = None
    self.savingDataPath = os.path.expanduser("~")+'/'

    # set project related variables
    if mainWindow is not None:
      self.mainWindow = mainWindow
      self.project = self.mainWindow.project
      self.application = self.mainWindow.application
      self.moduleArea = self.mainWindow.moduleArea
      self.preferences = self.application.preferences
      self.current = self.application.current

      # FIXME hack to give serial number to the pipeline module
      nameCount = 1
      for module in self.mainWindow.moduleArea.currentModules:
        if isinstance(module, GuiPipeline):
          nameCount += 1
      name = self.moduleName + str(nameCount)

      self.generalPreferences = self.application.preferences.general
      self.templatePath = self.generalPreferences.auxiliaryFilesPath
      self.savingDataPath = str(self.generalPreferences.dataPath)
      self.savingDataPath = str(self.generalPreferences.dataPath)




    # init the CcpnModule
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name, closeFunc=self._closeAllGuiPipes)

    # init the Pipeline
    Pipeline.__init__(self, application=self.application, pipelineName=name, pipes=pipes)

    self.pipelineSettingsParams = OrderedDict([('name', 'NewPipeline'),
                                               ('rename', 'NewPipeline'),
                                               ('savePath', self.savingDataPath),
                                               ('autoRun', False), ('addPosit', 'bottom'),
                                               ('autoActive', True), ])

    # set pipeline variables

    # self.pipes = pipes
    self.guiPipes = self._getGuiFromPipes(self.pipes)
    self.currentRunningPipeline = []
    self.currentGuiPipesNames = []
    self.pipelineTemplates = templates

    # set the graphics
    self._setIcons()
    self._setMainLayout()
    self._setPipelineThread()
    self._setSecondaryLayouts()

    # start the pipelineWorker
    self.pipelineWorker.stepIncreased.connect(self._runPipeline)


    # set notifier
    if self.project is not None:
      self._inputDataDeletedNotifier = Notifier(self.project, [Notifier.DELETE], 'Spectrum', self._updateInputData)



  def _getGuiFromPipes(self, pipes):
    allGuiPipes = []
    for pipe in pipes:
      if pipe:
        try:
          if pipe.guiPipe is not None:
            guiPipe = pipe.guiPipe
            guiPipe.pipe = pipe
            allGuiPipes.append(guiPipe)
          else: #deal with pipes without Gui -> Creates just an empty GuiPipe
            newEmptyPipe = GuiPipe
            pipe.guiPipe = newEmptyPipe
            newEmptyPipe.pipe = pipe
            newEmptyPipe.pipeName = pipe.pipeName
            newEmptyPipe.preferredPipe = False
            allGuiPipes.append(newEmptyPipe)
        except:
          # TODO handle exceptions if any
          pass
    return allGuiPipes

  @property
  def guiPipes(self):
    return self._guiPipes

  @guiPipes.setter
  def guiPipes(self, guiPipes):
    '''
    Set the guiPipes to the guiPipeline
    :param guiPipes:  GuiPipe class
    '''

    if guiPipes is not None:
      allGuiPipes = []
      for guiPipe in guiPipes:
         allGuiPipes.append(guiPipe)
      self._guiPipes = allGuiPipes
    else:
      self._guiPipes = []

  @property
  def pipelineTemplates(self):
    return self._pipelineTemplates

  @pipelineTemplates.setter
  def pipelineTemplates(self, pipelineTemplates):
    '''
    Set the pipelineTemplates to the guiPipeline
    :param pipelineTemplates:  [{templateName: templateClass}]
    '''

    if pipelineTemplates is not None:
      self._pipelineTemplates = pipelineTemplates
    else:
      self._pipelineTemplates = []

      #  TODO put notifier to update the pulldown when guiPipes change




  ####################################_________ GUI SETUP ____________###########################################
  def _setIcons(self):
    self.settingIcon = Icon('icons/applications-system')
    self.saveIcon = Icon('icons/save')
    self.openRecentIcon = Icon('icons/document_open_recent')
    self.goIcon = Icon('icons/play')
    self.stopIcon = Icon('icons/stop')
    self.filterIcon = Icon('icons/edit-find')

  def _setMainLayout(self):
    self.mainFrame = Frame(self.mainWidget, setLayout=False)
    self.mainLayout = QtGui.QVBoxLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.mainWidget.getLayout().addWidget(self.mainFrame, 0, 0, 0 ,0)

  def _setSecondaryLayouts(self):
    self.settingFrameLayout = QtGui.QHBoxLayout()
    self.goAreaLayout = QtGui.QHBoxLayout()
    self.pipelineAreaLayout = QtGui.QHBoxLayout()
    self.mainLayout.addLayout(self.settingFrameLayout)
    self.mainLayout.addLayout(self.goAreaLayout)
    self.mainLayout.addLayout(self.pipelineAreaLayout)
    self._createSettingButtonGroup()
    self._createPipelineWidgets()
    self._createSettingWidgets()

  def _createSettingButtonGroup(self):
    self.nameLabel = Label(self, 'Pipeline Name:')
    self.pipelineNameLabel = Label(self, 'NewPipeline')
    self.settingButtons = ButtonList(self, texts=['', ''],
                                     callbacks=[self._openSavedPipeline, self._savePipeline],
                                     icons=[self.openRecentIcon, self.saveIcon],
                                     tipTexts=['', ''], direction='H')
    self.settingFrameLayout.addWidget(self.nameLabel)
    self.settingFrameLayout.addWidget(self.pipelineNameLabel)

    self._addMenuToOpenButton()
    self.settingButtons.setStyleSheet(transparentStyle)
    self.settingFrameLayout.addStretch(1)
    self.settingFrameLayout.addWidget(self.settingButtons)

  def _addMenuToOpenButton(self):
    openButton = self.settingButtons.buttons[0]
    menu = QtGui.QMenu()
    templatesItem = menu.addAction('Templates')
    subMenu = QtGui.QMenu()
    if self.pipelineTemplates is not None:
      for item in self.pipelineTemplates:
        templatesSubItem = subMenu.addAction(item)
      openItem = menu.addAction('Open...', self._openSavedPipeline)
      templatesItem.setMenu(subMenu)
    openButton.setMenu(menu)


  def _createPipelineWidgets(self):
    self._addPipesPullDownWidget()
    self._addGoButtonWidget()
    self._addPipelineDropArea()


  def _addPipesPullDownWidget(self):
    self.pipePulldown = PulldownList(self, )
    self.pipePulldown.setMinimumWidth(200)
    self.goAreaLayout.addWidget(self.pipePulldown)
    self._setDataPipesPulldown()
    self.pipePulldown.installEventFilter(self)


  def _setDataPipesPulldown(self):
    self.pipePulldownData = [selectPipeLabel, ]
    preferredGuiPipes = [preferredPipeLabel, ]
    otherGuiPipes = [otherPipeLabel, ]


    for guiPipe in self.guiPipes:
      if guiPipe is not None:
        if guiPipe.preferredPipe:
          preferredGuiPipes.append(guiPipe.pipe.pipeName)
        else:
          otherGuiPipes.append(guiPipe.pipe.pipeName)
    self.pipePulldownData.extend(preferredGuiPipes)
    self.pipePulldownData.extend(otherGuiPipes)

    self.pipePulldown.setData(self.pipePulldownData)

    disablePreferredPipeLabel = self.pipePulldown.getItemIndex(preferredPipeLabel)
    self.pipePulldown.model().item(disablePreferredPipeLabel).setEnabled(False)
    disableOtherPipeLabel = self.pipePulldown.getItemIndex(otherPipeLabel)
    self.pipePulldown.model().item(disableOtherPipeLabel).setEnabled(False)

    # self.pipePulldown.insertSeparator(countPreferredGuiPipes)
    self.pipePulldown.activated[str].connect(self._selectPipe)

  def _updatePipePulldown(self):
    if len(self.guiPipes) != len(self.pipes):
      self.guiPipes = self._getGuiFromPipes(self.pipes)
    self._setDataPipesPulldown()

  def eventFilter(self, source, event):
    '''Filter to disable the wheel event in the guiPipes pulldown. Otherwise each scroll would add a guiPipe!'''
    if event.type() == QtCore.QEvent.Wheel:
      return True
    return False

  def _addGoButtonWidget(self):
    '''
    First Two button are reserved for autoRun mode. They are hidden if the setting autoRun is not checked.
    NB the stop callback needs to be a lambda call

    '''
    self.goButton = ButtonList(self, texts=['','',''], icons=[self.stopIcon, self.goIcon, self.goIcon,],
                               callbacks=[lambda:self.pipelineWorker.stop(), self.pipelineWorker.task, self._runPipeline],
                               hAlign='c')
    self.goButton.buttons[0].hide()
    self.goButton.buttons[1].hide()
    self.goButton.setStyleSheet(transparentStyle)
    self.goAreaLayout.addWidget(self.goButton, )
    self.goAreaLayout.addStretch(1)
    self.goButton.setEnabled(False)

  def _addPipelineDropArea(self):
    self.pipelineArea = PipelineDropArea()
    scroll = ScrollArea(self)
    scroll.setWidget(self.pipelineArea)
    scroll.setWidgetResizable(True)
    self.pipelineAreaLayout.addWidget(scroll)


  def _closeAllGuiPipes(self):
    guiPipes = self.pipelineArea.currentGuiPipes
    if len(guiPipes) > 0:
      for guiPipe in guiPipes:
        guiPipe._closeBox()

  def keyPressEvent(self, KeyEvent):
    ''' Run the pipeline by pressing the enter key '''
    if KeyEvent.key() == Qt.Key_Enter:
      self._runPipeline()

  def _getSerialName(self, guiPipeName):
    self.currentGuiPipesNames.append(guiPipeName)
    count = len(self.pipelineArea.findAll()[1])
    if count == 0:
      self.currentGuiPipesNames = []
    counter = collections.Counter(self.currentGuiPipesNames)
    return str(guiPipeName) + '-' + str(counter[str(guiPipeName)])


  ####################################_________ GUI CallBacks ____________###########################################

  def _selectPipe(self, selected):

    guiPipeName = self._getSerialName(str(selected))
    self._addGuiPipe(guiPipeName, selected)
    self.pipePulldown.setIndex(0)



  def _addGuiPipe(self, name, selected):
    for guiPipe in self.guiPipes:
      if guiPipe.pipeName == selected:
        position = self.pipelineSettingsParams['addPosit']
        guiPipe = guiPipe(parent=self, application=self.application, name=name, project=self.project)
        self.pipelineArea.addDock(guiPipe, position=position)
        autoActive = self.pipelineSettingsParams['autoActive']
        guiPipe.label.checkBox.setChecked(autoActive)


  def _runPipeline(self):

    self.queue = []
    if self.inputData:
      if len(self.pipelineArea.findAll()[1]) > 0:
        guiPipes = self.pipelineArea.orderedBoxes(self.pipelineArea.topContainer)
        for guiPipe in guiPipes:
          if guiPipe.isActive:
            guiPipe.pipe.isActive = True
            guiPipe.pipe._kwargs = guiPipe.widgetsState
            self.queue.append(guiPipe.pipe)

          else:
            guiPipe.pipe.isActive = False


      self.runPipeline()



  def _closeModule(self):
    """Re-implementation of closeModule function from CcpnModule to unregister notification """
    self._unregisterNotifier()
    super(GuiPipeline, self)._closeModule()

  def close(self):
    """
    Close the table from the commandline
    """
    self._closeModule()


  ####################################_________ others____________###########################################

  def _unregisterNotifier(self):
    "Cleanup of Notifierers"
    if self._inputDataDeletedNotifier:
      self._inputDataDeletedNotifier.unRegister()

  def _getGuiPipeClassFromClassName(self, name):
    for guiPipe in self.guiPipes:
      if guiPipe.__name__ == name:
        print('guiPipe.__name__ == name', name)
        return guiPipe

  def _getGuiPipeClass(self, name):
    for guiPipe in self.guiPipes:
      if guiPipe.pipeName == name:
        return guiPipe

  ####################################_________ Thread  SETUP ____________##############################################
  def _setPipelineThread(self):
    self.pipelineThread = QtCore.QThread()
    self.pipelineThread.start()
    self.pipelineWorker = PipelineWorker()
    self.pipelineWorker.moveToThread(self.pipelineThread)



  ####################################_________ Saving Restoring  SETUP ____________####################################
  def _openJsonFile(self, path):
    if path is not None:
      with open(str(path), 'r') as jf:
        data = json.load(jf)
      return data

  def _getPathFromDialogBox(self):
    dialog = FileDialog(self, text="Open Pipeline",
                        acceptMode=FileDialog.AcceptOpen)
    return dialog.selectedFile()

  def _getGuiPipesFromFile(self, params, guiPipesNames):
    pipelineBoxes = []
    for i in params:
      for key, value in i.items():
        if value[0].upper() in guiPipesNames:
          guiPipe = self._getGuiPipeClassFromClassName(key)
          pipelineBox = guiPipe(parent=self, application=self.application, name = value[0], params = value[1])
          pipelineBox.setActive(value[2])
          pipelineBoxes.append(pipelineBox)
    return pipelineBoxes

  def _openSavedPipeline(self):
    path = self._getPathFromDialogBox()
    state, guiPipesState, pipelineSettings = self._openJsonFile(path)
    self._closeAllGuiPipes()
    for item in guiPipesState:
      guiPipeClassName, guiPipeName, widgetsState, isActive = item
      guiPipeClass = self._getGuiPipeClassFromClassName(guiPipeClassName)
      guiPipe = guiPipeClass(parent=self, application=self.application, name=guiPipeName)
      guiPipe.restoreWidgetsState(**widgetsState)
      guiPipe.setActive(isActive)

      self.pipelineArea.addBox(guiPipe)

    self.pipelineArea.restoreState(state)
    self.pipelineSettingsParams = OrderedDict(pipelineSettings)
    self._setSettingsParams()

  def _savePipeline(self):
    '''jsonData = [{pipelineArea.state}, [guiPipesState], pipelineSettingsParams]   '''
    print('Saving')
    guiPipesState = self.pipelineArea.guiPipesState
    if len(guiPipesState)>0:
      self.jsonData = []
      self.jsonData.append(self.pipelineArea.saveState())
      self.jsonData.append(guiPipesState)
      self.jsonData.append(list(self.pipelineSettingsParams.items()))

      self._saveToJson()

  def _saveToJson(self):
    '''Tries to catch various error in giving the saving path '''
    savingPath  = str(self.savePipelineLineEdit.lineEdit.text())
    pipelineName = str(self.pipelineNameLabel.text())
    if not savingPath.endswith('.json'):
      try:
        if savingPath.endswith('/'):
          savingPath += pipelineName + '.json'
        else:
          if os.path.exists(savingPath):
            savingPath += '/'+ pipelineName + '.json'
          else:
            savingPath+='.json'
      except:
        print('Insert a valid directory path. E.g /Users/user1/Desktop/')
    self.savingDataPath = str(savingPath)

    try:
      with open(self.savingDataPath, 'w') as fp:
        json.dump(self.jsonData, fp, indent=2)
        fp.close()
      print('File saved in: ', self.savingDataPath)
    except:
      print('File not saved. Insert a valid directory path. E.g /Users/user1/Desktop/')




  #################################### _________ GUI PIPELINE SETTINGS ____________ ####################################

  def _pipelineBoxesWidgetParams(self, currentGuiPipesName):
    self.savePipelineParams = []
    for guiPipeName in currentGuiPipesName:
      guiPipe = self.pipelineArea.docks[str(guiPipeName)]
      guiPipeClassName = guiPipe.__class__.__name__
      state = guiPipe.isActive
      params = guiPipe.widgetsState
      newDict = {guiPipeClassName: (guiPipeName, params, state)}
      self.savePipelineParams.append(newDict)
    return self.savePipelineParams


  def _createSettingWidgets(self):
    self.settingsWidgets = []
    self._createSettingsGroupBox()
    self._createAllSettingWidgets()
    self._addWidgetsToLayout(self.settingsWidgets, self.settingWidgetsLayout)
    self._setSettingsParams()

  def _createSettingsGroupBox(self):
    self.settingFrame = Frame(self, setLayout=False)
    self.settingFrame.setMaximumWidth(300)
    self.settingWidgetsLayout = QtGui.QGridLayout()
    self.settingFrame.setLayout(self.settingWidgetsLayout)
    self.settingsWidget.getLayout().addWidget(self.settingFrame)

  def _getInputDataHeaderLabel(self):
    color = QtGui.QColor('Red')
    header = QtGui.QListWidgetItem(DropHereLabel)
    header.setFlags(QtCore.Qt.NoItemFlags)
    header.setTextColor(color)
    return header

  def _createAllSettingWidgets(self):
    #
    self.pipelineReNameLabel = Label(self, 'Name')
    self.settingsWidgets.append(self.pipelineReNameLabel)
    self.pipelineReNameTextEdit = LineEdit(self, str(self.pipelineNameLabel.text()))
    self.settingsWidgets.append(self.pipelineReNameTextEdit)
    #
    self.inputDataLabel = Label(self, 'Input Data')
    self.settingsWidgets.append(self.inputDataLabel)
    self.inputDataList = ListWidget(self)
    self.inputDataList.setMaximumHeight(200)
    self.inputDataList.setAcceptDrops(True)

    self.inputDataList.addItem(self._getInputDataHeaderLabel())
    self.settingsWidgets.append(self.inputDataList)
    self.connect(self.inputDataList, QtCore.SIGNAL("dropped"), self._itemsDropped)

    #
    self.autoLabel = Label(self, 'Auto Run')
    self.settingsWidgets.append(self.autoLabel)
    self.autoCheckBox = CheckBox(self,)
    self.settingsWidgets.append(self.autoCheckBox)
    #
    self.savePipelineLabel = Label(self, 'Save in: directory path', tipText='Select path where to save your Pipeline file')
    self.settingsWidgets.append(self.savePipelineLabel)
    self.savePipelineLineEdit = LineEditButtonDialog(self, fileMode=QtGui.QFileDialog.Directory)
    self.settingsWidgets.append(self.savePipelineLineEdit)
    #

    #
    self.selectDisplayLabel = Label(self, 'Select output Display',
                                   tipText='Select display to show the pipeline output')
    self.settingsWidgets.append(self.selectDisplayLabel)
    self.selectDisplay = PulldownList(self, texts = ['Select'])
    if self.mainWindow is not None:
      self.selectDisplay.setData(texts = ['Select'] + [display.pid for display in self.mainWindow.spectrumDisplays])
    self.settingsWidgets.append(self.selectDisplay)

    #
    self.addBoxLabel = Label(self, 'Add Method On')
    self.settingsWidgets.append(self.addBoxLabel)
    self.addBoxPosition = RadioButtons(self,texts=['top', 'bottom'], selectedInd=0,direction='h')
    self.addBoxPosition.setMaximumHeight(20)
    self.settingsWidgets.append(self.addBoxPosition)
    #
    self.autoActiveLabel = Label(self, 'Auto active')
    self.settingsWidgets.append(self.autoActiveLabel)
    self.autoActiveCheckBox = CheckBox(self, )
    self.autoActiveCheckBox.setChecked(True)
    self.settingsWidgets.append(self.autoActiveCheckBox)

    #
    self.filter = Label(self, 'Methods filter')
    self.settingsWidgets.append(self.filter)
    self.filterButton = Button(self, icon = self.filterIcon, callback = self.filterMethodPopup)
    self.filterButton.setStyleSheet(transparentStyle)
    self.settingsWidgets.append(self.filterButton)

    #
    self.spacerLabel = Label(self, '')
    self.spacerLabel.setMaximumHeight(1)
    self.settingsWidgets.append(self.spacerLabel)
    self.applyCancelsettingButtons = ButtonList(self, texts=['Cancel', 'Apply'], callbacks=[self._cancelSettingsCallBack, self._applySettingsCallBack],
                                                direction='H', hAlign='c')
    self.settingsWidgets.append(self.applyCancelsettingButtons)

  def _itemsDropped(self):
    if len(self.inputDataList.getTexts())==1:
      if DropHereLabel in self.inputDataList.getTexts():
        self.inputDataList.clear()
        self.goButton.setEnabled(True)



  def _updateInputDataWidgets(self):
    'update the gui pipe widget if the input data has changed'
    if len(self.pipelineArea.findAll()[1]) > 0:
      guiPipes = self.pipelineArea.orderedBoxes(self.pipelineArea.topContainer)
      for guiPipe in guiPipes:
        guiPipe._updateWidgets()


  def settingsPipelineWidgets(self):
    if self.settingFrame.isHidden():
      self._showSettingWidget()
    else:
      self._cancelSettingsCallBack()

  def _updateSettingsParams(self):
    name = str(self.pipelineReNameTextEdit.text())
    rename = str(self.pipelineReNameTextEdit.text())
    savePath = str(self.savePipelineLineEdit.lineEdit.text())
    autoRun = self.autoCheckBox.get()
    addPosit = self.addBoxPosition.get()
    autoActive = self.autoActiveCheckBox.get()

    params = OrderedDict([
      ('name', name),
      ('rename', rename),
      ('savePath', savePath),
      ('autoRun', autoRun),
      ('addPosit', addPosit),
      ('autoActive', autoActive)
    ])
    self.pipelineSettingsParams = params


  def _setSettingsParams(self):
    widgets = [self.pipelineNameLabel.setText, self.pipelineReNameTextEdit.setText,
               self.savePipelineLineEdit.lineEdit.setText, self.autoCheckBox.setChecked, self.addBoxPosition.set]
    for widget, value in zip(widgets, self.pipelineSettingsParams.values()):
      widget(value)


  def _renamePipeline(self):
    self.pipelineName = self.lineEdit.text()

  def _applySettingsCallBack(self):
    self._displayStopButton()
    self._updateSettingsParams()
    self._setSettingsParams()
    self.setDataSelection()
    self._updateInputDataWidgets()
    # self._hideSettingWidget()

  def _cancelSettingsCallBack(self):
    self._setSettingsParams()
    # self._hideSettingWidget()

  def _hideSettingWidget(self):
    self.settingFrame.hide()
    for widget in self.settingsWidgets:
      widget.hide()

  def _showSettingWidget(self):
    self.settingFrame.show()
    for widget in self.settingsWidgets:
      widget.show()

  def _displayStopButton(self):
    if self.autoCheckBox.isChecked():
      self.goButton.buttons[0].show()
      self.goButton.buttons[1].show()
      self.goButton.buttons[2].hide()
    else:
      self.goButton.buttons[0].hide()
      self.goButton.buttons[1].hide()
      self.goButton.buttons[2].show()

  def filterMethodPopup(self):
    FilterMethods(parent=self).exec()

  def _addWidgetsToLayout(self, widgets, layout):
    count = int(len(widgets) / 2)
    self.positions = [[i + 1, j] for i in range(count) for j in range(2)]
    for position, widget in zip(self.positions, widgets):
      i, j = position
      layout.addWidget(widget, i, j)

  def setDataSelection(self):

    dataTexts = self.inputDataList.getTexts()
    self.inputData.clear()
    self.spectrumGroups.clear()
    if self.project is not None:
      if len(dataTexts) == 0:
        self.goButton.setEnabled(False)
        self.inputDataList.addItem(self._getInputDataHeaderLabel())
        return
      for text in dataTexts:
        obj  = self.project.getByPid(text)
        if object is not None:
          if isinstance(obj, Spectrum):
            self.inputData.update([obj])
          elif isinstance(obj, SpectrumGroup):
            self.inputData.update(obj.spectra)
            self.spectrumGroups.update([obj])
          else:
            print(obj, 'Not available.')

  def _updateInputData(self, data):
    ''
    dataTexts = self.inputDataList.getTexts()
    sp =  data['object']
    item = sp.pid
    self.inputDataList.clearSelection()
    self.inputDataList.select(item)
    self.inputDataList.removeItem()
    self.setDataSelection()



    # self.setDataSelection()

class FilterMethods(CcpnDialog):

  def __init__(self, parent=None, title='Preferred Pipes', **kw):
    CcpnDialog.__init__(self, parent, setLayout=False, windowTitle=title, **kw)
    # super(FilterMethods, self).__init__(parent)
    self.parent = parent
    self._setMainLayout()
    self._setWidgets()
    self._addWidgetsToLayout()


  def _setMainLayout(self):
    self.mainLayout = QtGui.QGridLayout()
    self.setLayout(self.mainLayout)
    self.setWindowTitle("Filter Methods")
    self.resize(250, 300)

  def _setWidgets(self):

    self.selectLabel = Label(self, 'Select All')
    self.selectAllCheckBox = CheckBox(self, )
    self._setSelectionScrollArea()
    self._addMethodCheckBoxes()
    self.applyCancelButtons = ButtonList(self, texts=['Cancel', 'Ok'],
                                                callbacks=[self.reject, self._okButtonCallBack],
                                                direction='H')
    self.selectAllCheckBox.stateChanged.connect(self._checkAllMethods)

  def _addMethodCheckBoxes(self):
    self.allMethodCheckBoxes = []
    for i, guiPipe in enumerate(self.parent.guiPipes):
        self.spectrumCheckBox = CheckBox(self.scrollAreaWidgetContents, text=str(guiPipe.pipeName), grid=(i + 1, 0))
        self.allMethodCheckBoxes.append(self.spectrumCheckBox)
    self.updateMethodCheckBoxes()
    self.updateSelectAllCheckBox()

  def updateMethodCheckBoxes(self):

    for guiPipe in self.parent.guiPipes:
      if guiPipe.preferredPipe:
        for cb in self.allMethodCheckBoxes:
          if cb.text() == guiPipe.pipeName:
            cb.setChecked(True)

  def updateSelectAllCheckBox(self):
    for cb in self.allMethodCheckBoxes:
      if not cb.isChecked():
        return
      else:
        self.selectAllCheckBox.setChecked(True)


  def _checkAllMethods(self, state):
    if len(self.allMethodCheckBoxes)>0:
      for cb in self.allMethodCheckBoxes:
        if state == QtCore.Qt.Checked:
          cb.setChecked(True)
        else:
          cb.setChecked(False)

  def _setPreferredPipe(self):
    pipes = []
    for cb in self.allMethodCheckBoxes:
      if cb.isChecked():
        guiPipe =  self.parent._getGuiPipeClass(cb.text())
        guiPipe.preferredPipe = True
        pipes.append(guiPipe)
      else:
        guiPipe = self.parent._getGuiPipeClass(cb.text())
        guiPipe.preferredPipe = False
        pipes.append(guiPipe)
    self.parent.guiPipes = pipes

  def _setSelectionScrollArea(self):
    self.scrollArea = ScrollArea(self)
    self.scrollArea.setWidgetResizable(True)
    self.scrollAreaWidgetContents = Frame(None, setLayout=True)
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)

  def _addWidgetsToLayout(self):
    self.mainLayout.addWidget(self.selectLabel, 0,0)
    self.mainLayout.addWidget(self.selectAllCheckBox, 0, 1)
    self.mainLayout.addWidget(self.scrollArea, 1, 0, 1, 2)
    self.mainLayout.addWidget(self.applyCancelButtons, 2, 1,)

  def _okButtonCallBack(self):
    self._setPreferredPipe()
    self.parent._setDataPipesPulldown()
    self.accept()





#################################### _________ RUN GUI TESTING ____________ ####################################


if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea
  from ccpn.pipes.examples import pipeExamples

  # analysis specific
  from ccpn.pipes import loadedPipes
  from  ccpn.AnalysisScreen.pipes import _loadPipes
  _loadPipes()


  app = TestApplication()
  win = QtGui.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None, )
  pipeline = GuiPipeline(mainWindow=None, pipes = loadedPipes)
  # pipeline = GuiPipeline(mainWindow=None, pipes=pipeExamples)
  moduleArea.addModule(pipeline)

  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % pipeline.moduleName)
  win.show()

  app.start()