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

PipeName =  'Peak Filter ND'

FilterFactor = 'Filter_Factor' # NB Mock Paramater
DeletePeaks    = 'Delete_Peaks' # NB Mock Paramater

DefaultFilterFactor = 5.7
DefaultPeakListIndex = -1
DefaultDeletePeaks = False

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

# This Pipe has not been implemented yet. Gui Mock type only

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################

# This Pipe has not been implemented yet. Gui Mock type only



class PeakFilterNdGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName

  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(PeakFilterNdGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    row = 0
    filterFactorLabel = Label(self.pipeFrame, text=FilterFactor, grid=(row, 0))
    setattr(self, FilterFactor, DoubleSpinbox(self.pipeFrame, value=DefaultFilterFactor, min=0.01, step=0.1, grid=(row, 1)))

    row += 1
    deletePeakLabel = Label(self.pipeFrame, text=DeletePeaks, grid=(row, 0))
    setattr(self, DeletePeaks, CheckBox(self.pipeFrame, text='', checked=True, grid=(row, 1)))

########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################

# This Pipe has not been implemented yet. Gui Mock type only



class PeakFilterNdPipe(SpectraPipe):

  guiPipe = PeakFilterNdGuiPipe
  pipeName = PipeName

  _kwargs =   {
               FilterFactor: DefaultFilterFactor,
               DeletePeaks : DefaultDeletePeaks,
              }

  def runPipe(self, spectra):

    getLogger().warning('%s Has Not Been Implemented Yet' %PipeName)

    return spectra



PeakFilterNdPipe.register() # Registers the pipe in the pipeline

