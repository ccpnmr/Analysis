"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================
from datetime import datetime

from ccpn import AbstractWrapperObject
from ccpn import Project
from ccpncore.api.ccp.lims.Sample import Sample as ApiSample
from ccpncore.util import Pid



class Sample(AbstractWrapperObject):
  """NMR or other sample."""
  
  #: Short class name, for PID.
  shortClassName = 'SA'
  # Attribute it necessary as subclasses must use superclass className
  className = 'Sample'

  #: Name of plural link to instances of class
  _pluralLinkName = 'samples'
  
  #: List of child classes.
  _childClasses = []

  # CCPN properties  
  @property
  def _apiSample(self) -> ApiSample:
    """ CCPN sample matching Sample"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """sample name, corrected to use for id"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def name(self) -> str:
    """actual sample name"""
    return self._wrappedData.name
    
  @property
  def _parent(self) -> Project:
    """Parent (containing) object."""
    return self._project
  
  @property
  def pH(self) -> float:
    """pH of sample"""
    return self._wrappedData.ph
    
  @pH.setter
  def pH(self, value:float):
    self._wrappedData.ph = value

  @property
  def ionicStrength(self) -> float:
    """ionicStrength of sample"""
    return self._wrappedData.ionicStrength

  @ionicStrength.setter
  def ionicStrength(self, value:float):
    self._wrappedData.ionicStrength = value

  @property
  def amount(self) -> float:
    """amount of sample"""
    return self._wrappedData.amount

  @amount.setter
  def amount(self, value:float):
    self._wrappedData.amount = value

  @property
  def amountUnit(self) -> str:
    """amountUnit for sample"""
    return self._wrappedData.amountUnit

  @amountUnit.setter
  def amountUnit(self, value:str):
    self._wrappedData.amountUnit = value

  @property
  def isHazardous(self) -> bool:
    """is sample a hazard?"""
    return self._wrappedData.isHazard

  @isHazardous.setter
  def isHazardous(self, value:bool):
    self._wrappedData.isHazard = value

  @property
  def isVirtual(self) -> bool:
    """is sample virtual? Virtual samples serve as templates and may not be linked to Spectra"""
    return self._wrappedData.isVirtual

  @isVirtual.setter
  def isVirtual(self, value:bool):
    self._wrappedData.isVirtual = value

  @property
  def creationDate(self) -> datetime:
    """Creation timestamp for sample (not for the description record)"""
    return self._wrappedData.creationDate

  @creationDate.setter
  def creationDate(self, value:datetime):
    self._wrappedData.creationDate = value

  @property
  def batchIdentifier(self) -> str:
    """batch identifier for sample"""
    return self._wrappedData.batchNumber

  @batchIdentifier.setter
  def batchIdentifier(self, value:str):
    self._wrappedData.batchNumber = value

  @property
  def plateIdentifier(self) -> str:
    """plate identifier for sample"""
    return self._wrappedData.plateIdentifier

  @plateIdentifier.setter
  def plateIdentifier(self, value:str):
    self._wrappedData.plateIdentifier = value

  @property
  def rowNumber(self) -> str:
    """Row number on plate"""
    return self._wrappedData.rowPosition

  @rowNumber.setter
  def rowNumber(self, value:str):
    self._wrappedData.rowPosition = value

  @property
  def columnNumber(self) -> str:
    """Column number on plate"""
    return self._wrappedData.colPosition

  @columnNumber.setter
  def columnNumber(self, value:str):
    self._wrappedData.colPosition = value
  
  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details
    
  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  # Implementation functions
  def rename(self, value):
    """Rename Sample, changing its Id and Pid"""
    if value:
      self._wrappedData.name = value
    else:
      raise ValueError("Sample name must be set")


  @classmethod
  def _getAllWrappedData(cls, parent:Project)-> list:
    """get wrappedData (Sample.Samples) for all Sample children of parent NmrProject.sampleStore
    Set sampleStore to default if not set"""
    return parent._wrappedData.sampleStore.sortedSamples()


def newSample(self:Project, name:str, pH:float=None, ionicStrength:float=None, amount:float=None,
              amountUnit:str='L', isHazardous:bool=None, creationDate:datetime=None,
              batchIdentifier:str=None, plateIdentifier:str=None, rowNumber:int=None,
              columnNumber:int=None, comment:str=None) -> Sample:
  """Create new child Sample"""
  nmrProject = self._wrappedData
  apiSampleStore =  nmrProject.sampleStore

  newApiSample = apiSampleStore.newSample(name=name, ph=pH, ionicStrength=ionicStrength,
                                          amount=amount, amountUnit=amountUnit,
                                          isHazardous=isHazardous, creationDate=creationDate,
                                          batchIdentifier=batchIdentifier,
                                          plateIdentifier=plateIdentifier,rowPosition=rowNumber,
                                          colPosition=columnNumber, details=comment)
  #
  return self._data2Obj.get(newApiSample)
    
# Connections to parents:
Project._childClasses.append(Sample)
Project.newSample = newSample

# Notifiers:
className = ApiSample._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':Sample}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete'),
    ('_finaliseUnDelete', {}, className, 'undelete'),
    ('_resetPid', {}, className, 'setName'),
  )
)
