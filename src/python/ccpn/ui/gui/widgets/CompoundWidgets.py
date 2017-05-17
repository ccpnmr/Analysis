#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: Geerten Vuister $"
__date__ = "$Date: 2017-04-18 15:19:30 +0100 (Tue, April 18, 2017) $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore
from functools import partial

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.ColourDialog import ColourDialog
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.CompoundBaseWidget import CompoundBaseWidget
from ccpn.util.Colour import spectrumColours
from ccpn.core.lib.Notifiers import Notifier

from ccpn.util.Logging import getLogger
logger = getLogger()

class ListCompoundWidget(CompoundBaseWidget):
  """
  Compound class comprising a Label, a PulldownList, and a ListWidget, combined in a 
  CompoundBaseWidget (i.e.a Frame)
  
  NB: can also be used as only a Label and a ListWidget by hiding the Pulldown:
        myWidget.showPulldownList(False)

    orientation       widget layout
    ------------      ------------------------    
    left:             Label       PullDown         
                                  ListWidget

    centreLeft:                   PullDown         
                      Label       ListWidget

    right:            PullDown    Label   
                      ListWidget

    centreRight:      PullDown       
                      ListWidget  Label

    top:              Label
                      PullDown       
                      ListWidget

    bottom:           PullDown       
                      ListWidget
                      Label

    horizontal:       Label       PullDown  ListWidget

  """
  layoutDict = dict(
    # grid positions for label, pulldown and listWidget for the different orientations
    left        = [(0, 0), (0, 1), (1, 1)],
    centreLeft  = [(1, 0), (0, 1), (1, 1)],
    right       = [(0, 1), (0, 0), (1, 0)],
    centreRight = [(1, 1), (0, 0), (1, 0)],
    top         = [(0, 0), (1, 0), (2, 0)],
    bottom      = [(2, 0), (0, 0), (1, 0)],
    horizontal  = [(0, 0), (0, 1), (0, 2)],
  )

  def __init__(self, parent=None, showBorder=False, orientation='left',
                     minimumWidths=None, maximumWidths=None, fixedWidths=None,
                     labelText='', texts=None, callback=None,
                     defaults=None, uniqueList=True, **kwds):
    """
    :param parent: parent widget
    :param showBorder: flag to display the border of Frame (True, False)
    :param orientation: flag to determine the orientation of the labelText relative to the Pulldown/ListWidget.
                        Allowed values: 'left', 'right', 'top', 'bottom', 'centreLeft, centreRight, horizontal
    :param minimumWidths: tuple of three values specifying the minimum width of the Label, Pulldown and ListWidget, 
                          respectively
    :param maximumWidths: tuple of three values specifying the maximum width of the Label and Pulldown and ListWidget, 
                          respectively
    :param fixedWidths: tuple of three values specifying the maximum width of the Label and Pulldown and ListWidget, 
                        respectively
    :param labelText: Text for the Label
    :param texts: (optional) iterable generating text values for the Pulldown
    :param callback: (optional) callback for the Pulldown
    :param defaults: (optional) iterable of initially add elements to the ListWidget (text or index)
    :param uniqueList: (True) only allow unique elements in the ListWidget
    :param kwds: (optional) keyword, value pairs for the gridding of Frame
    """

    CompoundBaseWidget.__init__(self, parent=parent, layoutDict=self.layoutDict, orientation=orientation,
                                showBorder=showBorder, **kwds)

    self.label = Label(parent=self, text=labelText, vAlign='center')
    self._addWidget(self.label)

    # pulldown
    texts = [' > select-to-add <'] + list(texts)
    self.pulldownList = PulldownList(parent=self, texts=texts, callback=self._addToListWidget, index=0)
    self._addWidget(self.pulldownList)

    # listWidget
    self.listWidget = ListWidget(parent=self, callback=callback)
    self._uniqueList = uniqueList
    if defaults is not None:
      for dft in defaults:
        self.addPulldownItem(dft)
    self._addWidget(self.listWidget)

    if minimumWidths is not None:
      self.setMinimumWidths(minimumWidths)

    if maximumWidths is not None:
      self.setMinimumWidths(maximumWidths)

    if fixedWidths is not None:
      self.setFixedWidths(fixedWidths)

  def showPulldownList(self, show):
    if show:
      self.pulldownList.show()
    else:
      self.pulldownList.hide()

  def getTexts(self):
    "Convenience: Return list of texts in listWidget"
    return [self.listWidget.item(i).text() for i in range(self.listWidget.count())]

  def addText(self, text):
    "Convenience: Add text to listWidget"
    if text is None:
      return
    if self._uniqueList and text in self.getTexts():
      return
    self.listWidget.addItem(text)

  def addPulldownItem(self, item):
    "convenience: add pulldown item (text or index) to list"
    texts = self.pulldownList.texts
    if item in texts:
      self.addText(item)
      return
    try:
      item = texts[int(item)+1] # added "select-to-add" to pulldownlist
      self.addText(item)
    except:
      pass

  def _addToListWidget(self, item):
    "Callback for Pulldown, adding the selcted item to the listWidget"
    if item is not None and self.pulldownList.getSelectedIndex() != 0:
      self.addText(item)
    # reset to first > select-to-add < entry
    self.pulldownList.setIndex(0)


