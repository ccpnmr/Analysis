

from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PulldownList import PulldownList

from ccpn.util.Colour import spectrumColours

class PeakListPropertiesPopup(QtGui.QDialog, Base):
  def __init__(self, parent=None, peakList=None, **kw):
    super(PeakListPropertiesPopup, self).__init__(parent)
    Base.__init__(self, **kw)
    self.peakListViews = [peakListView for peakListView in peakList.project.peakListViews if peakListView.peakList == peakList]
    self.peakListLabel = Label(self, "PeakList Name ", grid=(0, 0))
    self.peakListLabel = Label(self, peakList.id, grid=(0, 1))
    self.displayedLabel = Label(self, 'Is displayed', grid=(1, 0))
    self.displayedCheckBox = CheckBox(self, grid=(1, 1))
    self.symbolLabel = Label(self, 'Peak Symbol', grid=(2, 0))
    self.symbolPulldown = PulldownList(self, grid=(2, 1))
    self.symbolPulldown.setData(['x'])
    self.symbolColourLabel = Label(self, 'Peak Symbol Colour', grid=(3, 0))
    self.symbolColourPulldownList = PulldownList(self, grid=(3, 1))
    self._fillColourPulldown(self.symbolColourPulldownList)
    self.symbolColourPulldownList.setCurrentIndex(list(spectrumColours.keys()).index(self.peakListViews[0].symbolColour))
    self.symbolColourPulldownList.currentIndexChanged.connect(self._changeSymbolColour)

    self.textColourLabel = Label(self, 'Peak Text Colour', grid=(4, 0))
    self.textColourPulldownList = PulldownList(self, grid=(4, 1))
    self._fillColourPulldown(self.textColourPulldownList)
    self.textColourPulldownList.setCurrentIndex(list(spectrumColours.keys()).index(self.peakListViews[0].textColour))
    self.textColourPulldownList.currentIndexChanged.connect(self._changeTextColour)

    self.minimalAnnotationLabel = Label(self, 'Minimal Annotation', grid=(5, 0))
    self.minimalAnnotationCheckBox = CheckBox(self, grid=(5, 1))
    self.closeButton = Button(self, text='Close', grid=(6, 1), callback=self.accept)

    if(any([peakListView.isVisible() for peakListView in self.peakListViews])):
      self.displayedCheckBox.setChecked(True)

    for peakListView in self.peakListViews:
      self.displayedCheckBox.toggled.connect(peakListView.setVisible)

  def _changeSymbolColour(self, value):
    colour = list(spectrumColours.keys())[value]
    for peakListView in self.peakListViews:
      peakListView.symbolColour = colour


  def _changeTextColour(self, value):
    colour = list(spectrumColours.keys())[value]
    for peakListView in self.peakListViews:
      peakListView.textColour = colour

  def _fillColourPulldown(self, pulldown):
    for item in spectrumColours.items():
      pix=QtGui.QPixmap(QtCore.QSize(20, 20))
      pix.fill(QtGui.QColor(item[0]))
      pulldown.addItem(icon=QtGui.QIcon(pix), text=item[1])

