from application.core.popups.SampleSetupPopup import solvents, SamplePopup, ExcludeRegions
from application.metabolomics.GuiPipeLine import PolyBaseline
from PyQt4 import QtCore, QtGui
from ccpncore.gui.Dock import CcpnDock
from ccpncore.gui.Base import Base
from ccpncore.gui.ScrollArea import ScrollArea
from ccpncore.gui.Table import ObjectTable, Column
from ccpncore.gui.LineEdit import LineEdit
from ccpncore.gui.PulldownList import PulldownList
from ccpncore.gui.Frame import Frame
from ccpncore.gui.CheckBox import CheckBox
from ccpncore.gui.ButtonList import ButtonList
from ccpncore.gui.Button import Button
from ccpncore.gui.Icon import Icon
from ccpncore.gui.GroupBox import GroupBox
from ccpncore.gui.DoubleSpinbox import DoubleSpinbox
from ccpncore.gui.Label import Label
from functools import partial
from application.metabolomics import GuiPipeLine as gp



#
class MetabolomicsModule(CcpnDock, Base):

  def __init__(self, project, **kw):

    super(MetabolomicsModule, self)
    CcpnDock.__init__(self, name='Metabolomics')
    Base.__init__(self, **kw)
    self.project = project


    self.pipelineMainGroupBox = GroupBox('Pipeline')
    self.pipelineMainVLayout = QtGui.QVBoxLayout()
    self.pipelineMainVLayout.setAlignment(QtCore.Qt.AlignTop)
    self.setLayout(self.pipelineMainVLayout)
    self.goArea = GoArea(self, project)
    self.layout.addWidget(self.goArea, 0, 0)
    self.pipelineMainGroupBox.setLayout(self.pipelineMainVLayout)
    self.scrollArea = ScrollArea(self)
    self.scrollArea.setWidget(self.pipelineMainGroupBox)
    self.scrollArea.setWidgetResizable(True)
    self.layout.addWidget(self.scrollArea, 1, 0)

    widget = (PipelineWidgets(self, project))
    self.pipelineMainVLayout.addWidget(widget)
    # self.checkBox = CheckBox(self, text='Auto-Update')

class GoArea(QtGui.QWidget):

  def __init__(self, parent=None, project=None, **kw):
    super(GoArea, self).__init__(parent)
    self.spectrumGroupLabel = Label(self, 'Input Data ', grid=(0, 0))
    self.spectrumGroupPulldown = PulldownList(self, grid=(0, 1))
    self.autoUpdateLabel = Label(self, 'Auto Update', grid=(0, 2))
    self.autoUpdateBox = CheckBox(self, grid=(0, 3))