class PulldownListCompoundWidget(CompoundBaseWidget):
  """
  Compound class comprising a Label and a PulldownList, combined in a CompoundBaseWidget (i.e. a Frame)

    orientation       widget layout
    ------------      ------------------------    
    left:             Label       PullDown         

    right:            PullDown    Label   

    top:              Label
                      PullDown       

    bottom:           PullDown       
                      Label

  """
  layoutDict = dict(
    # grid positions for label and pulldown for the different orientations
    left   = [(0, 0), (0, 1)],
    right  = [(0, 1), (0, 0)],
    top    = [(0, 0), (1, 0)],
    bottom = [(1, 0), (0, 0)],
  )

  def __init__(self, parent=None, showBorder=False, orientation='left',
               minimumWidths=None, maximumWidths=None, fixedWidths=None,
               labelText='', texts=None, callback=None, default=None, **kwds):
    """
    :param parent: parent widget
    :param showBorder: flag to display the border of Frame (True, False)
    :param orientation: flag to determine the orientation of the labelText relative to the pulldown widget.
                        Allowed values: 'left', 'right', 'top', 'bottom'
    :param minimumWidths: tuple of two values specifying the minimum width of the Label and Pulldown widget, respectively
    :param maximumWidths: tuple of two values specifying the maximum width of the Label and Pulldown widget, respectively
    :param labelText: Text for the Label
    :param texts: (optional) iterable generating text values for the Pulldown
    :param callback: (optional) callback for the Pulldown
    :param default: (optional) initially selected element of the Pulldown (text or index)
    :param kwds: (optional) keyword, value pairs for the gridding of Frame
    """

    CompoundBaseWidget.__init__(self, parent=parent, layoutDict=self.layoutDict, orientation=orientation,
                                showBorder=showBorder, **kwds)

    self.label = Label(parent=self, text=labelText, vAlign='center')
    self._addWidget(self.label)

    # pulldown text
    if texts is not None:
      texts = list(texts)
    # pulldown default index
    index = 0
    if default is not None and texts is not None and len(texts)> 0:
      if default in texts:
        index = texts.index(default)
      else:
        try:
          index = int(default)
        except:
          pass
    self.pulldownList = PulldownList(parent=self, texts=texts, callback=callback, index=index)
    self._addWidget(self.pulldownList)

    if minimumWidths is not None:
      self.setMinimumWidths(minimumWidths)

    if maximumWidths is not None:
      self.setMinimumWidths(maximumWidths)

    if fixedWidths is not None:
      self.setFixedWidths(fixedWidths)

  def getText(self):
    "Convenience: Return selected text in Pulldown"
    return self.pulldownList.currentText()

  def select(self, item):
    "Convenience: Set item in Pulldown; works with text or item"
    return self.pulldownList.select(item)

  def updatePulldownList(self, theObject, triggers, targetName, func, *args, **kwds):
    """
    Define a notifier to update the pulldown list by calling func(theObj, *args, **kwds) 

    :param theObject: A valid V3 core or current object
    :param triggers: any of the triggers, as defined in Notifier class
    :param targetName: a valid target for theObject, as defined in the Notifier class
    :param func: func(theObject, *args, **kwds) should return a list with the new pulldown elements
    :param args: optional arguments to func
    :param kwds: optional keyword arguments to func
    :return: Notifier instance
    """
    notifier = self.addObjectNotifier(theObject, triggers, targetName, self._updatePulldownList, *args, **kwds)
    notifier._listFunc = func
    return notifier

  def _updatePulldownList(self, callbackDict, *args, **kwds):
    "Here the action is done to update the pulldown list"
    listFunc = callbackDict[Notifier.NOTIFIER]._listFunc
    theObject = callbackDict[Notifier.THEOBJECT]
    trigger = callbackDict[Notifier.TRIGGER]       # ejb
    object = callbackDict[Notifier.OBJECT]         # ejb

    texts = listFunc(theObject, *args, **kwds)
    if texts is None:
      raise RuntimeError('Unable to update pulldownList')

    #FIXME:ED - fix to stop the removal of <Select Name> from head of list
    try:
      if trigger==Notifier.DELETE:                                # ejb - fix pulldownList delete
        item = getattr(object, Notifier.GETPID)
        tempPulldown = self.pulldownList.texts
        if item in tempPulldown:
          tempPulldown.remove(item)
          self.pulldownList.clear()
          self.pulldownList.setData(texts=tempPulldown)
      elif trigger==Notifier.CREATE:                               # ejb - fix pulldownList create
        item = getattr(object, Notifier.GETPID)
        tempPulldown = self.pulldownList.texts
        if item not in tempPulldown:
          tempPulldown.append(item)
          self.pulldownList.clear()
          self.pulldownList.setData(texts=tempPulldown)
      elif trigger == Notifier.RENAME:                            # ejb - fix pulldownList create
        item = getattr(object, Notifier.GETPID)
        tempPulldown = self.pulldownList.texts
        if item not in tempPulldown:
          tempPulldown.remove(callbackDict[Notifier.OLDPID])
          tempPulldown.append(item)
          self.pulldownList.clear()
          self.pulldownList.setData(texts=tempPulldown)
      else:
        self.pulldownList.clear()
        self.pulldownList.setData(texts=texts)
    except:
      pass

