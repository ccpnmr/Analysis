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
__dateModified__ = "$dateModified: 2017-07-07 16:32:28 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import collections
import operator
from typing import Union, Tuple

from ccpn.core.Residue import Residue
from ccpn.core.Atom import Atom
from ccpn.core.NmrResidue import NmrResidue
from ccpn.core.Peak import Peak
from ccpn.core.Project import Project
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.lib import Pid
from ccpn.core.lib.Util import AtomIdTuple
from ccpnmodel.ccpncore.api.ccp.nmr import Nmr
from ccpnmodel.ccpncore.lib import Constants
from ccpnmodel.ccpncore.lib import Util as modelUtil
from ccpn.util.Common import name2IsotopeCode


class NmrAtom(AbstractWrapperObject):
  """NmrAtom objects are used for assignment. An NmrAtom within an assigned NmrResidue is
  by definition assigned to the Atom with the same name (if any).

  NmrAtoms serve as a way of connecting a named nucleus to an observed chemical shift,
  and peaks are assigned to NmrAtoms. Renaming an NmrAtom (or its containing NmrResidue or
  NmrChain) automatically updates peak assignments and ChemicalShifts that use the NmrAtom,
  preserving the link.

  NmrAtom names must start with the atom type, ('H' for proton, 'D' for deuterium, 'C' for
  carbon, etc.), with '?' for 'unknown."""

  
  #: Short class name, for PID.
  shortClassName = 'NA'
  # Attribute it necessary as subclasses must use superclass className
  className = 'NmrAtom'

  _parentClass = NmrResidue

  #: Name of plural link to instances of class
  _pluralLinkName = 'nmrAtoms'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = Nmr.Resonance._metaclass.qualifiedName()

  # CCPN properties  
  @property
  def _apiResonance(self) -> Nmr.Resonance:
    """ CCPN atom matching Atom"""
    return self._wrappedData


  @property
  def _parent(self) -> NmrResidue:
    """Parent (containing) object."""
    return self._project._data2Obj[self._wrappedData.resonanceGroup]
  
  nmrResidue = _parent
    
  @property
  def _key(self) -> str:
    """Atom name string (e.g. 'HA') regularised as used for ID"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def _localCcpnSortKey(self) -> Tuple:
    """Local sorting key, in context of parent."""

    # We want sorting by name, even though Resonances have serials
    return (self._key,)


  @property
  def _idTuple(self) -> AtomIdTuple:
    """ID as chainCode, sequenceCode, residueType, atomName namedtuple
    NB Unlike the _id and key, these do NOT have reserved characters mapped to '^'
    NB _idTuple replaces empty strings with None"""
    parent = self._parent
    ll = [parent._parent.shortName, parent.sequenceCode, parent.residueType, self.name]
    return AtomIdTuple(*(x or None for x in ll))


  @property
  def name(self) -> str:
    """Atom name string (e.g. 'HA')"""
    return self._wrappedData.name

  @property
  def serial(self) -> int:
    """NmrAtom serial number - set at creation and unchangeable"""
    return self._wrappedData.serial

  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details

  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  @property
  def atom(self) -> Atom:
    """Atom to which NmrAtom is assigned. NB resetting the atom will rename the NmrAtom"""
    return self._project.getAtom(self._id)

  @atom.setter
  def atom(self, value:Atom):
    if value is None:
      self.deassign()
    else:
      self._wrappedData.atom = value._wrappedData

  @property
  def isotopeCode(self) -> str:
    """isotopeCode of NmrAtom. Set automatically on creation (from NmrAtom name)
    and cannot be changed later"""
    return self._wrappedData.isotopeCode

  @property
  def boundNmrAtoms(self) -> 'NmrAtom':
    """NmrAtoms directly bound to this one, as calculated from assignment and
    NmrAtom name matches (NOT from peak assignment)"""
    getDataObj = self._project._data2Obj.get
    ll = self._wrappedData.getBoundResonances()
    result = [getDataObj(x) for x in ll]

    nmrResidue = self.nmrResidue
    if nmrResidue.residue is None:
        # NmrResidue is unassigned. Add ad-hoc protein interresidue bonds
      if self.name == 'N':
        for rx in (nmrResidue.previousNmrResidue, nmrResidue.getOffsetNmrResidue(-1)):
          if rx is not None:
            na = rx.getNmrAtom('C')
            if na is not None:
              result.append(na)
      elif self.name == 'C':
        for rx in (nmrResidue.nextNmrResidue, nmrResidue.getOffsetNmrResidue(1)):
          if rx is not None:
            na = rx.getNmrAtom('N')
            if na is not None:
              result.append(na)
    #
    return result


  @property
  def assignedPeaks(self) -> Tuple[Peak]:
    """All Peaks assigned to the NmrAtom"""
    apiResonance = self._wrappedData
    apiPeaks = [x.peakDim.peak for x in apiResonance.peakDimContribs]
    apiPeaks.extend([x.peakDim.peak for x in apiResonance.peakDimContribNs])

    data2Obj = self._project._data2Obj
    return sorted(data2Obj[x] for x in set(apiPeaks))

  def rename(self, value:str=None):
    """Rename the NmrAtom, changing its name, Pid, and internal representation."""

    # NBNB TODO change so you can set names of the form '@123' (?)

    # NB This is a VERY special case
    # - API code and notifiers will take care of resetting id and Pid
    self._startCommandEchoBlock('rename', value)
    try:
      if value is None:
        self.deassign()

      else:
        if Pid.altCharacter in value:
          raise ValueError("Character %s not allowed in ccpn.NmrAtom.name" % Pid.altCharacter)

        isotopeCode = self._wrappedData.isotopeCode
        newIsotopeCode = name2IsotopeCode(value)
        if newIsotopeCode is not None:
          if isotopeCode == '?':
            self._wrappedData.isotopeCode = newIsotopeCode
          elif newIsotopeCode != isotopeCode:
            raise ValueError("Cannot rename %s type NmrAtom to %s" % (isotopeCode, value))
        #
        self._wrappedData.name = value
    finally:
      self._endCommandEchoBlock()

  def deassign(self):
    """Reset NmrAtom back to its originalName, cutting all assignment links"""
    self._startCommandEchoBlock('deassign')
    try:
      self._wrappedData.name = None
    finally:
      self._endCommandEchoBlock()

  def assignTo(self, chainCode:str=None, sequenceCode:Union[int,str]=None,
               residueType:str=None, name:str=None, mergeToExisting=False) -> 'NmrAtom':
    """Assign NmrAtom to naming parameters) and return the reassigned result

    If the assignedTo NmrAtom already exists the function raises ValueError.
    If mergeToExisting is True it instead merges the current NmrAtom into the target
    and returns the merged target. NB Merging is NOT undoable

    WARNING: is mergeToExisting is True, always use in the form "x = x.assignTo(...)",
    as the call 'x.assignTo(...) may cause the source x object to be deleted.

    Passing in empty parameters (e.g. chainCode=None) leaves the current value unchanged. E.g.:
    for NmrAtom NR:A.121.ALA.HA calling with sequenceCode=124 will assign to
    (chainCode='A', sequenceCode=124, residueType='ALA', atomName='HA')


    The function works as:

    nmrChain = project.fetchNmrChain(shortName=chainCode)

    nmrResidue = nmrChain.fetchNmrResidue(sequenceCode=sequenceCode, residueType=residueType)

    (or nmrChain.fetchNmrResidue(sequenceCode=sequenceCode) if residueType is None)
    """

    # Get parameter string for console echo - before parameters are changed
    defaults = collections.OrderedDict(
      (('chainCode', None), ('sequenceCode', None),
       ('residueType', None), ('name', None), ('mergeToExisting', False)
      )
    )

    oldPid = self.longPid
    clearUndo = False
    undo = self._apiResonance.root._undo
    apiResonance = self._apiResonance
    apiResonanceGroup = apiResonance.resonanceGroup

    self._startCommandEchoBlock('assignTo', values=locals(), defaults=defaults)
    try:
      if sequenceCode is not None:
        sequenceCode = str(sequenceCode) or None

      # set missing parameters to existing values
      chainCode = chainCode or apiResonanceGroup.nmrChain.code
      sequenceCode = sequenceCode or apiResonanceGroup.sequenceCode
      residueType = residueType or apiResonanceGroup.residueType
      name = name or apiResonance.name

      for ss in chainCode, sequenceCode, residueType, name:
        if ss and Pid.altCharacter in ss:
          raise ValueError("Character %s not allowed in ccpn.NmrAtom id : %s.%s.%s.%s"
                           % (Pid.altCharacter, chainCode, sequenceCode, residueType, name))

      isotopeCode = self.isotopeCode
      if name and isotopeCode not in (None, '?'):
        # Check for isotope match
        if name2IsotopeCode(name) not in (isotopeCode, None):
          raise ValueError("Cannot reassign %s type NmrAtom to %s" % (isotopeCode, name))


      oldNmrResidue = self.nmrResidue
      nmrChain = self._project.fetchNmrChain(chainCode)
      if residueType:
        nmrResidue = nmrChain.fetchNmrResidue(sequenceCode, residueType)
      else:
        nmrResidue = nmrChain.fetchNmrResidue(sequenceCode)

      if name:
        # result is matching NmrAtom, or (if None) self
        result = nmrResidue.getNmrAtom(name) or self
      else:
        # No NmrAtom can match, result is self
        result = self

      if nmrResidue is oldNmrResidue:
        if name != self.name:
          # NB self.name can never be returned as None

          if result is self:
            self._wrappedData.name = name or None

          elif mergeToExisting:
            clearUndo = True
            result._wrappedData.absorbResonance(self._apiResonance)
            self._project._logger.warning("Merging (1) %s into %s. Merging is NOT undoable."
                                        % (oldPid, result.longPid))

          else:
            raise ValueError("New assignment clash with existing assignment,"
                             " and merging is disallowed")

      else:

        if result is self:
          if nmrResidue.getNmrAtom(self.name) is None:
            self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
            if name != self.name:
              self._wrappedData.name = name or None
          elif name is None or oldNmrResidue.getNmrAtom(name) is None:
            if name != self.name:
              self._wrappedData.name = name or None
            self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
          else:
            self._wrappedData.name = None  # Necessary to avoid name clashes
            self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
            self._wrappedData.name = name

        elif mergeToExisting:
          # WARNING if we get here undo is no longer possible
          clearUndo = True
          result._wrappedData.absorbResonance(self._apiResonance)
          self._project._logger.warning("Merging (2) %s into %s. Merging is NOT undoable."
                                        % (oldPid, result.longPid))
        else:
          raise ValueError("New assignment clash with existing assignment,"
                           " and merging is disallowed")
      #
      if undo is not None and clearUndo:
        undo.clear()
    finally:
      self._endCommandEchoBlock()
    #
    return result

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent: NmrResidue)-> list:
    """get wrappedData (ApiResonance) for all NmrAtom children of parent NmrResidue"""
    return parent._wrappedData.sortedResonances()

def getter(self:Atom) -> NmrAtom:
  return self._project.getNmrAtom(self._id)

def setter(self:Atom, value:NmrAtom):
  oldValue = self.nmrAtom
  if oldValue is value:
    return
  elif value is None:
    raise ValueError("Cannot set Atom.nmrAtom to None")
  elif oldValue is not None:
    raise ValueError("New assignment of Atom clashes with existing assignment")
  else:
    value.atom = self
Atom.nmrAtom = property(getter, setter, None, "NmrAtom to which Atom is assigned")


def getter(self: Residue) -> Tuple[NmrAtom]:
  result = []
  for nmrResidue in self.allNmrResidues:
    result.extend(nmrResidue.nmrAtoms)
  #
  return tuple(result)
Residue.allNmrAtoms = property(getter, None, None,
                                  "All NmrAtoms corresponding to Residue - E.g. (for MR:A.87)"
                                  " NmrAtoms in NR:A.87, NR:A.87+0, NR:A.88-1, NR:A.82+5, etc.")

del getter
del setter
    
def _newNmrAtom(self:NmrResidue, name:str=None, isotopeCode:str=None,
                comment:str=None) -> NmrAtom:
  """Create new NmrAtom within NmrResidue. If name is None, use default name
  (of form e.g. 'H@211', 'N@45', ...)"""
  nmrProject = self._project._wrappedData
  resonanceGroup = self._wrappedData

  defaults = collections.OrderedDict((('name', None), ('isotopeCode', None)))

  # Set isotopeCode if empty
  if not isotopeCode:
    if name:
      isotopeCode = name2IsotopeCode(name) or '?'
    else:
      isotopeCode = '?'

  # Deal with reserved names
  serial = None
  if name:
    # Check for name clashes

    previous = self.getNmrAtom(name.translate(Pid.remapSeparators))
    if previous is not None:
      raise ValueError("%s already exists" % previous.longPid)

    # Deal with reserved names
    index = name.find('@')
    if index >= 0:
      try:
        serial = int(name[index+1:])
        obj = nmrProject.findFirstResonance(serial=serial)
      except ValueError:
        obj = None
      if obj is not None:
        previous = self._project._data2Obj[obj]
        if '@' in obj.name:
          # Two NmrAtoms both with same @serial. Error
          raise ValueError("Cannot create NmrAtom:%s.%s - reserved atom name clashes with %s"
                           % (self._id, name, previous.longPid))
        else:
          # We can renumber obj to free the serial for the new NmrAtom
          newSerial = obj.parent._serialDict['resonances'] + 1
          try:
            previous.resetSerial(newSerial)
            # modelUtil.resetSerial(obj, newSerial, 'resonances')
          except ValueError:
            self.project._logger.warning(
              "Could not reset serial of %s to %s - keeping original value" %(previous, serial)
            )
          previous._finaliseAction('rename')

  dd = {'resonanceGroup':resonanceGroup, 'isotopeCode':isotopeCode}
  if serial is None:
    dd['name'] = name
  if comment is None:
    dd['details'] = name

  self._startCommandEchoBlock('newNmrAtom', values=locals(), defaults=defaults,
                              parName='newNmrAtom')
  result = None
  try:
    obj = nmrProject.newResonance(**dd)
    result = self._project._data2Obj.get(obj)
    if serial is not None:
      try:
        result.resetSerial(serial)
        # modelUtil.resetSerial(obj, serial, 'resonances')
      except ValueError:
        self.project._logger.warning(
          "Could not set (reserved) name of %s to %s - set to %s instead"
                                     %(result, name, result.name))
      result._finaliseAction('rename')
  finally:
    self._endCommandEchoBlock()
  #
  return result

def _fetchNmrAtom(self:NmrResidue, name:str):
  """Fetch NmrAtom with name=name, creating it if necessary"""
  # resonanceGroup = self._wrappedData
  self._startCommandEchoBlock('fetchNmrAtom', name, parName='newNmrAtom')
  try:
    # self.getNmrAtom(name.translate(Pid.remapSeparators))
    result = (self.getNmrAtom(name.translate(Pid.remapSeparators)) or
              self.newNmrAtom(name=name))
    # result = (self._project._data2Obj.get(resonanceGroup.findFirstResonance(name=name)) or
    #         self.newNmrAtom(name=name))
  finally:
    self._endCommandEchoBlock()
  #
  return result

def _produceNmrAtom(self:Project, atomId:str=None, chainCode:str=None,
                   sequenceCode:Union[int,str]=None,
                   residueType:str=None, name:str=None) -> NmrAtom:
  """get chainCode, sequenceCode, residueType and atomName from dot-separated  atomId or Pid
  or explicit parameters, and find or create an NmrAtom that matches
  Empty chainCode gets NmrChain:@- ; empty sequenceCode get a new NmrResidue"""

  defaults = collections.OrderedDict((('atomId', None), ('chainCode', None), ('sequenceCode', None),
                                     ('residueType', None), ('name', None), ))

  self._startCommandEchoBlock('_produceNmrAtom', values=locals(), defaults=defaults,
                              parName='newNmrAtom')
  try:
    # Get ID parts to use
    if sequenceCode is not None:
      sequenceCode = str(sequenceCode) or None
    params = [chainCode, sequenceCode, residueType, name]
    if atomId:
      if any(params):
        raise ValueError("_produceNmrAtom: other parameters only allowed if atomId is None")
      else:
        # Remove colon prefix, if any
        atomId = atomId.split(Pid.PREFIXSEP, 1)[-1]
        for ii,val in enumerate(Pid.splitId(atomId)):
          if val:
            params[ii] = val
        chainCode, sequenceCode, residueType, name = params

    if name is None:
      raise ValueError("NmrAtom name must be set")

    elif Pid.altCharacter in name:
      raise ValueError("Character %s not allowed in ccpn.NmrAtom.name" % Pid.altCharacter)

    # Produce chain
    nmrChain = self.fetchNmrChain(shortName=chainCode or Constants.defaultNmrChainCode)
    nmrResidue = nmrChain.fetchNmrResidue(sequenceCode=sequenceCode, residueType=residueType)
    result = nmrResidue.fetchNmrAtom(name)
  finally:
    self._endCommandEchoBlock()
  return result
    
# Connections to parents:
NmrResidue.newNmrAtom = _newNmrAtom
del _newNmrAtom
NmrResidue.fetchNmrAtom = _fetchNmrAtom

Project._produceNmrAtom = _produceNmrAtom

# Notifiers:
className = Nmr.Resonance._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_finaliseApiRename', {}, className, 'setImplName'),
    ('_finaliseApiRename', {}, className, 'setResonanceGroup'),
  )
)
for clazz in Nmr.AbstractPeakDimContrib._metaclass.getNonAbstractSubtypes():
  className = clazz.qualifiedName()
  Project._apiNotifiers.extend(
    ( ('_modifiedLink', {'classNames':('NmrAtom','Peak')}, className, 'create'),
      ('_modifiedLink', {'classNames':('NmrAtom','Peak')}, className, 'delete'),
    )
  )

# NB Atom<->NmrAtom link depends solely on the NmrAtom name.
# So no notifiers on the link - notify on the NmrAtom rename instead.
