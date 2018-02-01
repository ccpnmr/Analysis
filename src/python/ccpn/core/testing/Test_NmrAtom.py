"""Test code for NmrResidue

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
__dateModified__ = "$dateModified: 2017-07-07 16:32:33 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.core.testing.WrapperTesting import WrapperTesting

class NmrAtomTest(WrapperTesting):

  # Path of project to load (None for new project
  projectPath = 'CcpnCourse2c'

  def test_reassign1(self):

    nchain = self.project.getByPid('NC:A')

    arg11 = self.project.getByPid('NR:A.11.ARG')
    atomN = arg11.fetchNmrAtom('N')
    self.assertEqual(atomN.pid, 'NA:A.11.ARG.N')

    atomNE = self.project._produceNmrAtom('NA:A.11.ARG.NE')
    atomNE2 = self.project._produceNmrAtom(chainCode='A', sequenceCode='11', name='NE')
    self.assertIs(atomNE, atomNE2)

    atomCX = self.project._produceNmrAtom('NA:A.11.ARG.CX')
    atomNX = arg11.newNmrAtom(name='NX')
    with self.assertRaises(ValueError):
      atomCX.rename('NX')

    atomCX.rename('CZ')
    self.assertEqual(atomCX.pid, 'NA:A.11.ARG.CZ')

    atomCX = atomCX.assignTo(chainCode='A', sequenceCode='888')
    self.assertEqual(atomCX.pid, 'NA:A.888.ARG.CZ')

    atomCX = atomCX.assignTo()
    self.assertEqual(atomCX.pid, 'NA:A.888.ARG.CZ')

    atomCX.rename()
    self.assertEqual(atomCX.pid, 'NA:A.888.ARG.C@198')

    self.project._wrappedData.root.checkAllValid(complete=True)


    with self.assertRaises(ValueError):
      atomCX = self.project._produceNmrAtom('NA:A.11.VAL.CX')

    self.assertEqual(atomCX.pid, 'NA:A.888.ARG.C@198')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(atomCX.pid, 'NA:A.888.ARG.C@198')

  def test_produce_reassign(self):
    at0 = self.project._produceNmrAtom(name='HX')
    self.assertEqual(at0.id,'@-.@89..HX')
    at1 = self.project._produceNmrAtom('X.101.VAL.N')
    self.assertEqual(at1.id,'X.101.VAL.N')
    at1 = at1.assignTo(name='NE')
    self.assertEqual(at1.id,'X.101.VAL.NE')
    at0 = at0.assignTo(sequenceCode=101)
    self.assertEqual(at0.id,'@-.101..HX')
    # Undo and redo all operations
    self.undo.undo()
    self.undo.redo()
    self.assertEqual(at0.id,'@-.101..HX')
    self.assertEqual(at1.id,'X.101.VAL.NE')