class CheckBoxCompoundWidget(CompoundBaseWidget):
  """
  Compound class comprising a Label and a CheckBox, combined in a CompoundBaseWidget (i.e. a Frame)

    orientation       widget layout
    ------------      ------------------------    
    left:             Label       CheckBox         

    right:            CheckBox    Label   

    top:              Label
                      CheckBox       

    bottom:           CheckBox       
                      Label

  """
  layoutDict = dict(
    # grid positions for label and checkBox for the different orientations
    left   = [(0, 0), (0, 1)],
    right  = [(0, 1), (0, 0)],
    top    = [(0, 0), (1, 0)],
    bottom = [(1, 0), (0, 0)],
  )

  def __init__(self, parent=None, showBorder=False, orientation='left',
               minimumWidths=None, maximumWidths=None, fixedWidths=None,
               labelText='', text='', callback=None, checked=False, **kwds):
    """
    :param parent: parent widget
    :param showBorder: flag to display the border of Frame (True, False)
    :param orientation: flag to determine the orientation of the labelText relative to the CheckBox widget.
                        Allowed values: 'left', 'right', 'top', 'bottom'
    :param minimumWidths: tuple of two values specifying the minimum width of the Label and CheckBox widget, respectively
    :param maximumWidths: tuple of two values specifying the maximum width of the Label and CheckBox widget, respectively
    :param labelText: Text for the Label
    :param text: (optional) text for the Checkbox
    :param callback: (optional) callback for the CheckBox
    :param checked: (optional) initial state of the CheckBox
    :param kwds: (optional) keyword, value pairs for the gridding of Frame
    """

    CompoundBaseWidget.__init__(self, parent=parent, layoutDict=self.layoutDict, orientation=orientation,
                                showBorder=showBorder, **kwds)

    self.label = Label(parent=self, text=labelText, vAlign='center')
    self._addWidget(self.label)

    hAlign = orientation if (orientation == 'left' or orientation == 'right') else 'center'
    self.checkBox = CheckBox(parent=self, checked=checked, text=text, callback=callback, hAlign=hAlign)
    self._addWidget(self.checkBox)

    if minimumWidths is not None:
      self.setMinimumWidths(minimumWidths)

    if maximumWidths is not None:
      self.setMaximumWidths(maximumWidths)

    if fixedWidths is not None:
      self.setFixedWidths(fixedWidths)

  def isChecked(self):
    "Convenience: Return whether checkBox is checked"
    return self.checkBox.isChecked()


