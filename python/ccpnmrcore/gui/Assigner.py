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
import sys
from PyQt4 import QtGui,QtCore

from ccpncore.gui.Dock import CcpnDock, CcpnDockLabel
from ccpncore.gui.Font import Font

from pyqtgraph.dockarea import Dock

class Assigner(CcpnDock):

  def __init__(self, project=None):

    super(Assigner, self).__init__(name='Assigner')
    self.project=project
    self.setStyleSheet("""
    QWidget { background-color: #000021;
              border: 1px solid #00092d;
    }
    """)
    # self.label.hide()
    # self.label = DockLabel('Assigner', self)
    # self.label.show()
    self.scrollArea = QtGui.QScrollArea()
    self.scrollArea.setWidgetResizable(True)
    self.scene = QtGui.QGraphicsScene(self)
    self.scrollContents = QtGui.QGraphicsView(self.scene, self)
    self.scrollContents.setInteractive(True)
    self.scrollContents.setGeometry(QtCore.QRect(0, 0, 380, 1000))
    self.horizontalLayout2 = QtGui.QHBoxLayout(self.scrollContents)
    self.scrollArea.setWidget(self.scrollContents)
    self.residueCount = 0
    self.layout.addWidget(self.scrollArea)
    self.atomSpacing = 66
    self.residuesShown = []
    self.predictedStretch = []

    # self.dock.addWidget(self)


  # def assignLeft(self):
  #   self.direction = 'left'
  #
  # def assignRight(self):
  #   self.direction = 'right'


  def clearAllItems(self):
    for item in self.scene.items():
      self.scene.removeItem(item)
      self.residueCount = 0


  def addResidue(self, nmrResidue, direction=None):

    if self.residueCount == 0:
      hAtom = self.addAtom("H", (0, self.atomSpacing))
      nAtom = self.addAtom("N", (0, hAtom.y()-self.atomSpacing))
      caAtom = self.addAtom("CA", (nAtom.x()+self.atomSpacing, nAtom.y()))
      cbAtom = self.addAtom("CB", (caAtom.x(), caAtom.y()-self.atomSpacing))
      coAtom = self.addAtom("CO", (caAtom.x()+abs(caAtom.x()-nAtom.x()),nAtom.y()))
      self.scene.addItem(hAtom)
      self.scene.addItem(nAtom)
      self.scene.addItem(caAtom)
      atoms = [atom.name for atom in nmrResidue.atoms]
      if 'CB' in atoms:
        cBetaAtom = nmrResidue.fetchNmrAtom('CB')
      else:
        cBetaAtom = None

      if cBetaAtom is not None:
        self.scene.addItem(cbAtom)
        self.addAssignmentLine(caAtom, cbAtom, 'grey', 1.0, 0)
        cbShift = self.project.chemicalShiftLists[0].findChemicalShift(cBetaAtom)
        print('cbshift',cbShift.value)

      self.scene.addItem(coAtom)
      self.addAssignmentLine(hAtom, nAtom, 'grey', 1.0, 0)

      self.addAssignmentLine(nAtom, caAtom, 'grey', 1.0, 0)
      self.addAssignmentLine(coAtom, caAtom, 'grey', 1.0, 0)
      nmrAtomLabel = QtGui.QGraphicsTextItem()
      nmrAtomLabel.setPlainText(nmrResidue.sequenceCode)
      nmrAtomLabel.setFont(Font(size=12, bold=True))
      nmrAtomLabel.setDefaultTextColor(QtGui.QColor('#f7ffff'))
      nmrAtomLabel.setPos(caAtom.x()-caAtom.boundingRect().width()/2, caAtom.y()+30)
      self.scene.addItem(nmrAtomLabel)
      print(cBetaAtom,'cbeta')
      if cBetaAtom is None:
        predictionLabel = QtGui.QGraphicsTextItem()
        predictionLabel.setPlainText('GLY')
        predictionLabel.setPos(caAtom.x()-caAtom.boundingRect().width()/2, nmrAtomLabel.y()+30)
        self.scene.addItem(predictionLabel)
        self.predictedStretch.insert(0, 'G')
      else:
        if float(cbShift.value) < 25:
          print('ALA')
          predictionLabel = QtGui.QGraphicsTextItem()
          predictionLabel.setPlainText('ALA')
          predictionLabel.setPos(caAtom.x()-caAtom.boundingRect().width()/2, nmrAtomLabel.y()+30)
          self.scene.addItem(predictionLabel)
          self.predictedStretch.insert(0, 'A')
        elif float(cbShift.value) > 68:
          print('THR')
          predictionLabel = QtGui.QGraphicsTextItem()
          predictionLabel.setPlainText('THR')
          predictionLabel.setPos(caAtom.x()-caAtom.boundingRect().width()/2, nmrAtomLabel.y()+30)
          self.scene.addItem(predictionLabel)
          self.predictedStretch.insert(0, 'T')
        else:
          print('here')
          self.predictedStretch.insert(0, '.')


      newResidue = {'number':self.residueCount, 'H':hAtom, "N": nAtom, "CA":caAtom, "CB":cbAtom, "CO":coAtom}
      self.residuesShown.append(newResidue)
      self.residueCount+=1

    else:
      if len(self.residuesShown) > 0:
        if direction == 'left':
          oldResidue = self.residuesShown[0]
          coAtom2 = self.addAtom("CO", (oldResidue["N"].x()-abs(oldResidue["CA"].x()-oldResidue["N"].x())-(oldResidue["N"].boundingRect().width()/2),oldResidue["CA"].y()))
          caAtom2 = self.addAtom("CA", ((coAtom2.x()-self.atomSpacing), oldResidue["N"].y()))
          cbAtom2 = self.addAtom("CB", (caAtom2.x(), caAtom2.y()-self.atomSpacing))
          nAtom2 = self.addAtom("N",(caAtom2.x()-self.atomSpacing, coAtom2.y()))
          hAtom2 = self.addAtom("H", (nAtom2.x(), nAtom2.y()+self.atomSpacing))
          self.scene.addItem(coAtom2)
          self.scene.addItem(caAtom2)
          atoms = [atom.name for atom in nmrResidue.atoms]
          if 'CB' in atoms:
            cBetaAtom = nmrResidue.fetchNmrAtom('CB')
          else:
            cBetaAtom = None

          if cBetaAtom is not None:
            self.scene.addItem(cbAtom2)
            self.addAssignmentLine(caAtom2, cbAtom2, 'grey', 1.0, 0)
            cbShift = self.project.chemicalShiftLists[0].findChemicalShift(cBetaAtom)
          self.scene.addItem(nAtom2)
          self.scene.addItem(hAtom2)
          self.addAssignmentLine(nAtom2, hAtom2, 'grey', 1.0, 0)
          self.addAssignmentLine(caAtom2, coAtom2, 'grey', 1.0, 0)
          self.addAssignmentLine(coAtom2, oldResidue['N'], 'grey', 1.0, 0)
          # self.addAssignmentLine(cbAtom2, caAtom2, 'grey', 1.2, 0)
          self.addAssignmentLine(nAtom2, caAtom2, 'grey', 1.0, 0)
          nmrAtomLabel = QtGui.QGraphicsTextItem()
          nmrAtomLabel.setPlainText(nmrResidue.sequenceCode)
          nmrAtomLabel.setPos(caAtom2.x()-caAtom2.boundingRect().width()/2, caAtom2.y()+30)
          self.scene.addItem(nmrAtomLabel)
          if cBetaAtom is None:
            predictionLabel = QtGui.QGraphicsTextItem()
            predictionLabel.setPlainText('GLY')
            predictionLabel.setPos(caAtom2.x()-caAtom2.boundingRect().width()/2, nmrAtomLabel.y()+30)
            self.scene.addItem(predictionLabel)
            self.predictedStretch.insert(0, 'G')
          else:
            if float(cbShift.value) < 25:
              print('ALA')
              predictionLabel = QtGui.QGraphicsTextItem()
              predictionLabel.setPlainText('ALA')
              predictionLabel.setPos(caAtom2.x()-caAtom2.boundingRect().width()/2, nmrAtomLabel.y()+30)
              self.scene.addItem(predictionLabel)
              self.predictedStretch.insert(0, 'A')
            if float(cbShift.value) > 68:
              print('THR')
              predictionLabel = QtGui.QGraphicsTextItem()
              predictionLabel.setPlainText('THR')
              predictionLabel.setPos(caAtom2.x()-caAtom2.boundingRect().width()/2, nmrAtomLabel.y()+30)
              self.scene.addItem(predictionLabel)
              self.predictedStretch.insert(0, 'T')
            else:
              self.predictedStretch.insert(0, '.')
          newResidue = {'H':hAtom2, "N": nAtom2, "CA":caAtom2, "CB":cbAtom2, "CO":coAtom2}
          self.residuesShown.insert(0, newResidue)

        if direction == 'right':
          oldResidue = self.residuesShown[-1]
          nAtom2 = self.addAtom("N", (oldResidue["CO"].x()+self.atomSpacing+oldResidue["CO"].boundingRect().width()/2, oldResidue["CA"].y()))
          hAtom2 = self.addAtom("H", (nAtom2.x(), nAtom2.y()+self.atomSpacing))
          caAtom2 = self.addAtom("CA", (nAtom2.x()+(nAtom2.x()-oldResidue["CO"].x())-(oldResidue["CO"].boundingRect().width()/2), oldResidue["CO"].y()))
          cbAtom2 = self.addAtom("CB", (caAtom2.x(), caAtom2.y()-self.atomSpacing))
          coAtom2 = self.addAtom("CO", (caAtom2.x()+abs(caAtom2.x()-nAtom2.x()),nAtom2.y()))
          self.scene.addItem(coAtom2)
          self.scene.addItem(caAtom2)
          self.scene.addItem(cbAtom2)
          self.scene.addItem(nAtom2)
          self.scene.addItem(hAtom2)
          self.addAssignmentLine(nAtom2, hAtom2, 'grey', 1.0, 0)
          self.addAssignmentLine(cbAtom2, caAtom2, 'grey', 1.0, 0)
          self.addAssignmentLine(caAtom2, coAtom2, 'grey', 1.0, 0)
          self.addAssignmentLine(nAtom2, oldResidue['CO'], 'grey', 1.0, 0)
          self.addAssignmentLine(nAtom2, caAtom2, 'grey', 1.0, 0)
          nmrAtomLabel = QtGui.QGraphicsTextItem()
          nmrAtomLabel.setPlainText(nmrResidue.sequenceCode)
          nmrAtomLabel.setPos(caAtom2.x()-caAtom2.boundingRect().width()/2, caAtom2.y()+30)
          self.scene.addItem(nmrAtomLabel)
          newResidue = {'H':hAtom2, "N": nAtom2, "CA":caAtom2, "CB":cbAtom2, "CO":coAtom2}
          self.residuesShown.append(newResidue)
      self.residueCount+=1


  def predictSequencePosition(self):
    sequence = ''.join([residue.shortName for residue in self.project.chains[0].residues])
    if len(self.predictedStretch) > 3:
      string = ''.join(self.predictedStretch)
      print(string)
      import re
      matcher = re.search(string, sequence)
      print(matcher.start(), matcher.end())
      newSequenceText = '<div>'+sequence[:matcher.start()]+'<span style="background-color: #000; ' \
                        'color: #FFF; display: inline-block; padding: 0 3px;"><strong>'+sequence[
                        matcher.start():matcher.end()]+'</strong></span>'+sequence[matcher.end():]+'</div>'
      self.project._appBase.mainWindow.sequenceWidget.setText(newSequenceText)
    else:
      print(self.predictedStretch)





  def addAssignmentLine(self, atom1, atom2, colour, width, displacement):

    if atom1.y() > atom2.y() and atom1.x() - atom2.x() == 0:
      x1 = atom1.x() + (atom1.boundingRect().width()/2)
      y1 = atom1.y() + (atom1.boundingRect().height()*0.2)
      x2 = atom2.x() + (atom1.boundingRect().width()/2)
      y2 = atom2.y() + (atom2.boundingRect().height()*0.8)
      newLine = AssignmentLine(x1+displacement, y1, x2+displacement, y2, colour, width)
      self.scene.addItem(newLine)

    elif atom1.y() < atom2.y() and atom1.x() - atom2.x() == 0:
      x1 = atom1.x() + (atom1.boundingRect().width()/2)
      y1 = atom1.y() + (atom1.boundingRect().height()*0.8)
      x2 = atom2.x() + (atom1.boundingRect().width()/2)
      y2 = atom2.y() + (atom2.boundingRect().height()*0.2)
      newLine = AssignmentLine(x1+displacement, y1, x2+displacement, y2, colour, width)
      self.scene.addItem(newLine)

    elif atom1.x() > atom2.x() and atom1.y() - atom2.y() == 0:
      x1 = atom1.x()
      x2 = atom2.x() + atom2.boundingRect().width()
      y1 = atom1.y() + (atom1.boundingRect().height()*0.5)
      y2 = atom2.y() + (atom2.boundingRect().height()*0.5)
      newLine = AssignmentLine(x1, y1+displacement, x2, y2+displacement, colour, width)
      self.scene.addItem(newLine)

    elif atom1.x() < atom2.x() and atom1.y() - atom2.y() == 0:
      x1 = atom1.x() + atom1.boundingRect().width()
      x2 = atom2.x()
      y1 = atom1.y() + (atom1.boundingRect().height()*0.5)
      y2 = atom2.y() + (atom2.boundingRect().height()*0.5)
      newLine = AssignmentLine(x1, y1+displacement, x2, y2+displacement, colour, width)
      self.scene.addItem(newLine)

    elif atom1.y() > atom2.y() and atom1.x() > atom2.x():
      x1 = atom1.x() + (atom1.boundingRect().width()*0.5)
      x2 = atom2.x() + (atom1.boundingRect().width()*1.5)
      y1 = atom1.y() + (atom1.boundingRect().height()/8)
      y2 = atom2.y() + (atom2.boundingRect().height()/2)
      newLine = AssignmentLine(x1, y1+displacement, x2, y2+displacement, colour, width)
      self.scene.addItem(newLine)

    elif atom1.y() < atom2.y() and atom1.x() < atom2.x():
      x1 = atom1.x() + (atom1.boundingRect().width())
      x2 = atom2.x() + (atom1.boundingRect().width()*0.5)
      y1 = atom1.y() + (atom1.boundingRect().height()/2)
      y2 = atom2.y() + (atom2.boundingRect().height()/8)
      newLine = AssignmentLine(x1+displacement, y1+displacement, x2+displacement, y2+displacement, colour, width)
      self.scene.addItem(newLine)

    elif atom1.y() > atom2.y() and atom1.x() < atom2.x():
      x1 = atom1.x() + (atom1.boundingRect().width()*0.5)
      x2 = atom2.x() - (atom1.boundingRect().width()/16)
      y1 = atom1.y() + (atom1.boundingRect().height()/8)
      y2 = atom2.y() + (atom2.boundingRect().height()/2)
      newLine = AssignmentLine(x1+displacement, y1+displacement, x2+displacement, y2+displacement, colour, width)
      self.scene.addItem(newLine)

    elif atom1.y() < atom2.y() and atom1.x() > atom2.x():
      x1 = atom1.x() + (atom1.boundingRect().width())
      x2 = atom2.x() + (atom1.boundingRect().width()*0.25)
      y1 = atom1.y() + (atom1.boundingRect().height()/2)
      y2 = atom2.y() + (atom2.boundingRect().height()/8)
      newLine = AssignmentLine(x1+displacement, y1+displacement, x2+displacement, y2+displacement, colour, width)
      self.scene.addItem(newLine)


  def addAtom(self, atomType, position):
    atom = GuiNmrAtom(text=atomType, pos=position)
    return(atom)

