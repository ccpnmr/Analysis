"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
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

from ccpn._wrapper._AbstractWrapperObject import AbstractWrapperObject
from ccpn._wrapper._Project import Project
from ccpn._wrapper._ChemicalShiftList import ChemicalShiftList
from ccpn._wrapper._NmrAtom import NmrAtom
from ccpncore.api.ccp.nmr.Nmr import Shift as ApiShift

class ChemicalShift(AbstractWrapperObject):
  """Chemical Shift."""
  
  #: Short class name, for PID.
  shortClassName = 'CS'

  #: Name of plural link to instances of class
  _pluralLinkName = 'chemicalShifts'
  
  #: List of child classes.
  _childClasses = []

  # CCPN properties  
  @property
  def apiShift(self) -> ApiShift:
    """ CCPN Chemical Shift matching ChemicalShift"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """identifier - assignment string"""
    # return ','.join(x or '' for x in self.nmrAtom.assignment)
    return self.nmrAtom._id
    
  @property
  def _parent(self) -> Project:
    """Parent (containing) object."""
    return self._project
  
  project = _parent
  
  @property
  def value(self) -> float:
    """shift value of ChemicalShift"""
    return self._wrappedData.value
    
  @value.setter
  def value(self, value:float):
    self._wrappedData.value = value

  @property
  def valueError(self) -> float:
    """shift valueError of ChemicalShift"""
    return self._wrappedData.error

  @valueError.setter
  def valueError(self, value:float):
    self._wrappedData.error = value

  @property
  def figureOfMerit(self) -> str:
    """Figure of Merit for ChemicalShift"""
    return self._wrappedData.figOfMerit

  @figureOfMerit.setter
  def figureOfMerit(self, value:str):
    self._wrappedData.figOfMerit = value
  
  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details
    
  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  @property
  def nmrAtom(self) -> NmrAtom:
    """NmrAtom that the shift belongs to"""
    return self._project._data2Obj.get(self._wrappedData.resonance)

    
  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent: ChemicalShiftList)-> list:
    """get wrappedData (ChemicalShiftLists) for all Shift children of parent ChemicalShiftList"""
    return [x for x in parent._wrappedData.sortedMeasurements()]

# Connections to parents:
ChemicalShiftList._childClasses.append(ChemicalShift)

def newChemicalShift(parent:ChemicalShiftList, value:float, nmrAtom:NmrAtom,
                     valueError:float=0.0, figureOfMerit:float=1.0,
                     comment:str=None) -> ChemicalShift:
  """Create new child Shift"""
  obj = parent._wrappedData.newShift(value=value,
                                     resonance=nmrAtom._wrappedData, error=valueError,
                                     figOfMerit=figureOfMerit, details=comment)
  return parent._project._data2Obj.get(obj)

ChemicalShiftList.newChemicalShift = newChemicalShift

# Notifiers:
className = ApiShift._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':ChemicalShift}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete')
  )
)