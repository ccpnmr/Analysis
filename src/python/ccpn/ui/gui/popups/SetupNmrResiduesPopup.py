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
__dateModified__ = "$dateModified: 2017-07-07 16:32:50 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.popups.Dialog import CcpnDialog      # ejb


class SetupNmrResiduesPopup(CcpnDialog):
  def __init__(self, parent=None, project=None
               , title='Setup nmrResidues', **kw):
    CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

    self.parent = parent
    self.project = project
    label1a = Label(self, text="Source PeakList ", grid=(0, 0))
    self.peakListPulldown = PulldownList(self, grid=(0, 1))
    self.peakListPulldown.setData([peakList.pid for peakList in project.peakLists
      if peakList.spectrum.experimentType == 'H[N]' or peakList.spectrum.experimentType == 'H[N[CO]]'])
    label1a = Label(self, text="NmrChain ", grid=(0, 2))
    self.nmrChainPulldown = PulldownList(self, grid=(0, 3))
    self.nmrChainPulldown.setData([nmrChain.pid for nmrChain in project.nmrChains])
    newWidget = QtWidgets.QWidget()
    newWidget.setLayout(QtWidgets.QGridLayout())
    self.assignmentCheckBox = CheckBox(newWidget, checked=True)
    assignmentLabel = Label(newWidget, "Keep existing assignments")
    newWidget.layout().addWidget(self.assignmentCheckBox, 0, 0)
    newWidget.layout().addWidget(assignmentLabel, 0, 1)
    self.layout().addWidget(newWidget, 1, 0, 1, 2)

    self.buttonBox = ButtonList(self, grid=(1, 3), texts=['Cancel', 'Ok'],
                                callbacks=[self.reject, self._setupNmrResidues])


  def _setupNmrResidues(self):
    # FIXME Why just 15N ?
    self.project._startCommandEchoBlock('_setupNmrResidues')
    try:
      peakList = self.project.getByPid(self.peakListPulldown.currentText())
      nmrChain = self.project.getByPid(self.nmrChainPulldown.currentText())
      keepAssignments = self.assignmentCheckBox.checkState()
      isotopeCodes = peakList.spectrum.isotopeCodes
      axisCodes = peakList.spectrum.axisCodes
      if (isotopeCodes.count('1H') == 1 and isotopeCodes.count('15N') == 1):
        ndim = isotopeCodes.index('15N')
        hdim = isotopeCodes.index('1H')
        for peak in peakList.peaks:
          if not keepAssignments or not any(len(dimensionNmrAtoms) > 0 for dimensionNmrAtoms in peak.dimensionNmrAtoms):
            r = nmrChain.newNmrResidue()
            a = r.fetchNmrAtom(name='N')
            a2 = r.fetchNmrAtom(name='H')
            peak.assignDimension(axisCode=axisCodes[ndim], value=a)
            peak.assignDimension(axisCode=axisCodes[hdim], value=a2)
      else:
        self.project._logger.warning('''Incompatible peak list selected. Only experiments with one 1H dimension
        and one 15N dimension can be used.''')
        return
    finally:
      self.accept()
      self.project._endCommandEchoBlock()
