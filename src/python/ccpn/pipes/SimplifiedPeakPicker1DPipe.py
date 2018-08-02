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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:39 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-20 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


#### GUI IMPORTS
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.pipes.lib._getNoiseLevel import _getNoiseLevelForPipe
from ccpn.util.Logging import getLogger , _debug3

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

PipeName =  'Peak Detector 1D'

ExcludeRegions   = 'Exclude_Regions'
NoiseThreshold   = 'Noise_Threshold'
NoiseLevelFactor = 'Noise_Level_Factor'
NegativePeaks    = 'Negative_Peaks'

DefaultNoiseThresholdFactor = 1.5
DefaultExcludeRegions = [[0.0, 0.0], [0.0, 0.0]]
DefaultPeakListIndex = -1
########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

# see in ccpn.core.PeakList.py function peakFinder1D

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################




class PeakDetector1DGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName

  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(PeakDetector1DGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    row = 0
    self.pickNegativeLabel = Label(self.pipeFrame, text=NegativePeaks, grid=(row, 0))
    setattr(self, NegativePeaks, CheckBox(self.pipeFrame, text='', checked=True, grid=(row, 1)))

    row += 1
    self.noiseLevelFactorLabel = Label(self.pipeFrame, text=NoiseLevelFactor, grid=(row, 0))
    setattr(self, NoiseLevelFactor, DoubleSpinbox(self.pipeFrame, value=1.5, min=0.01, step=0.1, grid=(row, 1)))




########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class PeakPicker1DPipe(SpectraPipe):

  guiPipe = PeakDetector1DGuiPipe
  pipeName = PipeName

  _kwargs =   {
               ExcludeRegions: DefaultExcludeRegions,
               NoiseLevelFactor: DefaultNoiseThresholdFactor,
               NegativePeaks: True,

              }

  def runPipe(self, spectra):
    '''
    :param data:
    :return:
    '''

    negativePeaks = self._kwargs[NegativePeaks]
    noiseLevelFactor = self._kwargs[NoiseLevelFactor]

    if ExcludeRegions in self.pipeline._kwargs:
      excludeRegions = self.pipeline._kwargs[ExcludeRegions]
    else:
      self._kwargs.update({ExcludeRegions: DefaultExcludeRegions})
      excludeRegions = self._kwargs[ExcludeRegions]

    for spectrum in self.inputData:
      if len(spectrum.peakLists) > 0:
        spectrum.peakLists[DefaultPeakListIndex].peakFinder1D(deltaFactor = noiseLevelFactor,
                                                              ignoredRegions=excludeRegions,
                                                              negativePeaks = negativePeaks)
      else:
        getLogger().warning('Error: PeakList not found for Spectrum: %s. Add a new PeakList first' % spectrum.pid)

    return spectra



PeakPicker1DPipe.register() # Registers the pipe in the pipeline

