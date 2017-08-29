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
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import collections
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Project import Project
from ccpn.core.PeakList import PeakList
from ccpn.core.Spectrum import Spectrum
from typing import List
from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import PeakList as ApiPeakList
import numpy as np
from scipy.integrate import trapz

from ccpn.core.lib.SpectrumLib import _estimateNoiseLevel1D



def _createIntersectingLine(x, y):
  '''create a straight line with x values like the original spectrum and y value from the estimated noise level'''
  return [_estimateNoiseLevel1D(x, y)] * len(x)


def _getIntersectionPoints(x, y, line):
  '''
  :param line: x points of line to intersect y points
  :return: list of intersecting points
  '''
  z = y - line
  dx = x[1:] - x[:-1]
  cross = np.sign(z[:-1] * z[1:])

  x_intersect = x[:-1] - dx / (z[1:] - z[:-1]) * z[:-1]
  negatives = np.where(cross < 0)
  points = x_intersect[negatives]

  return points


def _pairIntersectionPoints(intersectionPoints):
  """ Yield successive pair chunks from list of intersectionPoints """
  for i in range(0, len(intersectionPoints), 2):
    pair = intersectionPoints[i:i + 2]
    if len(pair) == 2:
      yield pair


def _getPeaksLimits(x, y, intersectingLine=None):
  '''Get the limits of each peak of the spectrum given an intersecting line. If
   intersectingLine is None, it is calculated by the STD of the spectrum'''
  if intersectingLine is  None:
    intersectingLine = _createIntersectingLine(x, y)
  limits = _getIntersectionPoints(x, y, intersectingLine)
  limitsPairs = list(_pairIntersectionPoints(limits))
  return limitsPairs





class IntegralList(AbstractWrapperObject):
  """An object containing Integrals. Note: the object is not a (subtype of a) Python list.
  To access all Integral objects, use integralList.integrals."""
  
  #: Short class name, for PID.
  shortClassName = 'IL'
  # Attribute it necessary as subclasses must use superclass className
  className = 'IntegralList'

  _parentClass = Spectrum

  #: Name of plural link to instances of class
  _pluralLinkName = 'integralLists'
  
  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class - NB shared with PeakList
  _apiClassQualifiedName = ApiPeakList._metaclass.qualifiedName()

  # Notifiers are handled through the PeakList class (which shares the ApiPeakList wrapped object)
  _registerClassNotifiers = False

  # Special error-raising functions for people who think PeakList is a list
  def __iter__(self):
    raise TypeError("IntegralList object is not iterable -"
                    "for a list of integrals use IntegralList.integrals")

  def __getitem__(self, index):
    raise TypeError("IntegralList object does not support indexing -"
                    " for a list of integrals use IntegralList.integrals")

  def __len__(self):
    raise TypeError("IntegralList object has no length - "
                    "for a list of integrals use IntegralList.integrals")

  # CCPN properties  
  @property
  def _apiPeakList(self) -> ApiPeakList:
    """ API peakLists matching IntegralList"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """id string - serial number converted to string"""
    return str(self._wrappedData.serial)

  @property
  def serial(self) -> int:
    """serial number of IntegralList, used in Pid and to identify the IntegralList. """
    return self._wrappedData.serial
    
  @property
  def _parent(self) -> Spectrum:
    """Spectrum containing IntegralList."""
    return  self._project._data2Obj[self._wrappedData.dataSource]
  
  spectrum = _parent
  
  @property
  def title(self) -> str:
    """title of IntegralList (not used in PID)."""
    return self._wrappedData.name
    
  @title.setter
  def title(self, value:str):
    self._wrappedData.name = value

  @property
  def symbolColour(self) -> str:
    """Symbol colour for integral annotation display"""
    return self._wrappedData.symbolColour

  @symbolColour.setter
  def symbolColour(self, value:str):
    self._wrappedData.symbolColour = value

  @property
  def textColour(self) -> str:
    """Text colour for integral annotation display"""
    return self._wrappedData.textColour

  @textColour.setter
  def textColour(self, value:str):
    self._wrappedData.textColour = value
  
  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details
    
  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent: Spectrum)-> list:
    """get wrappedData (PeakLists) for all IntegralList children of parent Spectrum"""
    return [x for x in parent._wrappedData.sortedPeakLists() if x.dataType == 'Integral']

  # Library functions

  def automaticIntegral1D(self, minimalLineWidth=0.01, noiseThreshold=None,) -> List['Integral']:
    '''
    minimalLineWidth:  an attempt to exclude noise. Below this threshold the area is discarded.
    noiseThreshold: value used to calculate the intersectingLine to get the peak limits
    '''
    # TODO: add excludeRegions option. Calculate Negative peak integral.
    self._project.suspendNotification()
    try:
      spectrum = self.spectrum
      x, y = np.array(spectrum.positions), np.array(spectrum.intensities)
      if noiseThreshold is None:
        intersectingLine = None
      else:
        intersectingLine = [noiseThreshold] * len(x)
      limitsPairs = _getPeaksLimits(x, y, intersectingLine)

      integrals = []

      for i in limitsPairs:
        lineWidth = abs(i[0] - i[1])
        if lineWidth > minimalLineWidth:
          index01 = np.where((x <= i[0]) & (x >= i[1]))
          # integral = trapz(index01)
          integrals.append(self.newIntegral(value= None, limits=[[min(i), max(i)],]))

    finally:
      self._project.resumeNotification()

    return integrals

# Connections to parents:

def _newIntegralList(self:Spectrum, title:str=None, symbolColour:str=None,
                     textColour:str=None, comment:str=None) -> IntegralList:
  """Create new IntegralList within Spectrum"""

  defaults = collections.OrderedDict((('title', None), ('comment', None),
                                      ('symbolColour',None), ('textColour',None)))

  apiDataSource = self._wrappedData
  self._startCommandEchoBlock('newIntegralList', values=locals(), defaults=defaults,
                              parName='newIntegralList')
  dd = {'name':title, 'details':comment, 'dataType':'Integral'}
  if symbolColour:
    dd['symbolColour'] = symbolColour
  if textColour:
    dd['textColour'] = textColour
  try:
    obj = apiDataSource.newPeakList(**dd)
  finally:
    self._endCommandEchoBlock()
  return self._project._data2Obj.get(obj)

Spectrum.newIntegralList = _newIntegralList
del _newIntegralList


def _factoryFunction(project:Project, wrappedData:ApiPeakList) -> AbstractWrapperObject:
  """create PeakList or IntegralList from API PeakList"""
  if wrappedData.dataType == 'Peak':
    return PeakList(project, wrappedData)
  elif wrappedData.dataType == 'Integral':
    return IntegralList(project, wrappedData)
  else:
    raise ValueError("API PeakList object has illegal dataType: %s. Must be 'Peak' or 'Integral"
                     % wrappedData.dataType)


IntegralList._factoryFunction = staticmethod(_factoryFunction)
PeakList._factoryFunction = staticmethod(_factoryFunction)











# Notifiers:

# NB API level notifiers are (and must be) in PeakList instead



