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
from PyQt4 import QtGui, QtCore

from ccpn.lib import Util as ccpnUtil
from ccpncore.gui.Dock import CcpnDock
from application.core.Base import Base as GuiBase
from ccpncore.gui.MessageDialog import showWarning
# from ccpncore.lib.Io import Formats as ioFormats

class DropBase(GuiBase):

  def __init__(self, appBase, *args, **kw):
  # def __init__(self, appBase, dropCallback, *args, **kw):

    GuiBase.__init__(self, appBase, *args, **kw)
    # self.dropCallback = dropCallback

    # This should NOT be there - use self._appBase (set in GuiBase)
    #self.appBase = appBase

  def dragEnterEvent(self, event):
    event.accept()

  def dropEvent(self, event):
    """Catch dropEvent and dispatch to processing"""


    from application.core.util import Qt as qtUtil

    event.accept()

    data, dataType  = qtUtil.interpretEvent(event)
    if data and dataType:
      self.processDropData(data, dataType, event)

  # def dropEvent(self, event):
  #   """NBNB FIXME, must be commented out"""
  #   event.accept()
  #   if isinstance(self.parent, QtGui.QGraphicsScene):
  #     event.ignore()
  #     return
  #
  #   if event.mimeData().urls():
  #     filePaths = [url.path() for url in event.mimeData().urls()]
  #
  #     if filePaths:
  #       for filePath in filePaths:
  #         try:
  #           if isFastaFormat(filePath):
  #             sequences = parseFastaFile(filePaths[0])
  #             for sequence in sequences:
  #               self._appBase.project.makeSimpleChain(sequence=sequence[1], compoundName=sequence[0],
  #                                                     molType='protein')
  #
  #         except:
  #           try:
  #             if filePath.endswith('.spc.par'):
  #               # NBNB TBD HACK: Should be handle properly
  #               filePath = filePath[:-4]
  #             spectrum = self._appBase.project.loadSpectrum(filePath)
  #             if spectrum is not None:
  #               self._appBase.mainWindow.leftWidget.addSpectrum(spectrum)
  #               self.dropCallback(spectrum)
  #           except:
  #               pass
  #
  #   if event.mimeData().hasFormat('application/x-strip'):
  #     data = event.mimeData().data('application/x-strip')
  #     pidData = str(data.data(),encoding='utf-8')
  #     pidData = [ch for ch in pidData if 32 < ord(ch) < 127]  # strip out junk
  #     actualPid = ''.join(pidData)
  #     wrapperObject = self.getByPid(actualPid)
  #     self.dropCallback(wrapperObject)
  #   else:
  #     data = event.mimeData().data('application/x-qabstractitemmodeldatalist')
  #     pidData = str(data.data(),encoding='utf-8')
  #     pidData = [ch for ch in pidData if 32 < ord(ch) < 127]  # strip out junk
  #     actualPid = ''.join(pidData)
  #     wrapperObject = self.getObject(actualPid)
  #     self.dropCallback(wrapperObject)


  def processDropData(self, data, dataType='pids', event=None):
    """ Process dropped-in data
    Separate function so it can be called from command line as well.
    """

    project = self._appBase.project

    if dataType == 'text':
      # data is a text string
      if hasattr(self, 'processText'):
        self.processText(data)

    else:
      pids = []
      if dataType == 'pids':
        pids = data

      elif dataType == 'urls':
        # data is list-of-urls
        # Load Urls one by one with normal loaders
        for url in data:
          loaded = project.loadData(url)
          if loaded:
            if isinstance(loaded, str):
              if hasattr(self, 'processText'):
                self.processText(loaded, event)

            else:
              newPids = [x.pid for x in loaded]
              projects = [x for x in newPids if x.startswith('PR:')]
              if projects:
                pids = projects[:1]
                if len(data) > 1 or len(newPids) > 1:
                  showWarning('Incorrect data load',
                              "Attempt to load project together with other data. Other data ignored",
                              colourScheme=self._appBase.preferences.general.colourScheme)
                break
              else:
                pids.extend(newPids)
          else:
            if isinstance(self, CcpnDock):
              self.overlay.hide()

        for pid in pids:
          pluralClassName = ccpnUtil.pid2PluralName(pid)

          # NBNB Code to put other data types in side bar must go here

          if pluralClassName == 'Spectra':
            spectrum = self.getByPid(pid)
            # self._appBase.mainWindow.sideBar.addSpectrum(spectrum)

      else:
        raise ValueError("processDropData does not recognise dataType %s" % dataType)

      # process pids
      if pids:

        tags = []
        tags = [ccpnUtil.pid2PluralName(x) for x in pids]
        if  len(set(tags)) == 1:
          # All pids of same type - process entire list with a single process call
          funcName = 'process' + tags[0]
          if hasattr(self, funcName):
            getattr(self,funcName)(pids, event)
          elif funcName == 'processProjects':
            # We never need to process a project
            pass
          else:
            project._logger.warning("Dropped data not processed - no %s function defined for %s"
            % (funcName, self))

        else:
          # Treat each Pid separately (but still pass it in a list - NBNB)
          # If we need special functions for multi-type processing they must go here.
          for ii,tag in enumerate(tags):
            funcName = 'process' + tag
            if hasattr(self, funcName):
              getattr(self,funcName)([pids[ii]], event)
            else:
              project._logger.warning("Dropped data %s not processed - no %s function defined for %s"
              % (pid, funcName, self))


  # def selectDispatchFunction(self, prefix:str, dataType:(str,Pid)):
  #   """Generate file name and return bound method matching name, if defined
  #   dataType may be either an accepted dataType, or a Pid that is used to derive it.
  #
  #   Accepted prefixes are 'process', currently
  #   DataTypes are singular, e.g. Spectrum, Peak, etc. even """
  #
  #   if not pidTypeMap:
  #     # NBNB TBD FIXME: Import of application should not be allowed here.
  #     # It will not break when put in function, but in theory application.core should not depend on ccpnmr
  #     import ccpn
  #     import ccpnmr
  #     for package in ccpn, ccpnmr:
  #       for tag in dir(package):
  #         obj = getattr(package, tag)
  #         if hasattr(obj, 'shortClassName'):
  #           shortClassName = getattr(obj, 'shortClassName')
  #           if shortClassName:
  #             pidTypeMap[shortClassName] = (obj.className if hasattr(obj, 'className')
  #                                           else obj.__class__.__name__)
  #
  #   ss = dataType.split(Pid.PREFIXSEP,1)[0]
  #   ss = pidTypeMap.get(ss, ss)
  #   funcName = prefix + ss
  #
  #   if hasattr(self, funcName):
  #     # print(funcName)
  #     return getattr(self, funcName)
  #   else:
  #
  #     return None
