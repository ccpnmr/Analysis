"""
This Module is used to save and restore the gui state of the program.
There are several Try except due to the fragility of Pyqtgraph layouts (containairs) and nested hierarchy of docks/areas etc..
The state is saved in a Json file. The default file is autogenerated when firing the program. It gets auto
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:29 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b5 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import ntpath
import glob
from ccpn.util.AttrDict import AttrDict
from collections import OrderedDict as od
from ccpn.util.Logging import getLogger
from ccpn.ui.gui.lib.GuiSpectrumDisplay import GuiSpectrumDisplay
import json
import sys, os
from ccpn.util import Path


StateDirName = 'state'
DefaultLayoutFileName = 'Layout.json'
Warning = "warning"
WarningMessage = "Warning. Any changes in this file will be overwritten when saving a new layout."
General = "general"
ApplicationName = "applicationName"  # type: str
ApplicationVersion = "applicationVersion"
LayoutVersionName = "LayoutVersion"
LayoutVersion = 'b.6'
SpectrumDisplays = "SpectrumDisplays"
GuiModules = "guiModules"
FileNames = 'fileNames'
LayoutState = "layoutState"
TitleText = 'LayoutFile'
Title = "Title"

DefaultLayoutFile = {
    Title      : TitleText,
    Warning    : WarningMessage,
    General    : {
        ApplicationName   : "",
        ApplicationVersion: "",
        LayoutVersionName:"",
        },
    SpectrumDisplays: [],
    GuiModules : [],
    FileNames  : [],
    LayoutState: {}
    }

METADATA = '_metadata'
MODULES = 'modules'


def _createLayoutFile(application):
    try:
        path = application.statePath + '/' + DefaultLayoutFileName

        if General in DefaultLayoutFile:
            if ApplicationName in DefaultLayoutFile[General]:
                DefaultLayoutFile[General][ApplicationName] = application.applicationName
            if ApplicationVersion in DefaultLayoutFile[General]:
                DefaultLayoutFile[General][ApplicationVersion] = application.applicationVersion
            if LayoutVersionName in DefaultLayoutFile[General]:
                DefaultLayoutFile[General][LayoutVersionName] = LayoutVersion

        with open(path, "w") as file:
            json.dump(DefaultLayoutFile, file, sort_keys=False, indent=4, separators=(',', ': '))

    except Exception as e:
        getLogger().debug('Impossible to create a layout File.', e)


def getLayoutFile(application):
    path = os.path.join(application.statePath, DefaultLayoutFileName)
    if not os.path.exists(path):
        _createLayoutFile(application)
    return path


def _updateGeneral(mainWindow, layout):
    application = mainWindow.application
    applicationName = application.applicationName
    applicationVersion = application.applicationVersion
    if General in layout:
        general = layout.get(General)  #getattr(layout, General)
        if ApplicationName in general:
            # setattr(general, ApplicationName, applicationName)
            general[ApplicationName] = applicationName
        if ApplicationVersion in general:
            # setattr(general, ApplicationVersion, applicationVersion)
            general[ApplicationVersion] = applicationVersion


def _updateFileNames(mainWindow, layout):
    """
    :param mainWindow:
    :param layout:
    :return: #updates the fileNames needed for importing the module. list of file name from the full path
    """
    guiModules = mainWindow.moduleArea.ccpnModules
    paths = []
    names = set()
    for guiModule in guiModules:
        if not isinstance(guiModule, GuiSpectrumDisplay):  #Don't Save spectrum Displays
            pyModule = sys.modules[guiModule.__module__]
            if pyModule:
                file = pyModule.__file__
                if file:
                    path = os.path.abspath(file)
                    basename = ntpath.basename(path)
                    basenameList = os.path.splitext(basename)
                    if len(basenameList) > 0:
                        names.add(basenameList[0])

    if len(names) > 0:
        if FileNames in layout:
            # setattr(layout, FileNames, list(names))
            layout[FileNames] = list(names)


def _updateGuiModules(mainWindow, layout):
    """

    :param mainWindow:
    :param layout:
    :return: #updates classNameModuleNameTupleList on layout with list of tuples [(className, ModuleName), (className, ModuleName)]
    list of tuples because a multiple modules of the same class type can exist. E.g. two peakListTable modules!
    """
    guiModules = mainWindow.moduleArea.ccpnModules

    classNames_ModuleNames = []  #list of tuples [(className, ModuleName), (className, ModuleName)]
    for module in guiModules:
        # if not isinstance(module, GuiSpectrumDisplay): # Displays are not stored here but in the DataModel
        classNames_ModuleNames.append((module.name(), module.className))

    if GuiModules in layout:
        # if ClassNameModuleName in layout.guiModules:
        #     setattr(layout.guiModules, ClassNameModuleName, classNames_ModuleNames )
        layout[GuiModules] = classNames_ModuleNames
        # setattr(layout, GuiModules, classNames_ModuleNames)


def _updateLayoutState(mainWindow, layout):
    if LayoutState in layout:
        # setattr(layout, LayoutState, mainWindow.moduleArea.saveState())
        layout[LayoutState] = mainWindow.moduleArea.saveState()

def _updateSpectrumDisplays(mainWindow, layout):
    sds = _getSpectrumDisplaysState(mainWindow.project.spectrumDisplays)
    layout[SpectrumDisplays] = sds


def _updateWarning(mainWindow, layout):
    if Warning in layout:
        # setattr(layout, Warning, WarningMessage)
        layout[Warning] = WarningMessage


def _checkLayoutFormat(mainWindow, layout):
    if not isinstance(layout, dict):
        # assume that this is a 'future' format and remove metadata
        getLogger().warning('Layout is not the correct format, converting to a dict')

        newLayout = DefaultLayoutFile.copy()
        if General in newLayout:
            if ApplicationName in newLayout[General]:
                newLayout[General][ApplicationName] = mainWindow.application.applicationName
            if ApplicationVersion in newLayout[General]:
                newLayout[General][ApplicationVersion] = mainWindow.application.applicationVersion

        mainWindow.application.layout = newLayout

    return mainWindow.application.layout


def updateSavedLayout(mainWindow):
    """
    Updates the application.layout Dict
    :param mainWindow: needed to get application
    :return: an up to date layout dictionary with the current state of GuiModules
    """
    layout = mainWindow.application.layout
    layout = _checkLayoutFormat(mainWindow, layout)

    _updateGeneral(mainWindow, layout)
    _updateSpectrumDisplays(mainWindow, layout)
    _updateFileNames(mainWindow, layout)
    _updateGuiModules(mainWindow, layout)
    _updateLayoutState(mainWindow, layout)
    _updateWarning(mainWindow, layout)


def saveLayoutToJson(mainWindow, jsonFilePath=None):
    """

    :param application:
    :param jsonFilePath: User defined file path where to save the layout. Default is in .ccpn/layout/v3Layout.json
    :return: None
    """
    try:
        updateSavedLayout(mainWindow)
        layout = mainWindow.application.layout
        if not jsonFilePath:
            jsonFilePath = getLayoutFile(mainWindow.application)

        with open(jsonFilePath, "w") as file:
            json.dump(layout, file, sort_keys=False, indent=4, separators=(',', ': '))

    except Exception as e:
        getLogger().debug('Impossible to save Layout %s' % e)


def _ccpnModulesImporter(path, neededModules):
    """
    :param path: fullPath of the directory where are located the CcpnModules files
    :return: list of CcpnModule classes
    """
    _ccpnModules = []
    import pkgutil as _pkgutil
    import inspect as _inspect
    from ccpn.ui.gui.modules.CcpnModule import CcpnModule

    for loader, name, isPpkg in _pkgutil.walk_packages(path):
        # print ('>>>loading', name)
        # print(neededModules, name)
        if name in neededModules:

            try:
                findModule = loader.find_module(name)
                # for neededModule in neededModules:
                module = findModule.load_module(name)
                # print ('>>>found')
                for i, obj in _inspect.getmembers(module):
                    if _inspect.isclass(obj):
                        if issubclass(obj, CcpnModule):
                            if hasattr(obj, 'className'):
                                # print ('>>>     end')
                                _ccpnModules.append(obj)
                                # print ('>>>     append')
            except Exception as es:
                getLogger().debug('Error loading module: %s' % str(es))
    return _ccpnModules


def _openCcpnModule(mainWindow, ccpnModules, className, moduleName=None):
    for ccpnModule in ccpnModules:
        if ccpnModule is not None:
            if ccpnModule.className == className:
                try:
                    newCcpnModule = ccpnModule(mainWindow=mainWindow, name=moduleName)
                    newCcpnModule._restored = True
                    # newCcpnModule.rename(newCcpnModule.name().split('.')[0])

                    mainWindow.moduleArea.addModule(newCcpnModule)

                except Exception as e:
                    getLogger().debug("Layout restore failed: %s" % e)


def _getApplicationSpecificModules(mainWindow, applicationName):
    '''init imports. try except as some applications may not be distribuited '''
    modules = []
    from ccpn.framework.Framework import AnalysisAssign, AnalysisMetabolomics, AnalysisStructure, AnalysisScreen

    if applicationName == AnalysisScreen:
        try:
            from ccpn.AnalysisScreen.gui import modules as aS

            modules.append(aS)
        except Exception as e:
            getLogger().debug("Import Error for AnalysisScreen, %s" % e)

    if applicationName == AnalysisAssign:
        try:
            from ccpn.AnalysisAssign import modules as aA

            modules.append(aA)
        except Exception as e:
            getLogger().debug("Import Error for AnalysisAssign, %s" % e)

    if applicationName == AnalysisMetabolomics:
        try:
            from ccpn.AnalysisMetabolomics.ui.gui import modules as aM

            modules.append(aM)
        except Exception as e:
            getLogger().debug("Import Error for AnalysisMetabolomics, %s" % e)

    if applicationName == AnalysisStructure:
        try:
            from ccpn.AnalysisStructure import modules as aS

            modules.append(aS)
        except Exception as e:
            getLogger().debug("Import Error for AnalysisStructure, %s" % e)

    return modules


def _getAvailableModules(mainWindow, layout, neededModules):
    from ccpn.ui.gui import modules as gM

    if General in layout:
        if ApplicationName in layout.general:

            applicationName = layout.general.get(ApplicationName)  # getattr(layout.general, ApplicationName)
            modules = []
            if applicationName != mainWindow.application.applicationName:
                getLogger().debug('The layout was saved in a different application. Some of the modules might not be loaded.'
                                  'If this happens,  start a new project with %s' % applicationName)
            else:
                modules = _getApplicationSpecificModules(mainWindow, applicationName)
            modules.append(gM)
            paths = [item.__path__ for item in modules]

            ccpnModules = [ccpnModule for path in paths for ccpnModule in _ccpnModulesImporter(path, neededModules)]
            return ccpnModules


def _traverse(o, tree_types=(list, tuple)):
    '''used to flat the state in a long list '''
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in _traverse(value, tree_types):
                yield subvalue
    else:
        yield o


def _getModuleNamesFromState(layoutState):
    ''' '''
    names = []
    if not layoutState:
        return names

    lls = []
    if 'main' in layoutState:
        mains = layoutState['main']
        lls += list(_traverse(mains))
    if 'float' in layoutState:
        flts = layoutState['float']
        lls += list(_traverse(flts))
        for i in list(_traverse(flts)):
            if isinstance(i, dict):
                if 'main' in i:
                    lls += list(_traverse(i['main']))

    excludingList = ['vertical', 'dock', 'horizontal', 'tab', 'main', 'sizes', 'float']
    names = [i for i in lls if i not in excludingList if isinstance(i, str)]

    return names



def _openSpectrumDisplays(mainWindow, spectrumDisplaysState):
    """

    """
    project = mainWindow.project
    for dd in spectrumDisplaysState:
        spectrumDisplayKeys = ["displayAxisCodes","axisOrder", "title", "positions", "widths", "units", "stripDirection","is1D"]
        fd = {i: dd.get(i) for i in spectrumDisplayKeys}
        spectraPids = dd.get("spectra")
        spectra = [project.getByPid(p) for p in spectraPids if project.getByPid(p)]
        stripsZoomStates = dd.get("stripsZoomStates")
        if len(spectra)>0:
            sd = mainWindow.createSpectrumDisplay(spectra[0], **fd)
            for sp in spectra[1:]:
                sd.displaySpectrum(sp)
            if len(stripsZoomStates)>0:
                if len(sd.strips)>0:
                    sd.strips[0].restoreZoomFromState(stripsZoomStates[0])
                    for stripState in stripsZoomStates[1:]:
                        newStrip = sd.addStrip()
                        newStrip.restoreZoomFromState(stripState)
        else:
            project.newSpectrumDisplay(axisCodes=fd.get('displayAxisCodes'), stripDirection = fd.get('stripDirection'))

def restoreLayout(mainWindow, layout, restoreSpectrumDisplay=False):
    ## import all the ccpnModules classes specific for the application.
    # mainWindow.moduleArea._closeAll()

    layout = _checkLayoutFormat(mainWindow, layout)
    if restoreSpectrumDisplay:
        if SpectrumDisplays in layout:
            _openSpectrumDisplays(mainWindow, layout[SpectrumDisplays])


    if FileNames in layout:
        neededModules = layout.get(FileNames)  # getattr(layout, FileNames)
        if len(neededModules) > 0:
            if GuiModules in layout:
                # if ClassNameModuleName in layout.guiModules:
                #   classNameGuiModuleNameList = getattr(layout.guiModules, ClassNameModuleName)

                classNameGuiModuleNameList = layout.get(GuiModules)  # getattr(layout, GuiModules)
                # Checks if  modules  are present in the layout file. If not stops it
                if not list(_traverse(classNameGuiModuleNameList)):
                    return

                try:
                    ccpnModules = _getAvailableModules(mainWindow, layout, neededModules)
                    for classNameGuiModuleName in classNameGuiModuleNameList:
                        if len(classNameGuiModuleName) == 2:
                            guiModuleName, className = classNameGuiModuleName

                            # move the 'skip' to here, instead of in the saveState
                            if className in ['SpectrumDisplay']:
                                continue

                            neededModules.append(className)
                            _openCcpnModule(mainWindow, ccpnModules, className, moduleName=guiModuleName)

                except Exception as e:
                    getLogger().debug2("Failed to restore Layout")

    if LayoutState in layout:
        # Very important step:
        # Checks if the all the modules opened are present in the layout state. If not, will not restore the geometries
        state = layout.get(LayoutState)  # getattr(layout, LayoutState)

        if not state:
            return
        namesFromState = _getModuleNamesFromState(state)
        openedModulesName = [i.name() for i in mainWindow.moduleArea.ccpnModules]
        compare = list(set(namesFromState) & set(openedModulesName))

        if len(openedModulesName) > 0:
            if len(compare) == len(openedModulesName):
                try:
                    mainWindow.moduleArea.restoreState(state)
                except Exception as e:
                    getLogger().debug2("Layout error: %s" % e)
            else:
                getLogger().debug2("Layout error: Some of the modules are missing. Geometries could not be restored")

def _getSpectrumDisplaysState(spectrumDisplays):
    """
    :return: list of dict with serialisable attributes needed to restore the SpDisplay status
    AbstractWrapperClasses will be converted as pid, EG spectrumDisplay.spectra
    """
    ll = []
    for spectrumDisplay in spectrumDisplays:
        dd = spectrumDisplay.getAsDict()
        stripDirection = dd.get("stripArrangement")
        axisCodes = dd.get("axisCodes")
        spectrumDisplayKeys = ["longPid","axisOrder", "title", "positions", "widths", "units", "is1D"]
        fd = {i: dd.get(i) for i in spectrumDisplayKeys}
        fd.update({'stripDirection': stripDirection})
        fd.update({'displayAxisCodes': axisCodes})
        fd.update({'spectra':[sp.pid for sp in spectrumDisplay._getSpectra()]})
        # strips informations
        stripsZoomStates = [strip.zoomState for strip in spectrumDisplay.strips]
        fd.update({"stripsZoomStates": stripsZoomStates})
        ll.append(fd)
    return ll

def _getFileNameFromPath(path, extToSplit= 'json'):
    file = ntpath.basename(path)
    name = file.split("."+extToSplit)[0]
    return name

def _getPredifinedLayouts(dirPath):
    # path has to finish with /
    sp = os.path.join(dirPath, '*.json')
    layoutsFiles = glob.glob(sp)
    return layoutsFiles

def _dictLayoutsNamePath(paths):
    dd = od()
    for path in paths:
        name = _getFileNameFromPath(path)
        dd[name] = path
    return dd

def isLayoutFile(filePath):
    with open(filePath) as fp:
        layout = json.load(fp, object_hook=AttrDict)
        if layout.get(LayoutState):
            return True
    return False

