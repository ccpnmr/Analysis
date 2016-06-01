"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================

import operator
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Project import Project
from ccpn.core.Spectrum import Spectrum
from ccpn.core.PeakList import PeakList
from ccpnmodel.ccpncore.api.ccp.nmr import Nmr
from ccpn.util import Pid
from typing import Tuple, Sequence, List


class ChemicalShiftList(AbstractWrapperObject):
  """Chemical Shift list. A chemical shift list named 'default' is used by default for
   new experiments, and is created if necessary."""
  
  #: Short class name, for PID.
  shortClassName = 'CL'
  # Attribute it necessary as subclasses must use superclass className
  className = 'ChemicalShiftList'

  _parentClass = Project

  #: Name of plural link to instances of class
  _pluralLinkName = 'chemicalShiftLists'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = Nmr.ShiftList._metaclass.qualifiedName()

  def __init__(self, project:Project, wrappedData:Nmr.ShiftList):

    self._wrappedData = wrappedData
    self._project = project
    defaultName = 'Shifts%s' % wrappedData.serial
    self._setUniqueStringKey(wrappedData, defaultName)
    super().__init__(project, wrappedData)

  # CCPN properties  
  @property
  def _apiShiftList(self) -> Nmr.ShiftList:
    """ CCPN ShiftList matching ChemicalShiftList"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """name, regularised as used for id"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def serial(self) -> int:
    """Shift list serial number"""
    return self._wrappedData.serial
    
  @property
  def _parent(self) -> Project:
    """Parent (containing) object."""
    return self._project
  
  @property
  def name(self) -> str:
    """name of ChemicalShiftList. Changing it will rename the ChemicalShiftList"""
    return self._wrappedData.name

  @property
  def unit(self) -> str:
    """Measurement unit of ChemicalShiftList"""
    return self._wrappedData.unit

  @unit.setter
  def unit(self, value:str):
    self._wrappedData.unit = value

  @property
  def autoUpdate(self) -> bool:
    """Automatically update Chemical Shifts from assigned peak - yes/no??"""
    return self._wrappedData.autoUpdate

  @autoUpdate.setter
  def autoUpdate(self, value:bool):
    self._wrappedData.autoUpdate = value

  @property
  def isSimulated(self) -> bool:
    """
    is ChemicalShiftList simulated?"""
    return self._wrappedData.isSimulated

  @isSimulated.setter
  def isSimulated(self, value:bool):
    self._wrappedData.isSimulated = value
  
  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details
    
  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  @property
  def spectra(self) -> Tuple[Spectrum, ...]:
    """ccpn.Spectra that use ChemicalShiftList to store chemical shifts"""
    ff = self._project._data2Obj.get
    return tuple(ff(y) for x in self._wrappedData.sortedExperiments()
                 for y in x.sortedDataSources())

  @spectra.setter
  def spectra(self, value:Sequence[Spectrum]):
    self._wrappedData.experiments =  set(x._wrappedData.experiment for x in value)
    
  # Implementation functions
  def rename(self, value:str):
    """Rename ChemicalShiftList, changing Id and Pid of ChemicalShiftList"""
    if not value:
      raise ValueError("ChemicalShiftList name must be set")

    elif Pid.altCharacter in value:
      raise ValueError("Character %s not allowed in ccpn.ChemicalShiftList.name" % Pid.altCharacter)

    else:
      self._wrappedData.name = value

  @classmethod
  def _getAllWrappedData(cls, parent: Project)-> List[Nmr.ShiftList]:
    """get wrappedData (ShiftLists) for all ShiftList children of parent Project"""
    return sorted((x for x in parent._apiNmrProject.measurementLists
            if x.className == 'ShiftList'), key=operator.attrgetter('name'))

# Connections to parents:

def getter(self:Spectrum) -> ChemicalShiftList:
  return self._project._data2Obj.get(self._apiDataSource.experiment.shiftList)
def setter(self:Spectrum, value:ChemicalShiftList):
  value = self.getByPid(value) if isinstance(value, str) else value
  self._apiDataSource.experiment.shiftList = value._apiShiftList
Spectrum.chemicalShiftList = property(getter, setter, None,
                          "ccpn.ChemicalShiftList used for ccpn.Spectrum")

def getter(self:PeakList) -> ChemicalShiftList:
  return self._project._data2Obj.get(self._wrappedData.shiftList)
def setter(self:PeakList, value:ChemicalShiftList):
  value = self.getByPid(value) if isinstance(value, str) else value
  self._apiPeakList.shiftList = None if value is None else value._apiShiftList
PeakList.chemicalShiftList = property(getter, setter, None,
                                      "ChemicalShiftList associated with PeakList.")
del getter
del setter

def _newChemicalShiftList(self:Project, name:str=None, unit:str='ppm',
                          isSimulated:bool=False, comment:str=None) -> ChemicalShiftList:
  """Create new ccpn.ChemicalShiftList"""

  if name and Pid.altCharacter in name:
    raise ValueError("Character %s not allowed in ccpn.ChemicalShiftList.name" % Pid.altCharacter)

  obj = self._wrappedData.newShiftList(name=name, unit=unit, isSimulated=isSimulated,
                                       details=comment)
  return self._data2Obj.get(obj)

Project.newChemicalShiftList = _newChemicalShiftList
del _newChemicalShiftList

# Notifiers
className = Nmr.ShiftList._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_finaliseApiRename', {}, className, 'setName'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'Spectrum')}, className, 'addExperiment'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'Spectrum')}, className,
     'removeExperiment'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'Spectrum')}, className, 'setExperiments'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'PeakList')}, className, 'addPeakList'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'PeakList')}, className, 'removePeakList'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'PeakList')}, className, 'setPeakLists'),
  )
)
Project._apiNotifiers.append(('_modifiedLink', {'classNames':('ChemicalShiftList', 'PeakList')},
                              Nmr.PeakList._metaclass.qualifiedName(), 'setSpecificShiftList')
                             )
className = Nmr.Experiment._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_modifiedLink', {'classNames':('ChemicalShiftList', 'Spectrum')},className, 'setShiftList'),
    ('_modifiedLink', {'classNames':('ChemicalShiftList', 'PeakList')},className, 'setShiftList'),
  )
)
