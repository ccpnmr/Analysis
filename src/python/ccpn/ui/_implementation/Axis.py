"""GUI Display Strip class

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
__dateModified__ = "$dateModified: 2017-07-07 16:32:40 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from typing import Sequence, Tuple

from ccpn.core.NmrAtom import NmrAtom
from ccpn.core.Project import Project
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.ui._implementation.Strip import Strip
from ccpn.core.lib import Pid
from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import Axis as ApiAxis
from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import StripAxis as ApiStripAxis

# from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import Axis as ApiAxis


class Axis(AbstractWrapperObject):
  """Display Axis for 1D or nD spectrum"""

  #: Short class name, for PID.
  shortClassName = 'GA'
  # Attribute it necessary as subclasses must use superclass className
  className = 'Axis'

  _parentClass = Strip

  #: Name of plural link to instances of class
  _pluralLinkName = 'axes'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = ApiStripAxis._metaclass.qualifiedName()
  

  # CCPN properties  
  @property
  def _apiStripAxis(self) -> ApiStripAxis:
    """ CCPN Axis matching Axis"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """local id, equal to Axis code"""
    return self._wrappedData.axis.code.translate(Pid.remapSeparators)

  code = _key

    
  @property
  def _parent(self) -> Strip:
    """Strip containing axis."""
    return self._project._data2Obj.get(self._wrappedData.strip)

  strip = _parent

  @property
  def position(self) -> float:
    """Centre point position for displayed region, in current unit."""
    return self._wrappedData.axis.position

  @position.setter
  def position(self, value):
    self._wrappedData.axis.position = value

  @property
  def width(self) -> float:
    """Width for displayed region, in current unit."""
    return self._wrappedData.axis.width

  @width.setter
  def width(self, value):
    self._wrappedData.axis.width = value

  @property
  def region(self) -> tuple:
    """Display region - position +/- width/2.."""
    position = self._wrappedData.axis.position
    halfwidth = self._wrappedData.axis.width / 2.
    return (position - halfwidth, position + halfwidth)

  @region.setter
  def region(self, value):
    self._wrappedData.axis.position = (value[0] + value[1]) / 2.
    self._wrappedData.axis.width = abs(value[1] - value[0])

  @property
  def unit(self) -> str:
    """Display unit for axis"""
    return self._wrappedData.axis.unit

  # NBNB TBD This should be settable, but changing it requires changing the position
  # values. For now we leave it unsettable.

  # NBNB TBD the 'regions' attribute may not be needed. leave it out

  @property
  def nmrAtoms(self) -> Tuple[NmrAtom]:
    """nmrAtoms connected to axis"""
    ff = self._project._data2Obj.get
    return tuple(sorted(ff(x) for x in self._wrappedData.axis.resonances))

  @nmrAtoms.setter
  def nmrAtoms(self, value):
    value = [self.getByPid(x) if isinstance(x, str) else x for x in value]
    self._wrappedData.axis.resonances = tuple(x._wrappedData for x in value)

  @property
  def strip(self):
    """Strip that Axis belongs to"""
    return self._project._data2Obj.get(self._wrappedData.strip)

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:Strip)-> list:
    """get wrappedData (ccpnmr.gui.Task.Axis) in serial number order"""
    apiStrip = parent._wrappedData
    dd = {x.axis.code:x for x in apiStrip.stripAxes}
    return [dd[x] for x in apiStrip.axisCodes]

  def delete(self):
    """Overrides normal delete"""
    raise  ValueError("Axes cannot be deleted independently")


# We should NOT have any newAxis functions

# Strip.orderedAxes property
def getter(self) -> Tuple[Axis, ...]:
  apiStrip = self._wrappedData
  ff = self._project._data2Obj.get
  return tuple(ff(apiStrip.findFirstStripAxis(axis=x)) for x in apiStrip.orderedAxes)
def setter(self, value:Sequence):
  value = [self.getByPid(x) if isinstance(x, str) else x for x in value]
  #self._wrappedData.orderedAxes = tuple(x._wrappedData.axis for x in value)
  self._wrappedData.axisOrder = tuple(x.code for x in value)
Strip.orderedAxes = property(getter, setter, None,
                             "Axes in display order (X, Y, Z1, Z2, ...) ")
del getter
del setter

# Notifiers:
Project._apiNotifiers.append(
  ('_notifyRelatedApiObject', {'pathToObject':'stripAxes', 'action':'change'},
   ApiAxis._metaclass.qualifiedName(), '')
)


