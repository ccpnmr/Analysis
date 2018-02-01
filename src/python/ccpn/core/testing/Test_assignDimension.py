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
__dateModified__ = "$dateModified: 2017-07-07 16:32:33 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon1 $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.util import Common as commonUtil


from ccpn.core.testing.WrapperTesting import WrapperTesting


class Test_makeNmrAtom(WrapperTesting):

  # Path of project to load (None for new project)
  projectPath = None

  def test_createNmrAtom_withIsotopeCode(self):
    c = self.project.newNmrChain()
    r = c.newNmrResidue()
    a = r.newNmrAtom(isotopeCode='15N')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(a._apiResonance.isotopeCode, '15N')

  def _test_createNmrAtom_withIsotopeCode(self):
    c = self.project.newNmrChain()
    r = c.newNmrResidue()
    a = r.newNmrAtom(isotopeCode='15N')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(a.isotopeCode, '15N')

  def test_createNmrAtom_withName(self):
    c = self.project.newNmrChain()
    r = c.newNmrResidue()
    a = r.newNmrAtom(name='CA')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(a.name, 'CA')

  def test_fetchNmrAtom(self):
    c = self.project.newNmrChain()
    r = c.newNmrResidue()
    a = r.fetchNmrAtom(name='CB')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(a.name, 'CB')




class Test_chemicalShift(WrapperTesting):

  # Path of project to load (None for new project)
  projectPath = None

  def setUp(self):

    with self.initialSetup():
      spectra = self.loadData('spectra/115.spc')
      self.spectrum = spectra[0] if spectra else None
      if len(self.project.chemicalShiftLists) < 1:
        self.project.newChemicalShiftList()
      c = self.project.newNmrChain()
      r = c.newNmrResidue()
      self.atom = r.newNmrAtom(isotopeCode='15N')
      # NBNB The first shiftList, called 'default' is created automatically
      self.shiftList = self.project.chemicalShiftLists[0]
      self.peakList = self.spectrum.newPeakList() if spectra else None


  def test_assignDimension(self):
    peaks = self.peakList.pickPeaksNd([[7.0, 7.2], [111.75, 112.2]])
    peaks[0].assignDimension(axisCode=commonUtil.axisCodeMatch('N', self.spectrum.axisCodes),
                             value=self.atom)
    # Undo and redo all operations
    self.assertIsNotNone(self.shiftList.getChemicalShift(self.atom.id))
    self.undo.undo()
    self.undo.redo()
    self.assertIsNotNone(self.shiftList.getChemicalShift(self.atom.id))

