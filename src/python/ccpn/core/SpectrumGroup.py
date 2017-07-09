"""
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:30 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from typing import Tuple

from ccpn.core.Project import Project
from ccpn.core.Spectrum import Spectrum
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.lib import Pid
from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import DataSource as ApiDataSource
from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import SpectrumGroup as ApiSpectrumGroup
from ccpnmodel.ccpncore.lib import Util as coreUtil


class SpectrumGroup(AbstractWrapperObject):
  """Combines multiple Spectrum objects into a group, so they can be treated as a single object.
"""
  
  #: Short class name, for PID.
  shortClassName = 'SG'
  # Attribute it necessary as subclasses must use superclass className
  className = 'SpectrumGroup'

  _parentClass = Project

  #: Name of plural link to instances of class
  _pluralLinkName = 'spectrumGroups'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = ApiSpectrumGroup._metaclass.qualifiedName()
  

  # CCPN properties  
  @property
  def _apiSpectrumGroup(self) -> ApiSpectrumGroup:
    """ CCPN Project SpectrumGroup"""
    return self._wrappedData

  @property
  def _key(self) -> str:
    """Residue local ID"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def name(self) -> str:
    """Name of SpectrumGroup, part of identifier"""
    return self._wrappedData.name

  @property
  def serial(self) -> str:
    """Serial number  of SpectrumGroup, used for sorting"""
    return self._wrappedData.serial

  @property
  def _parent(self) -> Project:
    """Parent (containing) object."""
    return self._project


  @property
  def spectra(self) -> Tuple[Spectrum, ...]:
    """Spectra that make up SpectrumGroup."""
    data2Obj = self._project._data2Obj
    return tuple(sorted(data2Obj[x] for x in self._wrappedData.dataSources))

  @spectra.setter
  def spectra(self, value):
    getDataObj = self._project._data2Obj.get
    value = [getDataObj(x) if isinstance(x,str) else x for x in value]
    self._wrappedData.dataSources = [x._wrappedData for x in value]

  # Implementation functions
  def rename(self, value:str):
    """Rename SpectrumGroup, changing its name and Pid"""
    oldName = self.name
    self._startCommandEchoBlock('rename', value)
    undo = self._project._undo
    if undo is not None:
      undo.increaseBlocking()

    try:
      if not value:
        raise ValueError("SpectrumGroup name must be set")
      elif Pid.altCharacter in value:
        raise ValueError("Character %s not allowed in ccpn.SpectrumGroup.name" % Pid.altCharacter)
      else:
        self._wrappedData.__dict__['name'] = value
        # coreUtil._resetParentLink(self._wrappedData, 'spectrumGroups', {'name':value})
        self._finaliseAction('rename')
        self._finaliseAction('change')

    finally:
      if undo is not None:
        undo.decreaseBlocking()
      self._endCommandEchoBlock()

    undo.newItem(self.rename, self.rename, undoArgs=(oldName,),redoArgs=(value,))

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:Project)-> list:
    """get wrappedData for all SpectrumGroups linked to NmrProject"""
    return parent._wrappedData.sortedSpectrumGroups()


def _newSpectrumGroup(self:Project, name:str, spectra=()) -> SpectrumGroup:
  """Create new SpectrumGroup"""

  if name and Pid.altCharacter in name:
    raise ValueError("Character %s not allowed in ccpn.SpectrumGroup.name" % Pid.altCharacter)

  if spectra:
    getByPid = self._project.getByPid
    spectra = [getByPid(x) if isinstance(x, str) else x for x in spectra]
    values = {'spectra':tuple(x.pid for x in spectra)}
  else:
    values = {}

  self._startCommandEchoBlock('newSpectrumGroup', name, values=values,
                              parName='newSpectrumGroup')
  self._project.blankNotification()
  try:
    result =  self._data2Obj.get(self._wrappedData.newSpectrumGroup(name=name))
    if spectra:
      result.spectra = spectra
  finally:
    self._endCommandEchoBlock()
    self._project.unblankNotification()

  # DO creation notifications
  result._finaliseAction('create')
  return result
    
# Connections to parents:
Project.newSpectrumGroup = _newSpectrumGroup
del _newSpectrumGroup


# reverse link Spectrum.spectrumGroups
def getter(self:Spectrum) -> Tuple[SpectrumGroup, ...]:
  data2Obj = self._project._data2Obj
  return tuple(sorted(data2Obj[x] for x in self._wrappedData.spectrumGroups))
def setter(self:Spectrum, value):
  self._wrappedData.spectrumGroups = [x._wrappedData for x in value]
#
Spectrum.spectrumGroups = property(getter, setter, None,
                                   "SpectrumGroups that contain Spectrum")
del getter
del setter

# Extra Notifiers to notify changes in Spectrum-SpectrumGroup link
className = ApiSpectrumGroup._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'addDataSource'),
    ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'removeDataSource'),
    ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'setDataSources'),
  )
)
className = ApiDataSource._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'addSpectrumGroup'),
    ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'removeSpectrumGroup'),
    ('_modifiedLink', {'classNames':('Spectrum','SpectrumGroup')}, className, 'setSpectrumGroups'),
  )
)
