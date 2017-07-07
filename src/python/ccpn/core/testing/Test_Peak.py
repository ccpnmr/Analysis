"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================

__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-04-10 12:56:46 +0100 (Mon, April 10, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from ccpn.util import Common as commonUtil
from ccpn.core.testing.WrapperTesting import WrapperTesting


class PeakTest(WrapperTesting):

  # Path of project to load (None for new project
  projectPath = 'CcpnCourse1b'
    
  def test_assignPeak(self):
    spectrum = self.project.getSpectrum('HSQC-115')
    shiftList = self.project.newChemicalShiftList()
    spectrum.chemicalShiftList = shiftList
    nmrResidue = self.project.nmrChains[0].fetchNmrResidue()
    nmrAtom = nmrResidue.fetchNmrAtom(name='N')
    peak = spectrum.peakLists[0].peaks[0]

    peak.assignDimension(axisCode=commonUtil.axisCodeMatch('N', spectrum.axisCodes),
                         value=nmrAtom)
    # shift = shiftList.findChemicalShift(nmrAtom)
    shift = shiftList.getChemicalShift(nmrAtom.id)
    # print("NewChemicalShift", shift, shift and shift.value)
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertTrue(shift is not None)
    self.assertTrue(shift.value is not None)
    self.project._wrappedData.root.checkAllValid(complete=True)


class PeakTest2(WrapperTesting):
  # Path of project to load (None for new project
  projectPath = 'CCPN_H1GI_clean_extended.nef'

  singleValueTags = ['height', 'volume', 'heightError', 'volumeError', 'figureOfMerit',
                     'annotation', 'comment']
  dimensionValueTags = ['position', 'positionError', 'boxWidths', 'lineWidths', 'assignedNmrAtoms']

  # NBNB TODO We still need a case where axisCodes are not in the same order (e.g. HNC<->HCN)



  def test_Peak_copy_exo_1(self):
    peakList1 = self.project.getPeakList('3dNOESY-182.3')
    peak1 = peakList1.getPeak(1110)
    peak2 = peak1.copyTo(peakList1)

    self.project._wrappedData.root.checkAllValid(complete=True)

    self.assertIs(peak1._parent, peakList1)
    self.assertIs(peak2._parent, peakList1)

    tags = self.singleValueTags + self.dimensionValueTags

    for tag in tags:
      self.assertEquals((tag, getattr(peak1, tag)), (tag, getattr(peak2, tag)))
    self.assertEquals(('serial', peak2.serial), ('serial', 1131))


  def test_Peak_copy_exo_2(self):
    peakList1 = self.project.getPeakList('3dNOESY-182.3')
    peakList2 = self.project.getPeakList('3dTOCSY-181.1')
    peak1 = peakList1.getPeak(1110)
    peak3 = peak1.copyTo(peakList2)

    tags = self.singleValueTags + self.dimensionValueTags

    self.assertIs(peak1._parent, peakList1)
    self.assertIs(peak3._parent, peakList2)

    for tag in tags:
      self.assertEquals((tag, getattr(peak1, tag)), (tag, getattr(peak3, tag)))
    self.assertEquals(('serial', peak1.serial), ('serial', peak3.serial))


