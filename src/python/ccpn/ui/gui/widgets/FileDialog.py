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
__dateModified__ = "$dateModified: 2017-07-07 16:32:53 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui

import sys
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Frame import Frame

class FileDialog(QtGui.QFileDialog):

  # def __init__(self, parent=None, fileMode=QtGui.QFileDialog.AnyFile, text=None,
  #              acceptMode=QtGui.QFileDialog.AcceptOpen, preferences=None, **kw):

  def __init__(self, parent=None, fileMode=QtGui.QFileDialog.AnyFile, text=None,
               acceptMode=QtGui.QFileDialog.AcceptOpen, preferences=None, selectFile=None, filter=None, **kw):

    # ejb - added selectFile to suggest a filename in the file box
    #       this is not passed to the super class

    QtGui.QFileDialog.__init__(self, parent, caption=text, **kw)

    staticFunctionDict = {
      (0, 0): 'getOpenFileName',
      (0, 1): 'getOpenFileName',
      (0, 2): 'getExistingDirectory',
      (0, 3): 'getOpenFileNames',
      (1, 0): 'getSaveFileName',
      (1, 1): 'getSaveFileName',
      (1, 2): 'getSaveFileName',
      (1, 3): 'getSaveFileName',
      (self.AcceptOpen, self.AnyFile): 'getOpenFileName',
      (self.AcceptOpen, self.ExistingFile): 'getOpenFileName',
      (self.AcceptOpen, self.Directory): 'getExistingDirectory',
      (self.AcceptOpen, self.ExistingFiles): 'getOpenFileNames',
      (self.AcceptSave, self.AnyFile): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFile): 'getSaveFileName',
      (self.AcceptSave, self.Directory): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFiles): 'getSaveFileName',
    }

    self.setFileMode(fileMode)
    self.setAcceptMode(acceptMode)
    if filter is not None:
     self.setFilter(filter)

    if selectFile is not None:    # ejb - populates fileDialog with a suggested filename
      self.selectFile(selectFile)

    if preferences is None:
      self.useNative = False

    if preferences:
      self.useNative = preferences.useNative
      if preferences.colourScheme == 'dark':
        self.setStyleSheet("""
                           QFileDialog QWidget {
                                               background-color: #2a3358;
                                               color: #f7ffff;
                                               }
                           QFileDialog QPushButton { 
                                                color: #bec4f3;
                                                background-color: #535a83;
                                                border: 1px solid #182548;
                                                padding: 5px;
                                          }
                          """)
      elif preferences.colourScheme == 'light':
        self.setStyleSheet("""
                            QFileDialog QWidget {
                                                color: #464e76;
                                                }
                           QFileDialog QPushButton { 
                                                color: #fdfdfc;
                                                background-color: #bd8413;
                                                border: 1px solid #EDC151;
                                                padding: 5px;
                                          }
                          """)

    # self.result is '' (first case) or 0 (second case) if Cancel button selected
    if preferences and preferences.useNative and not sys.platform.lower() == 'linux':
      funcName = staticFunctionDict[(acceptMode, fileMode)]
      self.result = getattr(self, funcName)(caption=text, **kw)
    else:
      self.result = self.exec_()

  # overrides Qt function, which does not pay any attention to whether Cancel button selected
  def selectedFiles(self):

    if self.result and not self.useNative:
      return QtGui.QFileDialog.selectedFiles(self)
    elif self.result and self.useNative:
      return [self.result]
    else:
      return []

  # Qt does not have this but useful if you know you only want one file
  def selectedFile(self):

    files = self.selectedFiles()
    if files:
      return files[0]
    else:
      return None


