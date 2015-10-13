"""Peak View in a specific  PeakList View

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

from ccpn import AbstractWrapperObject
from ccpn import Project
from ccpn import Peak
from ccpnmr import PeakListView
from ccpncore.api.ccpnmr.gui.Task import PeakView as ApiPeakView


class PeakView(AbstractWrapperObject):
  """Peak View for 1D or nD PeakList"""
  
  #: Short class name, for PID.
  shortClassName = 'GP'
  # Attribute it necessary as subclasses must use superclass className
  className = 'PeakView'

  #: Name of plural link to instances of class
  _pluralLinkName = 'peakViews'
  
  #: List of child classes.
  _childClasses = []
  

  # CCPN properties  
  @property
  def _apiPeakView(self) -> ApiPeakView:
    """ CCPN PeakView matching PeakView"""
    return self._wrappedData
    
  @property
  def _parent(self) -> PeakListView:
    """PeakListView containing PeakView."""
    return self._project._data2Obj.get(self._wrappedData.peakListView)

  spectrumView= _parent

  @property
  def _key(self) -> str:
    """id string - """
    return str(self._wrappedData.peak.serial)

  @property
  def textOffset(self) -> tuple:
    """Peak X,Y text annotation offset"""
    return self._wrappedData.textOffset

  @textOffset.setter
  def experimentType(self, value:tuple):
    self._wrappedData.textOffset = value

  @property
  def peak(self) -> Peak:
    """Peak that PeakView refers to"""
    return self._getWrapperObject(self._wrappedData.peak)

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:PeakListView)-> list:
    """get wrappedData (ccpnmr.gui.Task.PeakView) in serial number order"""
    return parent._wrappedData.sortedPeakViews()

  #CCPN functions

# Peak.peakViews property
def _getPeakViews(peak:Peak):
  return tuple(peak._project._data2Obj[x]
               for x in peak._wrappedData.sortedPeakViews())
Peak.peakViews = property(_getPeakViews, None, None,
                                         "PeakListViews showing Spectrum")
del _getPeakViews


# Connections to parents:
PeakListView._childClasses.append(PeakView)

# Notifiers:
className = ApiPeakView._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':PeakView}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete'),
    ('_finaliseUnDelete', {}, className, 'undelete'),
  )
)
