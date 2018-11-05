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
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================




#### GUI IMPORTS
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, PipelineDropArea , AutoGeneratedGuiPipe

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import Pipe


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

ReferenceSpectrum = 'referenceSpectrum'
PipeName = 'Auto-Generated GuiPipe Demo'


########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################


def myAlgorithm(data):
    # do something
    return data



########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################

class AutoGeneratedGuiPipeDemo(AutoGeneratedGuiPipe):

  preferredPipe = True
  pipeName = PipeName

  def __init__(self, name=pipeName, parent=None, project=None,  **kwds):
    super(AutoGeneratedGuiPipeDemo, self)
    AutoGeneratedGuiPipe.__init__(self, parent=parent, name=name, project=project,  **kwds)




########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################



class DemoPipe2(Pipe):
  'Demo with autoGenerated gui'

  autoGuiParams = [
                  {'variable':  ReferenceSpectrum,
                   'value':     ('spectrum1', 'spectrum2'),
                   'label':     'Select Spectrum',
                   'default':   'spectrum2'},

                 ]

  _kwargs = {
            ReferenceSpectrum: 'spectrum2',
            }

  guiPipe = AutoGeneratedGuiPipeDemo
  guiPipe.autoGuiParams = autoGuiParams
  pipeName = PipeName

  def runPipe(self, data):
    print(data, self._kwargs)





########################################################################################################################
##########################################      RUN TEST GUI PIPE     ##################################################
########################################################################################################################

if __name__ == '__main__':
  from PyQt5 import QtGui, QtWidgets
  from ccpn.ui.gui.widgets.Application import TestApplication

  app = TestApplication()
  win = QtWidgets.QMainWindow()

  pipeline = PipelineDropArea()
  demoGuiPipe = AutoGeneratedGuiPipeDemo(parent=pipeline)
  pipeline.addDock(demoGuiPipe)


  win.setCentralWidget(pipeline)
  win.resize(1000, 500)
  win.show()

  app.start()