class DoubleSpinBoxCompoundWidget(CompoundBaseWidget):
  """
  Compound class comprising a Label and a DoubleSpinBox, combined in a CompoundBaseWidget (i.e. a Frame)

    orientation       widget layout
    ------------      ------------------------    
    left:             Label          DoubleSpinBox         

    right:            DoubleSpinBox  Label   

    top:              Label
                      DoubleSpinBox       

    bottom:           DoubleSpinBox       
                      Label

  """
  layoutDict = dict(
    # grid positions for label and checkBox for the different orientations
    left   = [(0, 0), (0, 1)],
    right  = [(0, 1), (0, 0)],
    top    = [(0, 0), (1, 0)],
    bottom = [(1, 0), (0, 0)],
  )

  def __init__(self, parent=None, showBorder=False, orientation='left',
               minimumWidths=None, maximumWidths=None, fixedWidths=None,
               labelText='', value=None, range=(None,None), step=None, showButtons=True,
               decimals=None, callback=None, **kwds):
    """
    :param parent: parent widget
    :param showBorder: flag to display the border of Frame (True, False)
    :param orientation: flag to determine the orientation of the labelText relative to the DoubleSpinBox widget.
                        Allowed values: 'left', 'right', 'top', 'bottom'
    :param minimumWidths: tuple of two values specifying the minimum width of the Label and DoubleSpinBox widget, respectively
    :param maximumWidths: tuple of two values specifying the maximum width of the Label and DoubleSpinBox widget, respectively
    :param labelText: Text for the Label
    :param value: initial value for the DoubleSpinBox
    :param range: (minimumValue, maximumValue) tuple for the DoubleSpinBox
    :param step: initial step for the increment of the DoubleSpinBox buttons
    :param decimals: number of decimals the DoubleSpinBox to display
    :param showButtons: flag to display the DoubleSpinBox buttons (True, False)
    :param kwds: (optional) keyword, value pairs for the gridding of Frame
    """

    CompoundBaseWidget.__init__(self, parent=parent, layoutDict=self.layoutDict, orientation=orientation,
                                showBorder=showBorder, **kwds)

    self.label = Label(parent=self, text=labelText, vAlign='center')
    self._addWidget(self.label)

    hAlign = orientation if (orientation == 'left' or orientation == 'right') else 'center'
    minimumValue = range[0] if range[0] is not None else None
    maximumValue = range[1] if range[1] is not None else None
    self.doubleSpinBox = DoubleSpinbox(parent=self, value=value, min=minimumValue, max=maximumValue,
                                       step=step, showButtons=showButtons, decimals=decimals, hAlign=hAlign,
                                       callback=callback
                                      )
    self._addWidget(self.doubleSpinBox)

    if minimumWidths is not None:
      self.setMinimumWidths(minimumWidths)

    if maximumWidths is not None:
      self.setMinimumWidths(maximumWidths)

    if fixedWidths is not None:
      self.setFixedWidths(fixedWidths)

  def getValue(self)-> float:
    "get the value from the DoubleSpinBox"
    return self.doubleSpinBox.value()

  def setValue(self, value:float):
    "set the value from the DoubleSpinBox"
    return self.doubleSpinBox.setValue(value)



class SelectorWidget(QtGui.QWidget, Base):

  def __init__(self, parent=None, label='', data=None, callback=None, **kw):

    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    if data:
      data.insert(0, '')
    label1 = Label(self, text=label, grid=(0, 0))
    self.pulldownList = InputPulldown(self, grid=(0, 1), texts=data, callback=callback)


class InputPulldown(PulldownList):

  def __init__(self, parent=None, callback=None, **kw):
    PulldownList.__init__(self, parent, **kw)

    self.setData(['', '<New Item>'])
    if callback:
      self.setCallback(callback)
    else:
      self.setCallback(self.addNewItem)

  def addNewItem(self, item):
    if item == '<New Item>':
      newItemText = LineEditPopup()
      newItemText.exec_()
      newItem = newItemText.inputField.text()
      texts = self.texts
      texts.insert(-2, newItem)
      if '' in texts:
        texts.remove('')
      self.setData(list(set(texts)))
      self.select(newItem)
      return newItem


