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
__dateModified__ = "$dateModified: 2017-04-07 11:41:08 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.util.Undo import Undo
# from ccpnmodel.ccpncore.lib.Io import Api as apiIo
from ccpnmodel.ccpncore.testing.CoreTesting import CoreTesting

class PeakUndoTest(CoreTesting):

  # Path of project to load (None for new project)
  projectPath = 'CcpnCourse1b'
    
  def test_new_peak_undo(self):
    
    project = self.project
    nmrProject = project.currentNmrProject or project.findFirstNmrProject()
    experiment = nmrProject.findFirstExperiment(name='HSQC')
    dataSource = experiment.findFirstDataSource(name='HSQC-115')
    peakList = dataSource.newPeakList()
    
    project._undo = undo = Undo()
    undo.newWaypoint()
    peak = peakList.newPeak()
    undo.undo()
    assert len(peakList.peaks) == 0, 'len(peakList.peaks) = %d' % len(peakList.peaks)
    
  def test_new_peak_undo_redo(self):
    
    project = self.project
    nmrProject = project.currentNmrProject or project.findFirstNmrProject()
    experiment = nmrProject.findFirstExperiment(name='HSQC')
    dataSource = experiment.findFirstDataSource(name='HSQC-115')
    peakList = dataSource.newPeakList()

    project._undo = undo = Undo()
    undo.newWaypoint()
    peak = peakList.newPeak()
    undo.undo()
    undo.redo()
    assert len(peakList.peaks) == 1, 'len(peakList.peaks) = %d' % len(peakList.peaks)
    
 