class NefFileDialog(QtGui.QFileDialog):

  def __init__(self, parent=None, fileMode=QtGui.QFileDialog.AnyFile, text=None,
               acceptMode=QtGui.QFileDialog.AcceptOpen, preferences=None, selectFile=None, **kw):

    # ejb - added selectFile to suggest a filename in the file box
    #       this is not passed to the super class

    QtGui.QFileDialog.__init__(self, parent, caption=text, **kw)

    staticFunctionDict = {
      (0, 0): 'getOpenFileName',
      (0, 1): 'getOpenFileName',
      (0, 2): 'getExistingDirectory',
      (0, 3): 'getOpenFileNames',
      (1, 0): 'getSaveFileName',
      (1, 1): 'getSaveFileName',
      (1, 2): 'getSaveFileName',
      (1, 3): 'getSaveFileName',
      (self.AcceptOpen, self.AnyFile): 'getOpenFileName',
      (self.AcceptOpen, self.ExistingFile): 'getOpenFileName',
      (self.AcceptOpen, self.Directory): 'getExistingDirectory',
      (self.AcceptOpen, self.ExistingFiles): 'getOpenFileNames',
      (self.AcceptSave, self.AnyFile): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFile): 'getSaveFileName',
      (self.AcceptSave, self.Directory): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFiles): 'getSaveFileName',
    }

    self.setFileMode(fileMode)
    self.setAcceptMode(acceptMode)
    self.setLabelText(QtGui.QFileDialog.Accept, 'Select')

    if selectFile is not None:    # ejb - populates fileDialog with a suggested filename
      self.selectFile(selectFile)

    if preferences is None:
      self.useNative = False

    if preferences:
      self.useNative = preferences.useNative
      if preferences.colourScheme == 'dark':
        self.setStyleSheet("""
                           QFileDialog QWidget {
                                               background-color: #2a3358;
                                               color: #f7ffff;
                                               }
                          """)
      elif preferences.colourScheme == 'light':
        self.setStyleSheet("QFileDialog QWidget {color: #464e76; }")

  def selectedFiles(self):
    if self.useNative:
      # return empty list if the native dialog
      return None
    else:
      # the selectFile works and returns the file in the current directory
      if self.result and not self.useNative:
        return QtGui.QFileDialog.selectedFiles(self)
      elif self.result and self.useNative:
        return [self.result]
      else:
        return []

  def selectedFile(self):
    files = self.selectedFiles()
    if files:
      return files[0]
    else:
      return None

  def _setParent(self, parent, acceptFunc, rejectFunc):
    self.parent = parent
    self.acceptFunc = acceptFunc
    self.rejectFunc = rejectFunc

  def reject(self):
    super(NefFileDialog, self).reject()
    # self.rejectFunc()

  def accept(self):
    super(NefFileDialog, self).accept()
    # self.acceptFunc(self.selectedFile())

  def setLabels(self, save='Save', cancel='Cancel'):
    self.setLabelText(QtGui.QFileDialog.Accept, save)
    self.setLabelText(QtGui.QFileDialog.Reject, cancel)

  def _setResult(self, value):
    self.thisAccepted = value

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Widget import Widget
from os.path import expanduser

class LineEditButtonDialog(Widget, Base):
  def __init__(self,parent, textDialog=None, textLineEdit=None, fileMode=None, filter=None, directory=None, **kw):
    Widget.__init__(self, parent)
    Base.__init__(self, setLayout=True, **kw)
    self.openPathIcon = Icon('icons/directory')

    if textDialog is None:
      self.textDialog = ''
    else:
      self.textDialog = textDialog

    if textLineEdit is None:
      self.textLineEdit = expanduser("~")
    else:
      self.textLineEdit = textLineEdit

    if fileMode is None:
      self.fileMode = QtGui.QFileDialog.AnyFile
    else:
      self.fileMode = fileMode

    self.filter = filter
    self.directory = directory

    tipText= 'Click the icon to select'
    self.lineEdit = LineEdit(self, text=self.textLineEdit, textAlignment='l', hAlign='l', minimumWidth=100,
                             tipText=tipText, grid=(0, 0))
    self.lineEdit.setEnabled(False)
    self.lineEdit.setSizePolicy(QtGui.QSizePolicy.Expanding,
                  QtGui.QSizePolicy.Expanding)
    button = Button(self, text='', icon=self.openPathIcon, callback=self._openFileDialog, grid=(0, 1), hAlign='c')
    button.setStyleSheet("border: 0px solid transparent")

  def _openFileDialog(self):
    self.fileDialog = FileDialog(self, fileMode=self.fileMode, text=self.textDialog,
               acceptMode=QtGui.QFileDialog.AcceptOpen, directory=self.directory, filter=self.filter)

    selectedFile = self.fileDialog.selectedFile()
    if selectedFile:
      self.lineEdit.setText(str(selectedFile))
      return True
    else:
      return False



  def get(self):
    return self.lineEdit.text()

  def setText(self, text):
    self.lineEdit.setText(str(text))




if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.popups.Dialog import CcpnDialog
  app = TestApplication()
  popup = CcpnDialog(windowTitle='Test LineEditButtonDialog')
  slider = LineEditButtonDialog(parent=popup, fileMode=None, filter=('ccpn (*.ccpn)'))
  popup.show()
  popup.raise_()
  app.start()