class LineEditPopup(QtGui.QDialog, Base):

  def __init__(self, parent=None, dataType=None, **kw):

    QtGui.QDialog.__init__(self, parent)
    Base.__init__(self, **kw)

    inputLabel = Label(self, 'Input', grid=(0, 0))
    self.inputField = LineEdit(self, grid=(0, 1))

    ButtonList(self, grid=(1, 1), callbacks=[self.reject, self.returnItem], texts=['Cancel', 'OK'])

    if dataType:
      inputLabel.setText('New %s name' % dataType)

  def returnItem(self):
    self.accept()


class ColourSelectionWidget(Widget):

  def __init__(self, parent=None, labelName=None, **kw):
    Widget.__init__(self, parent, **kw)

    Label(self, labelName, grid=(0, 0))
    self.pulldownList = PulldownList(self, vAlign='t', hAlign='l', grid=(0, 1))
    for item in spectrumColours.items():
      pix=QtGui.QPixmap(QtCore.QSize(20, 20))
      pix.fill(QtGui.QColor(item[0]))
      self.pulldownList.addItem(icon=QtGui.QIcon(pix), text=item[1])
    Button(self, vAlign='t', hAlign='l', grid=(0, 2), hPolicy='fixed',
                            callback=partial(self._setColour), icon='icons/colours')

  def _setColour(self):
    dialog = ColourDialog()
    newColour = dialog.getColor()
    pix = QtGui.QPixmap(QtCore.QSize(20, 20))
    pix.fill(QtGui.QColor(newColour))
    newIndex = str(len(spectrumColours.items())+1)
    self.pulldownList.addItem(icon=QtGui.QIcon(pix), text='Colour %s' % newIndex)
    spectrumColours[newColour.name()] = 'Colour %s' % newIndex
    self.pulldownList.setCurrentIndex(int(newIndex)-1)

  def colour(self):
    return list(spectrumColours.keys())[self.pulldownList.currentIndex()]

  def setColour(self, value):
    self.pulldownList.select(spectrumColours[value])


if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.BasePopup import BasePopup

  app = TestApplication()

  def callback1(obj):
    print('callback1', obj)

  def callback2():
    print('callback2')

  popup = BasePopup(title='Testing widgets')

  # policyDict = dict(
  #   vAlign='top',
  #   hPolicy='expanding',
  # )
  policyDict = dict(
    vAlign='top',
    # hAlign='left',
  )
  # policyDict = dict(
  #   hAlign='left',
  # )
  # policyDict = {}

  row = -1

  row += 1
  checkBox1 = CheckBoxCompoundWidget(parent=popup, orientation='left', showBorder=True,
                                    minimumWidths=(150, 100),
                                    labelText='CheckboxCompoundWidget', text="test2",
                                    callback=callback2, grid=(row, 0), checked=True,
                                    **policyDict)

  row += 1
  texts = 'aap noot mies kees'.split()
  pulldownListwidget = PulldownListCompoundWidget(parent=popup, orientation='left', showBorder=True, minimumWidths=(150,100),
                                                  labelText='PulldownListCompoundWidget', texts=texts,
                                                  callback=callback1, grid=(row,0), default=0,
                                                  **policyDict )

  pulldownListwidget2 = PulldownListCompoundWidget(parent=popup, orientation='top', showBorder=True, maximumWidths=(10,10),
                                                  labelText='test-label on top which is longer', texts=texts,
                                                  callback=callback1, grid=(row,1), default='kees',
                                                  **policyDict )

  row += 1
  listWidget = ListCompoundWidget(parent=popup, orientation='left', showBorder=True,
                              labelText='ListCompoundWidget', texts=texts,
                              callback=callback2, grid=(row,0), defaults=texts[1:2],
                                **policyDict)
  listWidget.addPulldownItem(0)
  listWidget2 = ListCompoundWidget(parent=popup, orientation='top', showBorder=True,
                              labelText='ListCompoundWidget-hidden pulldown', texts=texts,
                              callback=callback2, grid=(row,1), defaults=[0,2],
                                **policyDict)
  listWidget2.showPulldownList(False)

  row += 1
  doubleSpinBox = DoubleSpinBoxCompoundWidget(parent=popup, labelText='doubleSpinBox: rage (-3,10)', grid=(row,0),
                                              callback = callback1, range=(-3,10)
                                              )

  row += 1
  doubleSpinBox2 = DoubleSpinBoxCompoundWidget(parent=popup, labelText='doubleSpinBox no buttons', grid=(row,0),
                                              showButtons=False, callback = callback1
                                              )

  app.start()
