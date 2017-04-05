"""
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

from typing import Optional
import collections
from ccpnmodel.ccpncore.lib import Util as coreUtil
from ccpn.core.lib import Pid
from ccpnmodel.ccpncore.api.ccp.nmr.NmrConstraint import Data as ApiData
from ccpnmodel.ccpncore.api.ccp.nmr.NmrConstraint import Parameter as ApiParameter
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Project import Project
from ccpn.core.DataSet import DataSet


class Data(AbstractWrapperObject):
  """Object storing links to the data structures (PeakLists, Spectra, StructureEnsembles etc.)
  connected to a given DataSet, and their associated calculation parameters."""
  
  #: Short class name, for PID.
  shortClassName = 'DA'
  # Attribute it necessary as subclasses must use superclass className
  className = 'Data'

  _parentClass = DataSet

  #: Name of plural link to instances of class
  _pluralLinkName = 'data'

  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = ApiData._metaclass.qualifiedName()

  # CCPN properties
  @property
  def _apiData(self) -> ApiData:
    """ CCPN Data object matching Data"""
    return self._wrappedData

  @property
  def _key(self) -> str:
    """id string - name"""
    # return self._wrappedData.name
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def name(self) -> str:
    """name of Data object, used in Pid and to identify the Data object. """
    return self._wrappedData.name
    
  @property
  def _parent(self) -> DataSet:
    """DataSet containing Data."""
    return  self._project._data2Obj[self._wrappedData.nmrConstraintStore]
  
  calculationStep = _parent
  
  @property
  def attachedObjectPid(self) -> Optional[str]:
    """Pid for attached object - used to calculate the attachedObject

    Remains unchanged also if the object pointed to is renamed or deleted, to
    preserve, as far as possible, the original data."""
    return self._wrappedData.attachedObjectPid

  @attachedObjectPid.setter
  def attachedObjectPid(self, value:str):
    self._wrappedData.attachedObjectPid = value

  @property
  def attachedObject(self) -> Optional[AbstractWrapperObject]:
    """attached object - derived from self.attachedObjectPid.

    If no attached object matching attachedObjectPid can be found
    (object has been renamed, deleted, or teh attachedObjectPid is incorrect)
    this attriibute has the value None."""
    ss = self._wrappedData.attachedObjectPid
    if ss:
      return self.getByPid(ss)
    else:
      return None

  @attachedObject.setter
  def attachedObject(self, value:str):
    if value:
      self._wrappedData.attachedObjectPid = value.pid
    else:
      self._wrappedData.attachedObjectPid = None

  @property
  def parameters(self) -> dict:
    """Keyword-value dictionary of parameters.
    NB the value is a copy - modifying it will not modify the actual data.
    Use the setParameter, deleteParameter, clearParameters, and updateParameters
    methods to modify the parameters.

    Dictionary values can be anything that can be exported to JSON,
    including OrderedDict, numpy.ndarray, ccpn.util.Tensor,
    or pandas DataFrame, Series, or Panel"""
    return dict((x.name, x.value) for x in self._wrappedData.parameters)

  def setParameter(self, name:str, value):
    """Add name:value to parameters, overwriting existing entries"""
    apiData = self._wrappedData
    parameter = apiData.findFirstParameter(name=name)
    if parameter is None:
      apiData.newParameter(name=name, value=value)
    else:
      parameter.value = value

  def deleteParameter(self, name:str):
    """Delete parameter named 'name'"""
    apiData = self._wrappedData
    parameter = apiData.findFirstParameter(name=name)
    if parameter is None:
      raise KeyError("No parameter named %s" % name)
    else:
      parameter.delete()

  def clearParameters(self):
    """Delete all parameters"""
    for parameter in self._wrappedData.parameters:
      parameter.delete()

  def updateParameters(self, value:dict):
    """Convenience routine, similar to dict.update().
    Calls self.setParameter(key, value) for each key,value pair in the input."""
    for key,val in value.items():
      self.setParameter(key, val)

  def rename(self, value:str):
    """Rename Data, changing its nmme and Pid"""
    oldName = self.name
    undo = self._project._undo
    self._startCommandEchoBlock('rename', value)
    if undo is not None:
      undo.increaseBlocking()

    try:
      if not value:
        raise ValueError("Data name must be set")
      elif Pid.altCharacter in value:
        raise ValueError("Character %s not allowed in ccpn.Data.name" % Pid.altCharacter)
      else:
        coreUtil._resetParentLink(self._wrappedData, 'data', {'name':value})
        self._finaliseAction('rename')
        self._finaliseAction('change')

    finally:
      self._endCommandEchoBlock()
      if undo is not None:
        undo.decreaseBlocking()

    undo.newItem(self.rename, self.rename, undoArgs=(oldName,),redoArgs=(value,))



  @classmethod
  def _getAllWrappedData(cls, parent:DataSet)-> list:
    """get wrappedData - all Data children of parent NmrConstraintStore"""
    return parent._wrappedData.sortedData()

# Connections to parents:

def _newData(self:DataSet, name:str, attachedObjectPid:str=None,
             attachedObject:AbstractWrapperObject=None) -> Data:
  """Create new Data within DataSet"""

  defaults = {'attachedObjectPid':None}

  project = self.project

  if attachedObject is not None:
    if attachedObjectPid is None:
      attachedObjectPid = attachedObject.pid
    else:
      raise ValueError(
        "Either attachedObject or attachedObjectPid must be None - values were %s and %s"
                      % (attachedObject, attachedObjectPid))

  self._startCommandEchoBlock('newData', name, values={'attachedObjectPid':attachedObjectPid},
                              defaults=defaults, parName='newData')
  try:
    obj = self._wrappedData.newData(name=name, attachedObjectPid=attachedObjectPid)
  finally:
    self._endCommandEchoBlock()
  return project._data2Obj.get(obj)

DataSet.newData = _newData
del _newData

# Notifiers:
# Data change whenever a parameter is created, deleted, or changed
Project._apiNotifiers.extend(
  (
    ('_notifyRelatedApiObject', {'pathToObject':'data', 'action':'change'},
     ApiParameter._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'data', 'action':'change'},
     ApiParameter._metaclass.qualifiedName(), '__init__'),
    ('_notifyRelatedApiObject', {'pathToObject':'data', 'action':'change'},
     ApiParameter._metaclass.qualifiedName(), 'delete'),
  )
)

