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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


#### GUI IMPORTS
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe , _getWidgetByAtt
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.pipes.lib._new1Dspectrum import _create1DSpectrum
########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys


## defaults
ReplaceInputData = 'Replace_Input_Data'
DefaultReplaceInputData  = False


## PipeName
PipeName = 'Duplicate Spectra'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################



########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class DuplicateSpectrumGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName
  _alreadyOpened = False


  def __init__(self, name=pipeName, parent=None, project=None, **kw):
    super(DuplicateSpectrumGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent
    DuplicateSpectrumGuiPipe._alreadyOpened = True

    row = 0
    tipText = 'Use the duplicated spectra as new inputData and remove the original spectra from the pipeline.'
    self.replaceInputDataLabel = Label(self.pipeFrame, text=ReplaceInputData, grid=(row, 0))
    setattr(self, ReplaceInputData, CheckBox(self.pipeFrame, text='', checked=DefaultReplaceInputData, tipText=tipText,
                                             grid=(row, 1)))

  def _updateWidgets(self):
    pass


  def _closeBox(self):
    'reset alreadyOpened flag '
    DuplicateSpectrumGuiPipe._alreadyOpened = False
    self.closeBox()




########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class DuplicateSpectrumPipe(SpectraPipe):

  guiPipe = DuplicateSpectrumGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                ReplaceInputData:DefaultReplaceInputData
               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: new spectra
    '''
    newSpectra = set()
    for spectrum in spectra:
      newspectrum = spectrum._clone()
      newSpectra.update([newspectrum])

    replaceInputData = self._kwargs[ReplaceInputData]
    if replaceInputData:
      self.pipeline.inputData = newSpectra
      return newSpectra
    else:
      spectra = set(spectra)
      spectra.update(newSpectra)
      return spectra

DuplicateSpectrumPipe.register() # Registers the pipe in the pipeline


