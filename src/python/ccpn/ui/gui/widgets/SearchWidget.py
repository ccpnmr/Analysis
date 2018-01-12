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

import json
import re

from PyQt4 import QtGui, QtCore
import pandas as pd
from pyqtgraph import TableWidget
import os
from ccpn.core.lib.CcpnSorting import universalSortKey
from ccpn.core.lib.CallBack import CallBack
from ccpn.core.lib.DataFrameObject import DataFrameObject
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets import MessageDialog
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Splitter import Splitter
from ccpn.ui.gui.widgets.TableModel import ObjectTableModel
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.TableFilter import ObjectTableFilter
from ccpn.ui.gui.widgets.ColumnViewSettings import ColumnViewSettingsPopup
from ccpn.ui.gui.widgets.TableModel import ObjectTableModel
from ccpn.core.lib.Notifiers import Notifier
from functools import partial
from collections import OrderedDict

from collections import OrderedDict
from ccpn.util.Logging import getLogger


class QuickTableFilter(Frame):
  def __init__(self, table, parent=None, **kw):
    Frame.__init__(self, parent, setLayout=False, **kw)
    self.table = table

    labelColumn = Label(self,'Search in',)
    self.columnOptions = PulldownList(self,)
    # self.columnOptions.setMinimumWidth(self.columnOptions.sizeHint().width()*2)
    self.columnOptions.setMinimumWidth(40)
    self.searchLabel = Label(self,'Search for',)
    self.edit = LineEdit(self,)
    self.searchButtons = ButtonList(self, texts=['Close','Reset','Search'], tipTexts=['Close Search','Restore Table','Search'],
                                   callbacks=[self.hideSearch
                                              , partial(self.restoreTable, self.table)
                                              , partial(self.findOnTable, self.table)])
    self.searchButtons.buttons[1].setEnabled(False)
    self.searchButtons.setFixedHeight(30)

    self.widgetLayout = QtGui.QHBoxLayout()
    self.setLayout(self.widgetLayout)
    ws = [labelColumn,self.columnOptions, self.searchLabel,self.edit, self.searchButtons]
    for w in ws:
      self.widgetLayout.addWidget(w)
    self.setColumnOptions()
    self.widgetLayout.setContentsMargins(0,0,0,0)
    self.setContentsMargins(0,0,0,0)

    self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Minimum)

  def setColumnOptions(self):
    # columns = self.table._dataFrameObject.columns
    # texts = [c.heading for c in columns]
    # objectsRange = range(len(columns))

    texts = self.table._dataFrameObject.headings
    objectsRange = range(len(texts))

    self.columnOptions.clear()
    self.columnOptions.addItem('<Whole Table>', object=None)
    for i, text in enumerate(texts):
      self.columnOptions.addItem(text, objectsRange[i])
    self.columnOptions.setIndex(0)

  def updateSearchWidgets(self, table):
    self.table = table
    self.setColumnOptions()
    self.searchButtons.buttons[1].setEnabled(False)

  def hideSearch(self):
    self.restoreTable(self.table)
    if self.table.searchWidget is not None:
      self.table.searchWidget.hide()

  def restoreTable(self, table):
    self.table.refreshTable()
    self.edit.clear()
    self.searchButtons.buttons[1].setEnabled(False)

  def findOnTable(self, table):
    if self.edit.text() == '' or None:
      self.restoreTable(table)
      return

    self.table = table
    text = self.edit.text()
    columns = self.table._dataFrameObject.headings

    if self.columnOptions.currentObject() is None:

      df = self.table._dataFrameObject.dataFrame
      idx = df[columns[0]].apply(lambda x:text in str(x))
      for col in range(1, len(columns)):
        idx = idx | df[columns[col]].apply(lambda x:text in str(x))
      self._searchedDataFrame = df.loc[idx]

    else:
      objCol = columns[self.columnOptions.currentObject()]

      df = self.table._dataFrameObject.dataFrame
      self._searchedDataFrame = df.loc[df[objCol].apply(lambda x:text in str(x))]

    if not self._searchedDataFrame.empty:
      self.table.setData(self._searchedDataFrame.values)
      self.table.refreshHeaders()
      self.searchButtons.buttons[1].setEnabled(True)
    else:
      self.searchButtons.buttons[1].setEnabled(False)
      self.restoreTable(table)
      MessageDialog.showWarning('Not found', '')


def attachSearchWidget(table):
  """
  Attach the search widget to the bottom of the table widget
  """
  try:
    if table._parent is not None:
      parentLayout = None
      if isinstance(table._parent, Base):
      # if hasattr(table.parent, 'getLayout'):
        parentLayout = table._parent.getLayout()

      if isinstance(parentLayout, QtGui.QGridLayout):
        idx = parentLayout.indexOf(table)
        location = parentLayout.getItemPosition(idx)
        if location is not None:
          if len(location)>0:
            row, column, rowSpan, columnSpan = location
            table.searchWidget = QuickTableFilter(table=table, vAlign='B')
            parentLayout.addWidget(table.searchWidget, row+1, column, rowSpan+1, columnSpan)
            table.searchWidget.hide()

            # TODO:ED move this to the tables
            # parentLayout.setVerticalSpacing(0)
    return True
  except:
    return False