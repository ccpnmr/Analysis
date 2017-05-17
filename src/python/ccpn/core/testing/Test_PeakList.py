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
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
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

from ccpn.core.testing.WrapperTesting import WrapperTesting


# Properly done version of above
class PeakListCreationTest(WrapperTesting):
  def setUp(self):
    with self.initialSetup():
      self.spectrum = self.project.createDummySpectrum('H')


  def test_newPeakList(self):
    self.assertEqual(len(self.spectrum.peakLists), 1)

    peakList = self.spectrum.newPeakList()

    self.assertEqual(len(self.spectrum.peakLists), 2)
    self.assertEqual(peakList.className, 'PeakList')
    self.assertIs(self.spectrum.peakLists[1], peakList)


  def test_newPeakList_UndoRedo(self):
    peakList = self.spectrum.newPeakList()

    self.assertEqual(len(self.spectrum.peakLists), 2)
    self.undo.undo()
    self.assertEqual(len(self.spectrum.peakLists), 1)

    self.undo.redo()
    self.assertEqual(len(self.spectrum.peakLists), 2)
    self.assertIs(self.spectrum.peakLists[1], peakList)


class PeakListTest2(WrapperTesting):
  # Path of project to load (None for new project
  projectPath = 'CCPN_H1GI_clean_extended.nef'

  singleValueTags = ['isSimulated', 'symbolColour', 'symbolStyle', 'textColour', 'textColour',
                     'title']

  def test_PeakList_copy(self):
    peakList = self.project.getPeakList('3dNOESY-182.3')
    spectrum = peakList.spectrum
    peakList2 = peakList.copyTo(spectrum)

    self.assertEquals(peakList2.serial, 4)
    self.assertEquals(peakList2.comment,
"""Copy of PeakList:3dNOESY-182.3
ARIA2_NOE_Peaks_run1_it8_auto1195328348.86|6|1|2"""
                      )

    for tag in self.singleValueTags:
      self.assertEquals((tag, getattr(peakList, tag)), (tag, getattr(peakList2, tag)))

  def test_PeakList_copy_keyparameters(self):
    peakList = self.project.getPeakList('3dNOESY-182.3')
    spectrum = peakList.spectrum

    params = {
      'title':'ATITLE',
      'comment':'ACOMMENT',
      'symbolStyle':'+',
      'symbolColour':'RED',
      'textColour':'dish',
      'isSimulated':True,
    }
    peakList2 = peakList.copyTo(spectrum, **params)

    self.assertEquals(peakList2.serial, 4)
    self.assertEquals(peakList2.comment, 'ACOMMENT')

    for tag, val in params.items():
      self.assertEquals(val, getattr(peakList2, tag))

  def test_PeakList_copy_exo(self):
    peakList = self.project.getPeakList('3dNOESY-182.3')
    spectrum = self.project.getSpectrum('3dTOCSY-181')
    peakList2 = peakList.copyTo(spectrum)

    self.assertIs(peakList2._parent, spectrum)

    self.assertEquals(peakList2.serial, 2)
    self.assertEquals(peakList2.comment,
"""Copy of PeakList:3dNOESY-182.3
ARIA2_NOE_Peaks_run1_it8_auto1195328348.86|6|1|2"""
                      )

    for tag in self.singleValueTags:
      self.assertEquals((tag, getattr(peakList, tag)), (tag, getattr(peakList2, tag)))




