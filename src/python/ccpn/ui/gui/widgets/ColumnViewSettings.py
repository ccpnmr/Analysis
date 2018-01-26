"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = ""
__credits__ = ""
__licence__ = ("")
__reference__ = ("")
#=========================================================================================
# Last code modification:
#=========================================================================================
__modifiedBy__ = "$modifiedBy$"
__dateModified__ = "$dateModified$"
__version__ = "$Revision$"
#=========================================================================================
# Created:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.util.Logging import getLogger
from ccpn.core.lib.DataFrameObject import OBJECT_DATAFRAME


class ColumnViewSettingsPopup(CcpnDialog):
  # def __init__(self, table=None, parent=None, hideColumns=None, title='Column Settings', **kw):
  def __init__(self, dataFrameObject=None, parent=None, hideColumns=None, title='Column Settings', **kw):
    CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)
    self.setContentsMargins(5, 5, 5, 5)
    self.dataFrameObject = dataFrameObject
    # self.widgetColumnViewSettings = ColumnViewSettings(parent=self, table=table, hideColumns=hideColumns, grid=(0,0))
    self.widgetColumnViewSettings = ColumnViewSettings(parent=self, dataFrameObject=dataFrameObject, grid=(0,0))
    buttons = ButtonList(self, texts=['Close'], callbacks=[self._close], grid=(1,0), hAlign='c')
    self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

  def _close(self):
    'Save the hidden columns to the table class. So it remembers when you open again the popup'
    hiddenColumns = self.widgetColumnViewSettings._getHiddenColumns()
    self.dataFrameObject.hiddenColumns = hiddenColumns
    self.reject()
    return hiddenColumns

SEARCH_MODES = [ 'Literal','Case Sensitive Literal','Regular Expression' ]
CheckboxTipText = 'Select column to be visible on the table.'

class ColumnViewSettings(Widget):
  ''' hide show check boxes corresponding to the table columns '''

  def __init__(self, parent=None, dataFrameObject=None, direction='v', hideColumns=None, **kw):
    Widget.__init__(self, parent, setLayout=True, **kw)
    self.direction=direction
    # self.table = table
    self.dataFrameObject = dataFrameObject
    self.checkBoxes = []
    # self.hiddenColumns = []
    # self.hideColumns = hideColumns or []      # list of column names
    self._hideColumnWidths = {}
    self.initCheckBoxes()
    self.filterLabel =  Label(self, 'Display Columns', grid=(0,1), vAlign='t', hAlign='l')


  def initCheckBoxes(self):
    columns = self.dataFrameObject.headings   #   self.table._columns
    hiddenColumns = self.dataFrameObject.hiddenColumns or []

    if columns:
      for i, colum in enumerate(columns):

        # always ignore the special column
        if colum != OBJECT_DATAFRAME:
          if self.direction=='v':
            i+=1
            cb = CheckBox(self, text=colum, grid=(i, 1), callback=self.checkBoxCallBack
                          , checked=True if colum not in hiddenColumns else False,
                          hAlign='l',tipText= CheckboxTipText,)
          else:
            cb = CheckBox(self, text=colum, grid=(1, i), callback=self.checkBoxCallBack
                          , checked=True if colum not in hiddenColumns else False,
                          hAlign='l',tipText= CheckboxTipText,)

          cb.setMinimumSize(cb.sizeHint()*1.3)

          self.checkBoxes.append(cb)
          # if colum not in self.hideColumns:
          #   self._showColumn(i, colum)
          # else:
          #   self._hideColumn(i, colum)

  def _getHiddenColumns(self):
    return self.dataFrameObject.hiddenColumns

  def checkBoxCallBack(self):
    currentCheckBox = self.sender()
    name = currentCheckBox.text()
    # i = self.table._columns.index(name)
    i = self.dataFrameObject.headings.index(name)

    checkedBoxes = []

    for checkBox in self.checkBoxes:
      checkBox.setEnabled(True)
      if checkBox.isChecked():
        checkedBoxes.append(checkBox)
    if len(checkedBoxes)>0:
      if currentCheckBox.isChecked():
        self._showColumn(i, name)
      else:
        self._hideColumn(i, name)
    else: #always display at least one columns, disables the last checkbox
      currentCheckBox.setEnabled(False)
      currentCheckBox.setChecked(True)

  def updateWidgets(self, table):
    self.table = table
    if self.checkBoxes:
      for cb in self.checkBoxes:
        cb.deleteLater()
    self.checkBoxes = []
    self.initCheckBoxes()

  def _hideColumn(self, i, name):
    self.dataFrameObject.table.hideColumn(i)            #self.table.getColumnInt(columnName=name))
    # self._hideColumnWidths[name] = self.table.columnWidth(self.table.getColumnInt(columnName=name))
    if name not in self.dataFrameObject.hiddenColumns:
      self.dataFrameObject.hiddenColumns.append(name)
    # self.hiddenColumns.append(name)

  def _showColumn(self, i, name):
    self.dataFrameObject.table.showColumn(i)            #self.table.getColumnInt(columnName=name))
    # if name in self._hideColumnWidths:
    #   self.table.setColumnWidth(self.table.getColumnInt(columnName=name), self._hideColumnWidths[name])
    self.dataFrameObject.table.resizeColumnToContents(i)
    if name in self.dataFrameObject.hiddenColumns:
      self.dataFrameObject.hiddenColumns.remove(name)

  def showColumns(self):
    # hide the columns in the list
    columns = self.dataFrameObject.headings

    for i, colName in enumerate(columns):
      if colName in self.dataFrameObject.hiddenColumns:
        self._hideColumn(i, colName)
      else:
        self._showColumn(i, colName)

