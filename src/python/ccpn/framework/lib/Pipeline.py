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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:14 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"

__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#====================================



class Pipeline(object):
  '''
  Pipeline class.
  To run insert the pipes in the queue.

  '''


  def __init__(self, application=None, pipelineName=None, pipes=None ):

    self.pipelineName = pipelineName
    self._kwargs = {}



    self.inputData = set()
    self.spectrumGroups = set()
    self.queue = [] # Pipes to be ran
    # self.finishedPipe = [] # Pipes already ran


    if application is not None:
      self.application = application
      self.current = self.application.current
      self.preferences = self.application.preferences
      self.ui = self.application.ui
      self.project = self.application.project
      try:
        self.mainWindow = self.ui.mainWindow
      except AttributeError:
        pass

    if pipes is not None:
      self.pipes = [cls(application=application) for cls in pipes]
    else:
      self.pipes = []

  @property
  def pipes(self):
    return self._pipes

  @pipes.setter
  def pipes(self, pipes):
    '''
    '''

    if pipes is not None:
      allPipes = []
      for pipe in pipes:
          pipe.pipeline = self
          allPipes.append(pipe)
      self._pipes = allPipes
    else:
      self._pipes = []


  def _updateRunArgs(self, arg, value):
    self._kwargs[arg] = value

  def runPipeline(self):
    '''Run all pipes in the specified order '''
    if len(self.queue)>0:
      for pipe in self.queue:
        if pipe is not None:
            pipe.inputData = self.inputData
            pipe.spectrumGroups = self.spectrumGroups
            result = pipe.runPipe(self.inputData)
            self.inputData = result or set()
            # self.queue.remove(pipe)

    return self.inputData


