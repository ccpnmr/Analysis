"""
This Module implements the main graphics window functionality
It works in concert with a wrapper object for storing/retrieving attibute values

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
__modifiedBy__ = "$modifiedBy: Geerten Vuister $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:44 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-04 09:51:15 +0100 (Tue, April 04, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

#import datetime
import json
import os
from functools import partial

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QKeySequence

from ccpn.util.Svg import Svg
from ccpn.ui.gui.lib.mouseEvents import PICK, SELECT
from ccpn.ui.gui.modules.GuiSpectrumDisplay import GuiSpectrumDisplay
from ccpn.ui.gui.modules.GuiStrip import GuiStrip
from ccpn.ui.gui.modules.GuiWindow import GuiWindow

from ccpn.ui.gui.modules.MacroEditor import MacroEditor
from ccpn.ui.gui.widgets import MessageDialog
from ccpn.ui.gui.widgets.Action import Action
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.IpythonConsole import IpythonConsole
from ccpn.ui.gui.widgets.Menu import Menu, MenuBar
from ccpn.ui.gui.widgets.SideBar import SideBar
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea
from ccpn.ui.gui.widgets.Splitter import Splitter
from ccpn.util.Common import uniquify
from ccpn.util import Logging
#from ccpn.util.Logging import getLogger
#from collections import OrderedDict


#TODO:WAYNE: incorporate most functionality from GuiWindow and
#TODO:TJ: functionality from FrameWork
# For readability there should be a class:
# _MainWindowShortCuts which (Only!) has the shortcut definitions and the callbacks to initiate them.
# The latter should all be private methods!
# For readability there should be a class:
# _MainWindowMenus which (Only!) has menu instantiations, the callbacks to initiate them, + relevant methods
# The latter should all be private methods!
#
# The docstring of GuiMainWindow should detail how this setup is


class GuiMainWindow(GuiWindow, QtWidgets.QMainWindow):

  def __init__(self, application=None):

    # super(GuiMainWindow, self).__init__(parent=None)
    GuiWindow.__init__(self, application)
    QtWidgets.QMainWindow.__init__(self)
    # Layout
    layout = self.layout()

    logger = Logging.getLogger()
    logger.debug('GuiMainWindow: layout: %s' % layout)

    if layout is not None:
      layout.setContentsMargins(0, 0, 0, 0)
      layout.setSpacing(0)

    self.setGeometry(200, 40, 1100, 900)

    # connect a close event, cleaning up things as needed
    self.closeEvent = self._closeEvent
    # self.connect(self, QtCore.PYQT_SIGNAL('triggered()'), self._closeEvent)
    # self.triggered.connect(self._closeEvent)    # ejb

    # GuiWindow.__init__(self, application)
    self.application = application

    # Module area
    self.moduleArea = CcpnModuleArea(mainWindow=self)
    logger.debug('GuiMainWindow.moduleArea: layout: %s' % self.moduleArea.layout) ## pyqtgraph object
    self.moduleArea.setGeometry(0, 0, 1000, 800)
    self.setCentralWidget(self.moduleArea)

    self.recordingMacro = False
    self._setupWindow()
    self._setupMenus()
    self._initProject()
    self._setShortcuts()
    self._setUserShortcuts(preferences=self.application.preferences, mainWindow=self)

    # do not need an unRegisterNotify because those removed when mainWindow / project destroyed
    self.application.current.registerNotify(self._resetRemoveStripAction, 'strips')

    self.feedbackPopup = None
    self.updatePopup = None

    # blank display opened later by the _initLayout if there is nothing to show otherwise
    # self.newBlankDisplay()
    self.pythonConsoleModule = None
    self.statusBar().showMessage('Ready')
    self.mouseMode = SELECT
    self.show()

  #   self.installEventFilter(self)
  #   # for action in self.actions():
  #   #   print (action)
  #   # QtWidgets.QShortcut.activated.connect(self._activatedkeySequence)
  #     # action.activatedAmbiguously.connect(self._ambiguouskeySequence)
  #
  # def eventFilter(self, obj, event):
  #   if event.type() == QtGui.QKeySequence.ExactMatch or event.type() == QtGui.QKeySequence.PartialMatch:
  #     try:
  #       print ('>>>key')
  #       self.statusBar().showMessage('key: %s' % str(event.key()))
  #       QtGui.QKeySequence.count = 0
  #
  #     except Exception as es:
  #       print (str(es))
  #
  #   return False

  def _activatedkeySequence(self, ev):
    key = ev.key()
    self.statusBar().showMessage('key: %s' % str(key))

  def _ambiguouskeySequence(self, ev):
    key = ev.key()
    self.statusBar().showMessage('key: %s' % str(key))

  def changeEvent(self, event):
    if event.type() == QtCore.QEvent.WindowStateChange:
      if self.windowState() & QtCore.Qt.WindowMinimized:

        # don't do anything on minimising
        pass

      elif event.oldState() & QtCore.Qt.WindowMinimized:

        # TODO:ED changeEvent: Normal/Maximised/FullScreen - call populate all modules
        pass

    event.ignore()

  def _initProject(self):
    """
    Puts relevant information from the project into the appropriate places in the main window.
    """
    #TODO:RASMUS: assure that isNew() and isTemporary() get added to Project; remove API calls
    isNew = self._apiWindow.root.isModified  # a bit of a hack this, but should be correct

    project = self._project
    path = project.path
    self.namespace['project'] = project
    self.namespace['runMacro'] = self.pythonConsole._runMacro

    msg = path + (' created' if isNew else ' opened')
    self.statusBar().showMessage(msg)
    msg2 = 'project = %sProject("%s")' % (('new' if isNew else 'open'), path)
    self.pythonConsole.writeConsoleCommand(msg2)

    self._fillRecentProjectsMenu()
    self.pythonConsole.setProject(project)
    self._updateWindowTitle()
    if hasattr(self.application.project._wrappedData.root, '_temporaryDirectory'):
      self.getMenuAction('Project->Archive').setEnabled(False)
    else:
      self.getMenuAction('Project->Archive').setEnabled(True)


  def _updateWindowTitle(self):
    """
    #CCPN INTERNAL - called in saveProject method of Framework
    """
    windowTitle = '{}, {}'.format(self.application.applicationName, self.application.applicationVersion)
    self.setWindowTitle(windowTitle)

  def getMenuAction(self, menuString, topMenuAction=None):
    from ccpn.framework.Translation import translator
    if topMenuAction is None:
      topMenuAction = self._menuBar
    splitMenuString = menuString.split('->')
    splitMenuString = [translator.translate(text) for text in splitMenuString]
    if len(splitMenuString) > 1:
      topMenuAction = self.getMenuAction('->'.join(splitMenuString[:-1]), topMenuAction)
    for a in topMenuAction.actions():
      # print ('>>>', menuString, a.text())
      if a.text() == splitMenuString[-1]:
        return a.menu() or a
    raise ValueError('Menu item not found.')

  def searchMenuAction(self, menuString, topMenuAction=None):
    from ccpn.framework.Translation import translator

    found = None
    if topMenuAction is None:
      topMenuAction = self._menuBar
    splitMenuString = menuString.split('->')
    splitMenuString = [translator.translate(text) for text in splitMenuString]
    if len(splitMenuString) > 1:
      topMenuAction = self.getMenuAction('->'.join(splitMenuString[:-1]), topMenuAction)
    for a in topMenuAction.actions():
      # print ('>>>', menuString, a.text())
      if a.text() == splitMenuString[-1]:
        found = a.menu() if a.menu() else a
        break
      else:
        if a.menu():
          found = self.searchMenuAction(menuString, topMenuAction=a.menu())
          if found:
            break
    return found

  def _setupWindow(self):
    """
    Sets up SideBar, python console and splitters to divide up main window properly.

    """
    self.namespace = {'application': self.application,
                      'current': self.application.current,
                      'preferences': self.application.preferences,
                      'redo': self.application.redo,
                      'undo': self.application.undo,

                      'ui': self.application.ui,
                      'mainWindow': self,
                      'project': self.application.project,
                      'loadProject': self.application.loadProject,
                      'newProject': self.application.newProject,
                     }

    self.pythonConsole = IpythonConsole(self)

    #TODO:LUCA: find out where the string is stored when you type '?' in the console; prepend this string
#     self.pythonConsole.ipythonWidget.__doc__ = \
# """
# CcpNmr IPython Console Area (shortcut 'PY' to toggle)
#
# Access to:
#
#     application, project, current, ui, mainWindow, preferences
#     redo(), undo(), loadProject(), newProject()
#
# """ + self.pythonConsole.ipythonWidget.__doc__

    self.sideBar = SideBar(parent=self)

    # A horizontal splitter runs vertical; ie. allows Widgets resize in a horizontal direction
    self._horizontalSplitter = Splitter(QtCore.Qt.Horizontal)
    # A vertical splitter runs horizontal; ie. allows Widgets resize in a vertical direction
    # self._verticalSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

    self._verticalTEMPSPLIT = Splitter(QtCore.Qt.Vertical)
    self._TESTFRAME = Frame(setLayout=False)
    self._tempLayout = QtWidgets.QVBoxLayout()
    self._TESTFRAME.setLayout(self._tempLayout)
    self._TESTFRAME.hide()

    # GWV: do not understand this order
    # self._verticalSplitter.addWidget(self.sideBar)
    # self._horizontalSplitter.addWidget(self._verticalSplitter)
    # self._horizontalSplitter.addWidget(self.moduleArea)
    # self.setCentralWidget(self._horizontalSplitter)

    # GWV: there is no need for the above as the moduleArea generates its splitter
    # when required

    self._horizontalSplitter.addWidget(self._verticalTEMPSPLIT)

    self._verticalTEMPSPLIT.addWidget(self.sideBar)
    self._verticalTEMPSPLIT.addWidget(self._TESTFRAME)

    self._horizontalSplitter.addWidget(self.moduleArea)
    self.setCentralWidget(self._horizontalSplitter)

  def _setupMenus(self):
    """
    Creates menu bar for main window and creates the appropriate menus according to the arguments
    passed at startup.

    This currently pulls info on what menus to create from Framework.  Once GUI and Project are
    separated, Framework should be able to call a method to set the menus.
    """

    self._menuBar = MenuBar(self)
    for m in self.application._menuSpec:
      self._createMenu(m)
    self.setMenuBar(self._menuBar)
    self._menuBar.setNativeMenuBar(False)

    self._fillRecentProjectsMenu()
    self._fillRecentMacrosMenu()
    #TODO:ED needs fixing
    self._fillPluginsMenu()     # ejb - nothing to show, and crash anyway
    self._attachModulesMenuAction()

  def _attachModulesMenuAction(self):
    # add a connect to call _fillModulesMenu when the menu item is about to show
    # so it is always uptodate
    modulesMenu = self.searchMenuAction('Show/hide Modules')
    # modulesMenu = self.getMenuAction('Show/hide Modules')
    modulesMenu.aboutToShow.connect(self._fillModulesMenu)

  def _createMenu(self, spec, targetMenu=None):
    menu = self._addMenu(spec[0], targetMenu)
    self._addMenuActions(menu, spec[1])

  def _addMenu(self, menuTitle, targetMenu=None):
    if targetMenu is None:
      targetMenu = self._menuBar
    if isinstance(targetMenu, MenuBar):
      menu = Menu(menuTitle, self)
      targetMenu.addMenu(menu)
    else:
      menu = targetMenu.addMenu(menuTitle)
    return menu

  def _addMenuActions(self, menu, actions):
    for action in actions:
      if len(action) == 0:
        menu.addSeparator()
      elif len(action) == 2:
        if callable(action[1]):
          menu.addAction(Action(self, action[0], callback=action[1]))
        else:
          self._createMenu(action, menu)
      elif len(action) == 3:
        kwDict = dict(action[2])
        for k,v in kwDict.items():
          if (k == 'shortcut') and v.startswith('⌃'):  # Unicode U+2303, NOT the carrot on your keyboard.
            kwDict[k] = QKeySequence('Ctrl+{}'.format(v[1:]))
        menuAction = Action(self, action[0], callback=action[1], **kwDict)
        menu.addAction(menuAction)

  def _queryCloseProject(self, title, phrase):

    apiProject = self._project._wrappedData.root
    if hasattr(apiProject, '_temporaryDirectory'):
      return True

    if apiProject.isProjectModified():
      ss = ' and any changes will be lost'
    else:
      ss = ''
    result = MessageDialog.showYesNo(title,
          'Do you really want to %s project (current project will be closed%s)?' % (phrase, ss))

    return result

  def loadProject(self, projectDir=None):
    """
    Opens a loadProject dialog box if project directory is not specified.
    Loads the selected project.
    """
    result = self._queryCloseProject(title='Open Project', phrase='open another')
    project = None
    if result:
      if projectDir is None:
        dialog = FileDialog(self, fileMode=FileDialog.Directory, text="Open Project",
                            acceptMode=FileDialog.AcceptOpen, preferences=self.application.preferences.general)
        projectDir = dialog.selectedFile()

      if projectDir:
        project = self.application.loadProject(projectDir)

        if project:
          project._mainWindow.show()
          QtWidgets.QApplication.setActiveWindow(project._mainWindow)
        else:
          MessageDialog.showError('loadProject', 'Error loading project:\n%s' % str(projectDir))
          Logging.getLogger().warning('Error loading project: %s' % str(projectDir))

    return project

  def _fillRecentProjectsMenu(self):
    """
    Populates recent projects menu with 10 most recently loaded projects
    specified in the preferences file.
    """
    recentFileLocations = self.application._getRecentFiles()
    recentFileMenu = self.getMenuAction('Project->Open Recent')
    recentFileMenu.clear()
    for recentFile in recentFileLocations:
      # action = Action(self, text=recentFile, translate=False,
      #                callback=partial(self.application.loadProject, path=recentFile))

      action = Action(self, text=recentFile, translate=False,
                     callback=partial(self.loadProject, projectDir=recentFile))
      recentFileMenu.addAction(action)
    recentFileMenu.addSeparator()
    recentFileMenu.addAction(Action(recentFileMenu, text='Clear',
                                    callback=self.application.clearRecentProjects))

  def _fillMacrosMenu(self):
    """
    Populates recent macros menu with last ten macros ran.
    """
    #TODO: make sure that running a macro adds it to the prefs and calls this function

    runMacrosMenu = self.getMenuAction('Macro->Run Recent')
    runMacrosMenu.clear()

    from ccpn.framework.PathsAndUrls import macroPath as ccpnMacroPath

    try:
      ccpnMacros = os.listdir(ccpnMacroPath)
      ccpnMacros = [f for f in ccpnMacros if
                    os.path.isfile(os.path.join(ccpnMacroPath, f))]
      ccpnMacros = [f for f in ccpnMacros if f.split('.')[-1] == 'py']
      ccpnMacros = [f for f in ccpnMacros if not f.startswith('.')]
      ccpnMacros = [f for f in ccpnMacros if not f.startswith('_')]
      ccpnMacros = sorted(ccpnMacros)

      for macro in ccpnMacros:
        action = Action(self, text=macro, translate=False,
                        callback=partial(self.runMacro,
                                         macroFile=os.path.join(ccpnMacroPath, macro)))
        runMacrosMenu.addAction(action)
      if len(ccpnMacros) > 0:
        runMacrosMenu.addSeparator()
    except FileNotFoundError:
      pass

    try:
      userMacroPath = os.path.expanduser(self.application.preferences.general.userMacroPath)
      userMacros = os.listdir(userMacroPath)
      userMacros = [f for f in userMacros if
                    os.path.isfile(os.path.join(userMacroPath, f))]
      userMacros = [f for f in userMacros if f.split('.')[-1] == 'py']
      userMacros = [f for f in userMacros if not f.startswith('.')]
      userMacros = [f for f in userMacros if not f.startswith('_')]
      userMacros = sorted(userMacros)

      for macro in userMacros:
          action = Action(self, text=macro, translate=False,
                          callback=partial(self.runMacro,
                                           macroFile=os.path.join(userMacroPath, macro)))
          runMacrosMenu.addAction(action)
      if len(userMacros) > 0:
        runMacrosMenu.addSeparator()
    except FileNotFoundError:
      pass

    runMacrosMenu.addAction(Action(runMacrosMenu, text='Refresh',
                                    callback=self._fillMacrosMenu))
    runMacrosMenu.addAction(Action(runMacrosMenu, text='Browse...',
                                    callback=self.runMacro))

  def _fillRecentMacrosMenu(self):
    """
    Populates recent macros menu with last ten macros ran.
    TODO: make sure that running a macro adds it to the prefs and calls this function
    """

    recentMacros = uniquify(self.application.preferences.recentMacros)
    recentMacrosMenu = self.getMenuAction('Macro->Run Recent')
    recentMacrosMenu.clear()
    for recentMacro in recentMacros:
      action = Action(self, text=recentMacro, translate=False,
                      callback=partial(self.runMacro, macroFile=recentMacro))
      recentMacrosMenu.addAction(action)
    recentMacrosMenu.addSeparator()
    recentMacrosMenu.addAction(Action(recentMacrosMenu, text='Clear',
                                      callback=self.application.clearRecentMacros))

  def _addPluginSubMenu(self, Plugin):
    targetMenu = pluginsMenu = self.getMenuAction('Plugins')
    if '...' in Plugin.PLUGINNAME:
      package, name = Plugin.PLUGINNAME.split('...')
      try:
        targetMenu = self.getMenuAction(package, topMenuAction=pluginsMenu)
      except ValueError:
        targetMenu = self._addMenu(package, targetMenu=pluginsMenu)
    else:
      name = Plugin.PLUGINNAME
    action = Action(self, text=name, translate=False,
                    callback=partial(self.startPlugin, Plugin=Plugin))
    targetMenu.addAction(action)

  def _fillModulesMenu(self):
    modulesMenu = self.searchMenuAction('Show/hide Modules')
    modulesMenu.clear()

    moduleSize = self.sideBar.size()
    visible = moduleSize.width() != 0 and moduleSize.height() != 0
    modulesMenu.addAction(Action(modulesMenu, text='Sidebar'
                                 , checkable=True, checked=visible
                                 , callback=partial(self._showSideBarModule, self.sideBar, self)))

    for module in self.moduleArea.ccpnModules:
      moduleSize = module.size()
      visible = moduleSize.width() != 0 and moduleSize.height() != 0

      modulesMenu.addAction(Action(modulesMenu, text=module.name()
                                   , checkable=True, checked=visible
                                   , callback=partial(self._showModule, module, self)))

  def _showModule(self, module, modulesMenu):
    try:
      menuItem = self.searchMenuAction(module.name())
      if menuItem:
        if module.size().height() != 0 and module.size().width() != 0:   #menuItem.isChecked():    # opposite as it has toggled
          module.setStretch(0, 0)
        else:
          module.setStretch(1, 1)
    except Exception as es:
      Logging.getLogger().warning('Error expanding module: %s', module.name())

  def _showSideBarModule(self, module, modulesMenu):
    try:
      if module.size().height() != 0 and module.size().width() != 0:   #menuItem.isChecked():    # opposite as it has toggled
        module.hide()
      else:
        module.show()
    except Exception as es:
      Logging.getLogger().warning('Error expanding module: sideBar')

  def keyPressEvent(self, e):

    if e.key() == QtCore.Qt.Key_Escape:
      # Reset Mouse Mode
      mode = self.mouseMode
      if mode != SELECT:
        self.setMouseMode(SELECT)

  def _fillPluginsMenu(self):
    from ccpn.framework.lib.ExtensionLoader import getPlugins
    from ccpn.framework.PathsAndUrls import pluginPath

    from ccpn.plugins import loadedPlugins

    pluginsMenu = self.getMenuAction('Plugins')
    pluginsMenu.clear()

    # Plugins = getPlugins(pluginPath)        # ejb - original
    # Plugins = sorted(Plugins, key=lambda p:p.PLUGINNAME)
    # for Plugin in Plugins:
    #   self._addPluginSubMenu(Plugin)
    #
    # pluginsMenu.addSeparator()
    # Plugins = getPlugins(self.application.preferences.general.userPluginPath)
    # Plugins = sorted(Plugins, key=lambda p:p.PLUGINNAME)
    # for Plugin in Plugins:
    #   self._addPluginSubMenu(Plugin)

    # Plugins = getPlugins(pluginPath)                      # already a set
    # Plugins = sorted(Plugins, key=lambda p:p.PLUGINNAME)
    # # for Plugin in Plugins:
    # #   self._addPluginSubMenu(Plugin)
    #
    # Plugins2 = getPlugins(self.application.preferences.general.userPluginPath)
    # Plugins2 = sorted(Plugins2, key=lambda p:p.PLUGINNAME)
    #
    # Plugins += Plugins2

    for Plugin in loadedPlugins:
      self._addPluginSubMenu(Plugin)

    pluginsMenu.addSeparator()
    pluginsMenu.addAction(Action(pluginsMenu, text='Reload',
                                      callback=self._fillPluginsMenu))

  def startPlugin(self, Plugin):
    plugin = Plugin(application=self.application)
    self.application.plugins.append(plugin)
    if plugin.guiModule is None:
      if not plugin.UiPlugin:
        plugin.run()
        return
      else:
        from ccpn.ui.gui.modules.PluginModule import AutoGeneratedPluginModule
        pluginModule = AutoGeneratedPluginModule(mainWindow=self
                                                , plugin=plugin
                                                , application=self.application)   # ejb

    else:
      pluginModule = plugin.guiModule(name=plugin.PLUGINNAME, parent=self,
                                      plugin=plugin, application=self.application
                                      , mainWindow=self)
    plugin.ui = pluginModule
    if not pluginModule.aborted:
      self.application.ui.pluginModules.append(pluginModule)
      self.moduleArea.addModule(pluginModule)
    # TODO: open as pop-out, not as part of MainWindow
    # self.moduleArea.moveModule(pluginModule, position='above', neighbor=None)

  def _updateRestoreArchiveMenu(self):

    action = self.getMenuAction('Project->Restore From Archive...')
    action.setEnabled(bool(self.application._archivePaths()))

  def undo(self):
    self._project._undo.undo()

  def redo(self):
    self._project._undo.redo()

  def saveLogFile(self):
    pass

  def clearLogFile(self):
    pass

  def displayProjectSummary(self):
    info = MessageDialog.showInfo('Not implemented yet',
          'This function has not been implemented in the current version')

  def _closeEvent(self, event=None):
    """
    Saves application preferences. Displays message box asking user to save project or not.
    Closes Application.
    """
    from ccpn.framework.PathsAndUrls import userPreferencesPath
    #prefPath = os.path.expanduser("~/.ccpn/v3settings.json")
    #TODO:TJ move all of the saving of preferences to FrameWork
    directory = os.path.dirname(userPreferencesPath)
    if not os.path.exists(directory):
      try:
        os.makedirs(directory)
      except Exception as e:
        self._project._logger.warning('Preferences not saved: %s' % (directory, e))
        return

    prefFile = open(userPreferencesPath, 'w+')
    json.dump(self.application.preferences, prefFile, sort_keys=True, indent=4, separators=(',', ': '))
    prefFile.close()

    # set the active window to mainWindow so that the quit popup centres correctly.
    QtWidgets.QApplication.setActiveWindow(self)
    reply = MessageDialog.showMulti("Quit Program", "Do you want to save changes before quitting?",
                                     ['Save and Quit', 'Quit without Saving', 'Cancel'],
                                   )
    if reply == 'Save and Quit':
      if event:
        event.accept()
      prefFile = open(userPreferencesPath, 'w+')
      json.dump(self.application.preferences, prefFile, sort_keys=True, indent=4, separators=(',', ': '))
      prefFile.close()

      success = self.application.saveProject()
      if success is True:
        # Close and clean up project
        self.application._closeProject()      # close if saved
        QtWidgets.QApplication.quit()
      else:
        if event:                             # ejb - don't close the project
          event.ignore()

    elif reply == 'Quit without Saving':
      if event:
        event.accept()
      prefFile = open(userPreferencesPath, 'w+')
      json.dump(self.application.preferences, prefFile, sort_keys=True, indent=4, separators=(',', ': '))
      prefFile.close()

      self.application._closeProject()
      QtWidgets.QApplication.quit()
    else:
      if event:
        event.ignore()

  def newMacroFromLog(self):
    """
    Displays macro editor with contents of the log.
    """
    editor = MacroEditor(self.moduleArea, self, "Macro Editor")
    l = open(self.project._logger.logPath, 'r').readlines()
    text = ''.join([line.strip().split(':', 6)[-1]+'\n' for line in l])
    editor.textBox.setText(text)

  #TODO:TJ the below is in Framework (slightly different implementation) so presumably does not belong here???
  #Framework owns the command, this part juts get the file to run
  def runMacro(self, macroFile:str=None):
    """
    Runs a macro if a macro is specified, or opens a dialog box for selection of a macro file and then
    runs the selected macro.
    """
    if macroFile is None:
      dialog = FileDialog(self, fileMode=FileDialog.ExistingFile, text="Run Macro",
                          acceptMode=FileDialog.AcceptOpen, preferences=self.application.preferences.general)
      if os.path.exists(self.application.preferences.general.userMacroPath):
        dialog.setDirectory(self.application.preferences.general.userMacroPath)
      macroFile = dialog.selectedFile()
      if not macroFile:
        return

    if os.path.isfile(macroFile):
      self.application.preferences.recentMacros.append(macroFile)
      self._fillRecentMacrosMenu()
      self.pythonConsole._runMacro(macroFile)

  def _resetRemoveStripAction(self, strips):
    for spectrumDisplay in self.spectrumDisplays:
      pass  # GWV: poor solution spectrumDisplay._resetRemoveStripAction()

  def printToFile(self, spectrumDisplayOrStrip=None, path=None, width=800, height=800):
    #TODO:LUCA: Docstring needed

    try:
      saveName = spectrumDisplayOrStrip.title+'.svg'
    except:
      saveName=''

    current = self.application.current
    if not spectrumDisplayOrStrip:
      spectrumDisplayOrStrip = current.spectrumDisplay
    if not spectrumDisplayOrStrip and current.strip:
      spectrumDisplayOrStrip = current.strip.spectrumDisplay
    if not spectrumDisplayOrStrip and self.spectrumDisplays:
      spectrumDisplayOrStrip = self.spectrumDisplays[0]
    if spectrumDisplayOrStrip:
      if isinstance(spectrumDisplayOrStrip, GuiSpectrumDisplay):
        strips = spectrumDisplayOrStrip.strips
        if not strips:
          return

      if not path:
        dialog = FileDialog(parent=self
                            , directory=saveName, fileMode=FileDialog.AnyFile, text='Print to File',
                            acceptMode=FileDialog.AcceptSave, preferences=self.application.preferences.general,
                            filter='SVG (*.svg)')
        path = dialog.selectedFile()
        if not path:
          return
        if not path.endswith(".svg"):
          path = path+".svg"

      xCount = yCount = 1
      if isinstance(spectrumDisplayOrStrip, GuiSpectrumDisplay):
        if spectrumDisplayOrStrip.stripDirection == 'X':
          yCount = len(strips)
        else:
          xCount = len(strips)

      with Svg(path, xCount=xCount, yCount=yCount, width=width, height=height) as printer:

        # box
        printer.writeLine(0, 0, width, 0)
        printer.writeLine(width, 0, width, height)
        printer.writeLine(width, height, 0, height)
        printer.writeLine(0, height, 0, 0)

        xNumber = yNumber = 0
        if isinstance(spectrumDisplayOrStrip, GuiSpectrumDisplay):
          for n, strip in enumerate(strips):
            if spectrumDisplayOrStrip.stripDirection == 'X':
              xOutputRegion = (0, width)
              yOutputRegion = (n * height / yCount, (n + 1) * height / yCount)
              yNumber = n
              if n > 0:
                # strip separator
                printer.writeLine(0, yOutputRegion[0], width, yOutputRegion[0])
            else:
              xOutputRegion = (n * width / xCount, (n + 1) * width / xCount)
              yOutputRegion = (0, height)
              xNumber = n
              if n > 0:
                # strip separator
                printer.writeLine(xOutputRegion[0], 0, xOutputRegion[0], height)
            printer.startRegion(xOutputRegion, yOutputRegion, xNumber, yNumber)
            strip._printToFile(printer)
        else:
          xOutputRegion = (0, width)
          yOutputRegion = (0, height)
          printer.startRegion(xOutputRegion, yOutputRegion)
          spectrumDisplayOrStrip._printToFile(printer)

  _mouseMovedSignal = QtCore.pyqtSignal(dict)

  def _mousePositionMoved(self, strip:GuiStrip, position:QtCore.QPointF):
    """ CCPN INTERNAL: called from ViewBox
    This is called when the mouse cursor position has changed in some strip
    :param strip: The strip the mouse cursor is hovering over
    :param position: The cursor position in "natural" (e.g. ppm) units
    :return: None
    """
    axisCodes = strip.axisCodes
    orderedAxes = strip.orderedAxes

    # positionDict
    #   strip --> strip
    #   axisCode --> position (for each axisCode in strip)
    # for the first two axes the position is provided by the cursor
    # for the z axes the position is provided as the center of the axis region (i.e. the position)

    mouseMovedDict = dict(strip=strip)
    try:
      for n, axisCode in enumerate(axisCodes):
        if n == 0:
          xPos = pos = position.x()
        elif n == 1:
          yPos = pos = position.y()
        else:
          pos = orderedAxes[n].position
        mouseMovedDict[axisCode] = pos

      self.application.current.cursorPosition = (xPos, yPos) # TODO: is there a better place for this to be set?

      self._mouseMovedSignal.emit(mouseMovedDict)
    except Exception as es:
      Logging.warning(str(es))