class GuiNmrAtom(QtGui.QGraphicsTextItem):

  def __init__(self, text, pos=None):

    super(GuiNmrAtom, self).__init__()
    self.setPlainText(text)
    self.setPos(QtCore.QPointF(pos[0], pos[1]))
    self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    # self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | self.flags())
    # self.brush = QtGui.QBrush()
    self.setDefaultTextColor(QtGui.QColor('#f7ffff'))
    # self.setBrush(self.brush)
    if self.isSelected:
      # self.setFont(Font(size=17.5, bold=True))
      self.setDefaultTextColor(QtGui.QColor('#bec4f3'))
    else:
      self.setDefaultTextColor(QtGui.QColor('#f7ffff'))
      # self.setBrush(self.brush)


  def hoverEnterEvent(self, event):
    self.setDefaultTextColor(QtGui.QColor('#e4e15b'))

  def hoverLeaveEvent(self, event):
    self.setDefaultTextColor(QtGui.QColor('#f7ffff'))

  def printAtom(self):
    print(self)


class AssignmentLine(QtGui.QGraphicsLineItem):
  def __init__(self, x1, y1, x2, y2, colour, width):
    QtGui.QGraphicsLineItem.__init__(self)
    self.pen = QtGui.QPen()
    self.pen.setColor(QtGui.QColor(colour))
    self.pen.setCosmetic(True)
    self.pen.setWidth(width)
    self.setPen(self.pen)
    self.setLine(x1, y1, x2, y2)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    dialog = Assigner()
    dialog.show()
    dialog.raise_()

    app.exec_()