class PipelineWidgets(QtGui.QWidget):
  '''
  '''


  def __init__(self, parent=None, project=None, **kw):
    super(PipelineWidgets, self).__init__(parent)
    # Base.__init__(self, **kw)
    self.project = project
    self.pullDownData = {
                'Poly Baseline': gp.PolyBaseline(self, self.project),
                'Align To Reference': gp.AlignToReference(self, self.project),
                'Align Spectra': gp.AlignSpectra(self, self.project),
                'Scale': gp.Scale(self, self.project),
                'Segmental Align': gp.SegmentalAlign(self, self.project),
                'Whittaker Baseline': gp.WhittakerBaseline(self, self.project),
                'Whittaker Smooth': gp.WhittakerSmooth(self, self.project),
                'Bin': gp.Bin(self, self.project),
                'Exclude Baseline Points': gp.ExcludeBaselinePoints(self, self.project),
                'Normalise Spectra': gp.NormaliseSpectra(self, self.project),
                'Exclude Signal Free Regions': gp.ExcludeSignalFreeRegions(self, self.project)}



    self.moveUpRowIcon = Icon('iconsNew/sort-up')
    self.moveDownRowIcon = Icon('iconsNew/sort-down')
    self.addRowIcon = Icon('iconsNew/plus')
    self.removeRowIcon = Icon('iconsNew/minus')

    self.mainWidgets = GroupBox(self)
    self.mainWidgets.setFixedHeight(80)
    self.mainWidgets_layout = QtGui.QHBoxLayout(self.mainWidgets)

    self.pulldownAction = PulldownList(self,)
    self.pulldownAction.setFixedWidth(130)
    self.pulldownAction.setFixedHeight(25)

    pdData = list(self.pullDownData.keys())
    pdData.insert(0, '< Select Method >')
    self.selectMethod = '< Select Method >'


    self.pulldownAction.setData(pdData)
    self.pulldownAction.activated[str].connect(self.addMethod)

    self.checkBox = CheckBox(self, text='active')


    self.moveUpDownButtons = ButtonList(self, texts = ['︎','︎︎'], callbacks=[self.moveRowUp, self.moveRowDown], icons=[self.moveUpRowIcon,self.moveDownRowIcon],
                                       tipTexts=['Move row up', 'Move row down'], direction='h', hAlign='r')
    self.moveUpDownButtons.setFixedHeight(40)
    self.moveUpDownButtons.setFixedWidth(40)
    self.moveUpDownButtons.setStyleSheet('font-size: 10pt')

    self.addRemoveButtons = ButtonList(self, texts = ['',''], callbacks=[self.addRow, self.removeRow],icons=[self.addRowIcon,self.removeRowIcon],
                                       tipTexts=['Add new row', 'Remove row '],  direction='H', hAlign='l' )
    self.addRemoveButtons.setStyleSheet('font-size: 10pt')
    self.addRemoveButtons.setFixedHeight(40)
    self.addRemoveButtons.setFixedWidth(40)

    self.mainWidgets_layout.addWidget(self.pulldownAction,)
    self.mainWidgets_layout.addWidget(self.checkBox,)

    self.mainWidgets_layout.addWidget(self.moveUpDownButtons,)
    self.mainWidgets_layout.addWidget(self.addRemoveButtons,)
    self.addRemoveButtons.buttons[0].setEnabled(False)
    self.goBox = self.parent().goArea.autoUpdateBox
    self.goBox.toggled.connect(self.runPipeline)




  def addMethod(self, selected):
     self.updateLayout()

     if selected != '< Select Method >':
      obj = self.pullDownData[selected]
      self.mainWidgets_layout.insertWidget(2, obj, 1)
      mainVboxLayout = obj.parent().parent().parent().layout()
      items = [mainVboxLayout.itemAt(i) for i in range(mainVboxLayout.count())]
      self.enableAddButton(items)


  def updateLayout(self):
    layout = self.mainWidgets_layout
    item = layout.itemAt(2)
    if item.widget() is not self.moveUpDownButtons:
      item.widget().hide()
      layout.removeItem(item)


  def moveRowUp(self):
    '''
    obj => sender = button, parent1= buttonList, parent2= GroupBox1, parent3=PipelineWidgets obj
    objLayout is the main parent layout (VLayout)
    '''
    obj = self.sender().parent().parent().parent()
    objLayout = obj.parent().layout()
    currentPosition = objLayout.indexOf(obj)
    newPosition = max(currentPosition-1, 0)
    objLayout.insertWidget(newPosition, obj)

  def moveRowDown(self):
    '''
    obj as above
    objLayout is the main parent layout (VLayout)
    '''

    obj = self.sender().parent().parent().parent()
    objLayout = obj.parent().layout()
    currentPosition = objLayout.indexOf(obj)
    newPosition = min(currentPosition+1, objLayout.count()-1)
    objLayout.insertWidget(newPosition, obj)

  def addRow(self):
    '''
    This function will add a new Pipelinewidgets obj in the next row below the clicked button.
    '''

    newObj = (PipelineWidgets(self, self.project))
    obj = self.sender().parent().parent().parent()
    objLayout = obj.parent().layout()
    currentPosition = objLayout.indexOf(obj)
    newPosition = min(currentPosition+1, objLayout.count())
    objLayout.insertWidget(newPosition, newObj)

    items = [objLayout.itemAt(i) for i in range(objLayout.count())]
    self.disableAddButton(items)


  def disableAddButton(self, items):
    '''
    If there is empty row with no method selected, will disable all the addButtons in each other row
    '''
    for i in items:
      if i.widget().pulldownAction.getText() == '< Select Method >':
        for i in items:
          i.widget().addRemoveButtons.buttons[0].setEnabled(False)

  def enableAddButton(self, items):
    '''
    If a method is selected, will enable all the addButtons in each other row
    '''
    for i in items:
      i.widget().addRemoveButtons.buttons[0].setEnabled(True)


  def removeRow (self):
    '''
    This function will remove the Pipelinewidgets selected from the main parent layout (VLayout)
    '''

    obj = self.sender().parent().parent().parent()
    objLayout = obj.parent().layout()
    currentPosition = objLayout.indexOf(obj)

    if objLayout.count() == 1 and currentPosition == 0:
      pass

    else:
      obj.deleteLater()

  def runPipeline(self):
    if self.goBox.isChecked():
      items = [self.mainWidgets_layout.itemAt(i) for i in range(self.mainWidgets_layout.count())]
      if isinstance(items[0].widget(), PulldownList):
          print(items[0].widget().currentText())
          if items[1].widget().isChecked():
            print(items[2].widget().getParams())









