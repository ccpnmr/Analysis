"""Spectrum  class. Gives spectrum values, including per-dimension values as tuples.
Values that are not defined for a given dimension (e.g. sampled dimensions) are given as None.
Reference-related values apply only to the first Reference given (which is sufficient for
all common cases).

Dimension identifiers run from 1 to the number of dimensions (e.g. 1,2,3 for a 3D).
Per-dimension values are given in the order data are stored in the spectrum file - for
CCPN data the preferred convention is to have the acquisition dimension as dimension 1.

The axisCodes are used as an alternative axis identifier. They are unique strings (so they can
b recognised even if the axes are reordered in display). The axisCodes reflect the isotope
on the relevant axis, and match the dimension identifiers in the reference experiment templates,
linking a dimension to the correct reference experiment dimension. They are also used to map
automatically spectrum axes to display axes and to other spectra. By default the axis name
is the name of the atom being measured. Axes that are linked by a onebond
magnetisation transfer are given a lower-case suffix to show the nucleus bound to.
Duplicate axis names are distinguished by a
numerical suffix. The rules are best shown by example:

Experiment                 axisCodes

1D Bromine NMR             Br

3D proton NOESY-TOCSY      H, H1, H2

19F-13C-HSQC               Fc, Cf

15N-NOESY-HSQC OR
15N-HSQC-NOESY:            Hn, Nh, H

4D HCCH-TOCSY              Hc, Ch, Hc1, Ch1

HNCA/CB                    H. N. C

HNCO                       Hn, Nh, CO     *(CO is treated as a separate type)*

HCACO                      Hca, CAh, CO    *(CA is treated as a separate type)*

"""
# TODO double check axis codes for HCACO, HNCO, and use of Hcn axiscodes

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
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import numpy
import operator
from typing import Sequence, Tuple, Optional
from ccpn.util import Common as commonUtil
from ccpn.util import Constants
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Project import Project
from ccpnmodel.ccpncore.api.ccp.nmr import Nmr
from ccpnmodel.ccpncore.api.ccp.general import DataLocation
from ccpn.core.lib import Pid
from ccpn.core.lib.SpectrumLib import MagnetisationTransferTuple

from ccpnmodel.ccpncore.lib.Io import Formats


class Spectrum(AbstractWrapperObject):
  """A Spectrum object contains all the stored properties of an NMR spectrum, as well as the
  path to the stored NMR data file."""

  #: Short class name, for PID.
  shortClassName = 'SP'
  # Attribute it necessary as subclasses must use superclass className
  className = 'Spectrum'

  _parentClass = Project

  #: Name of plural link to instances of class
  _pluralLinkName = 'spectra'

  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = Nmr.DataSource._metaclass.qualifiedName()

  def __init__(self, project:Project, wrappedData:Nmr.ShiftList):

    self._intensities = None
    self._positions = None

    super().__init__(project, wrappedData)

  # CCPN properties
  @property
  def _apiDataSource(self) -> Nmr.DataSource:
    """ CCPN DataSource matching Spectrum"""
    return self._wrappedData


  @property
  def _key(self) -> str:
    """name, regularised as used for id"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def _localCcpnSortKey(self) -> Tuple:
    """Local sorting key, in context of parent."""
    dataSource = self._wrappedData
    return(dataSource.experiment.serial, dataSource.serial)


  @property
  def name(self) -> str:
    """short form of name, used for id"""

    return self._wrappedData.name

  @property
  def _parent(self) -> Project:
    """Parent (containing) object."""
    return self._project

  # Attributes of DataSource and Experiment:

  @property
  def dimensionCount(self) -> int:
    """Number of dimensions in spectrum"""
    return self._wrappedData.numDim

  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details

  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  @property
  def positiveContourCount(self) -> int:
    """number of positive contours to draw"""
    return self._wrappedData.positiveContourCount

  @positiveContourCount.setter
  def positiveContourCount(self, value):
    self._wrappedData.positiveContourCount  = value

  @property
  def positiveContourBase(self) -> float:
    """base level of positive contours"""
    return self._wrappedData.positiveContourBase

  @positiveContourBase.setter
  def positiveContourBase(self, value):
    self._wrappedData.positiveContourBase  = value

  @property
  def positiveContourFactor(self) -> float:
    """level multiplier for positive contours"""
    return self._wrappedData.positiveContourFactor

  @positiveContourFactor.setter
  def positiveContourFactor(self, value):
    self._wrappedData.positiveContourFactor  = value

  @property
  def positiveContourColour(self) -> str:
    """colour of positive contours"""
    return self._wrappedData.positiveContourColour

  @positiveContourColour.setter
  def positiveContourColour(self, value):
    self._wrappedData.positiveContourColour  = value

  @property
  def negativeContourCount(self) -> int:
    """number of negative contours to draw"""
    return self._wrappedData.negativeContourCount

  @negativeContourCount.setter
  def negativeContourCount(self, value):
    self._wrappedData.negativeContourCount  = value

  @property
  def negativeContourBase(self) -> float:
    """base level of negative contours"""
    return self._wrappedData.negativeContourBase

  @negativeContourBase.setter
  def negativeContourBase(self, value):
    self._wrappedData.negativeContourBase  = value

  @property
  def negativeContourFactor(self) -> float:
    """level multiplier for negative contours"""
    return self._wrappedData.negativeContourFactor

  @negativeContourFactor.setter
  def negativeContourFactor(self, value):
    self._wrappedData.negativeContourFactor  = value

  @property
  def negativeContourColour(self) -> str:
    """colour of negative contours"""
    return self._wrappedData.negativeContourColour

  @negativeContourColour.setter
  def negativeContourColour(self, value):
    self._wrappedData.negativeContourColour  = value

  @property
  def sliceColour(self) -> str:
    """colour of 1D slices"""
    return self._wrappedData.sliceColour

  @sliceColour.setter
  def sliceColour(self, value):
    self._wrappedData.sliceColour  = value

  @property
  def scale(self) -> float:
    """Scaling factor for intensities and volumes.
    Intensities and volumes should be *multiplied* by scale before comparison."""
    return self._wrappedData.scale

  @scale.setter
  def scale(self, value:float):
    self._wrappedData.scale = value
    for spectrumView in self.spectrumViews:
      spectrumView.refreshData()

  @property
  def spinningRate(self) -> float:
    """NMR tube spinning rate (in Hz)."""
    return self._wrappedData.experiment.spinningRate

  @spinningRate.setter
  def spinningRate(self, value:float):
    self._wrappedData.experiment.spinningRate = value

  @property
  def noiseLevel(self) -> float:
    """Estimated noise level for the spectrum,
    defined as the estimated standard deviation of the points from the baseplane/baseline"""
    return self._wrappedData.noiseLevel

  @noiseLevel.setter
  def noiseLevel(self, value:float):
    self._wrappedData.noiseLevel = value

  @property
  def experimentType(self) -> str:
    """Systematic experiment type descriptor (CCPN system)."""
    refExperiment = self._wrappedData.experiment.refExperiment
    if refExperiment is None:
      return None
    else:
      return refExperiment.name

  @experimentType.setter
  def experimentType(self, value:str):
    for nmrExpPrototype in self._wrappedData.root.sortedNmrExpPrototypes():
      for refExperiment in nmrExpPrototype.sortedRefExperiments():
        if value == refExperiment.name:
          # refExperiment matches name string - set it
          self._wrappedData.experiment.refExperiment = refExperiment
          synonym = refExperiment.synonym
          if synonym:
            self.experimentName = synonym
          return
    # nothing found - error:
    raise ValueError("No reference experiment matches name '%s'" % value)

  @property
  def experimentName(self) -> str:
    """Common experiment type descriptor (May not be unique)."""
    return self._wrappedData.experiment.name

  @experimentName.setter
  def experimentName(self, value):
    self._wrappedData.experiment.name = value

  @property
  def filePath(self) -> str:
    """Absolute path to NMR data file."""
    xx = self._wrappedData.dataStore
    if xx:
      return xx.fullPath
    else:
      return None

  @filePath.setter
  def filePath(self, value:str):

    apiDataStore = self._wrappedData.dataStore
    if apiDataStore is None:
      raise ValueError("Spectrum is not stored, cannot change file path")

    elif not value:
      raise ValueError("Spectrum file path cannot be set to None")

    else:
      dataUrl = self._project._wrappedData.root.fetchDataUrl(value)
      apiDataStore.repointToDataUrl(dataUrl)
      apiDataStore.path = value[len(dataUrl.url.path)+1:]

  @property
  def headerSize(self) -> int:
    """File header size in bytes."""
    xx = self._wrappedData.dataStore
    if xx:
      return xx.headerSize
    else:
      return None
  # NBNB TBD Should this be made modifiable? Would be a bit of work ...

  @property
  def numberType(self) -> str:
    """Data type of numbers stored in data matrix ('int' or 'float')."""
    xx = self._wrappedData.dataStore
    if xx:
      return xx.numberType
    else:
      return None
  # NBNB TBD Should this be made modifiable? Would be a bit of work ...

  @property
  def complexStoredBy(self) -> str:
    """Hypercomplex numbers are stored by ('timepoint', 'quadrant', or 'dimension')."""
    xx = self._wrappedData.dataStore
    if xx:
      return xx.complexStoredBy
    else:
      return None
  # NBNB TBD Should this be made modifiable? Would be a bit of work ...

  # Attributes belonging to AbstractDataDim

  def _setStdDataDimValue(self, attributeName, value:Sequence):
    """Set value for non-Sampled DataDims only"""
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        if dataDim.className != 'SampledDataDim':
          setattr(dataDim, attributeName, value[ii])
        elif value[ii] is not None:
          raise ValueError("Attempt to set value for invalid attribute %s in dimension %s: %s" %
                           (attributeName, ii+1, value))
    else:
      raise ValueError("Value must have length %s, was %s" % (apiDataSource.numDim, value))

  @property
  def pointCounts(self) -> Tuple[int, ...]:
    """Number active of points per dimension

    NB, Changing the pointCounts will keep the spectralWidths (after Fourier transformation)
    constant.

    NB for FidDataDims more points than these may be stored (see totalPointCount)."""
    result = []
    for dataDim in self._wrappedData.sortedDataDims():
      if hasattr(dataDim, 'numPointsValid'):
        result.append(dataDim.numPointsValid)
      else:
        result.append(dataDim.numPoints)
    return tuple(result)

  @pointCounts.setter
  def pointCounts(self, value:Sequence):
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      dataDimRefs = self._mainDataDimRefs()
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        val = value[ii]
        className = dataDim.className
        if className == 'SampledDataDim':
          # No sweep width to worry about. Up to programmer to make sure sampled values match.
          dataDim.numPoints = val
        elif  className == 'FidDataDim':
          #Number of points refers to time domain, independent of sweep width
          dataDim.numPointsValid = val
        elif className == 'FreqDataDim':
          # Changing the number of points may NOT change the spectralWidth
          relativeVal = val / dataDim.numPoints
          dataDim.numPoints = val
          dataDim.valuePerPoint /= relativeVal
          dataDimRef = dataDimRefs[ii]
          if dataDimRef is not None:
            # This will work if we are changing to a different factor of two in pointCount.
            # If we are making an arbitrary change, the referencing is not reliable anyway.
            dataDimRef.refPoint = ((dataDimRef.refPoint -1) * relativeVal) + 1
        else:
          raise TypeError("API DataDim object with unknown className:", className)
    else:
      raise ValueError("pointCounts value must have length %s, was %s" %
                       (apiDataSource.numDim, value))

  @property
  def totalPointCounts(self) -> Tuple[int, ...]:
    """Total number of points per dimension

    NB for FidDataDims and SampledDataDims these are the stored points,
    for FreqDataDims these are the points after transformation before cutting down.

    NB, changing the totalPointCount will *not* modify the resolution (or dwell time),
    so the implied total width will change."""
    result = []
    for dataDim in self._wrappedData.sortedDataDims():
      if hasattr(dataDim, 'numPointsOrig'):
        result.append(dataDim.numPointsOrig)
      else:
        result.append(dataDim.numPoints)
    return tuple(result)

  @totalPointCounts.setter
  def totalPointCounts(self, value:Sequence):
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        if hasattr(dataDim, 'numPointsOrig'):
          dataDim.numPointsOrig = value[ii]
        else:
          dataDim.numPoints = value[ii]
    else:
      raise ValueError("totalPointCount value must have length %s, was %s" %
                       (apiDataSource.numDim, value))

  @property
  def pointOffsets(self) -> Tuple[int, ...]:
    """index of first active point relative to total points, per dimension"""
    return tuple(x.pointOffset if x.className != 'SampledDataDim' else None
             for x in self._wrappedData.sortedDataDims())

  @pointOffsets.setter
  def pointOffsets(self, value:Sequence):
    self._setStdDataDimValue('pointOffset', value)

  @property
  def isComplex(self) -> Tuple[bool, ...]:
    """Is dimension complex? -  per dimension"""
    return tuple(x.isComplex for x in self._wrappedData.sortedDataDims())

  @isComplex.setter
  def isComplex(self, value:Sequence):
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        dataDim.isComplex = value[ii]
    else:
      raise ValueError("Value must have length %s, was %s" % (apiDataSource.numDim, value))

  @property
  def dimensionTypes(self) -> Tuple[str, ...]:
    """dimension types ('Fid' / 'Frequency' / 'Sampled'),  per dimension"""
    ll = [x.className[:-7] for x in self._wrappedData.sortedDataDims()]
    return tuple('Frequency' if x == 'Freq' else x for x in ll)

  @property
  def spectralWidthsHz(self) -> Tuple[Optional[float], ...]:
    """spectral width (in Hz) before dividing by spectrometer frequency, per dimension"""
    return tuple(x.spectralWidth if hasattr(x, 'spectralWidth') else None
                 for x in self._wrappedData.sortedDataDims())

  @spectralWidthsHz.setter
  def spectralWidthsHz(self, value:Sequence):
    apiDataSource = self._wrappedData
    attributeName = 'spectralWidth'
    if len(value) == apiDataSource.numDim:
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        val = value[ii]
        if hasattr(dataDim, attributeName):
          if not val:
            raise ValueError("Attempt to set %s to %s in dimension %s: %s"
                           % (attributeName, val, ii+1, value))
          else:
            # We assume that the number of points is constant, so setting SW changes valuePerPoint
            swold = getattr(dataDim, attributeName)
            dataDim.valuePerPoint *= (val/swold)
        elif val is not None:
          raise ValueError("Attempt to set %s in sampled dimension %s: %s"
                           % (attributeName, ii+1, value))
    else:
      raise ValueError("SpectralWidth value must have length %s, was %s" %
                       (apiDataSource.numDim, value))

    @property
    def valuesPerPoint(self) -> Tuple[Optional[float], ...]:
      """valuePerPoint for each dimension

      in ppm for Frequency dimensions with a single, well-defined reference

      None for Frequency dimensions without a single, well-defined reference

      in time units (seconds) for FId dimensions

      None for sampled dimensions"""

      result = []
      for dataDim in self._wrappedData.sortedDataDims():
        if hasattr(dataDim, 'primaryDataDimRef'):
          # FreqDataDim - get ppm valuePerPoint
          ddr = dataDim.primaryDataDimRef
          valuePerPoint = ddr and ddr.valuePerPoint
        elif hasattr(dataDim, 'valuePerPoint'):
          # FidDataDim - get time valuePerPoint
          valuePerPoint = dataDim.valuePerPoint
        else:
          # Sampled DataDim - return None
          valuePerPoint = None
        #
        result.append(valuePerPoint)
      #
      return tuple(result)

  @property
  def phases0(self) -> tuple:
    """zero order phase correction (or None), per dimension. Always None for sampled dimensions."""
    return tuple(x.phase0 if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @phases0.setter
  def phases0(self, value:Sequence):
    self._setStdDataDimValue('phase0', value)

  @property
  def phases1(self) -> Tuple[Optional[float], ...]:
    """first order phase correction (or None) per dimension. Always None for sampled dimensions."""
    return tuple(x.phase1 if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @phases1.setter
  def phases1(self, value:Sequence):
    self._setStdDataDimValue('phase1', value)

  @property
  def windowFunctions(self) -> Tuple[Optional[str], ...]:
    """Window function name (or None) per dimension - e.g. 'EM', 'GM', 'SINE', 'QSINE', ....
    Always None for sampled dimensions."""
    return tuple(x.windowFunction if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @windowFunctions.setter
  def windowFunctions(self, value:Sequence):
    self._setStdDataDimValue('windowFunction', value)

  @property
  def lorentzianBroadenings(self) -> Tuple[Optional[float], ...]:
    """Lorenzian broadening in Hz per dimension. Always None for sampled dimensions."""
    return tuple(x.lorentzianBroadening if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @lorentzianBroadenings.setter
  def lorentzianBroadenings(self, value:Sequence):
    self._setStdDataDimValue('lorentzianBroadening', value)

  @property
  def gaussianBroadenings(self) -> Tuple[Optional[float], ...]:
    """Gaussian broadening per dimension. Always None for sampled dimensions."""
    return tuple(x.gaussianBroadening if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @gaussianBroadenings.setter
  def gaussianBroadenings(self, value:Sequence):
    self._setStdDataDimValue('gaussianBroadening', value)

  @property
  def sineWindowShifts(self) -> Tuple[Optional[float], ...]:
    """Shift of sine/sine-square window function in degrees. Always None for sampled dimensions."""
    return tuple(x.sineWindowShift if x.className != 'SampledDataDim' else None
                 for x in self._wrappedData.sortedDataDims())

  @sineWindowShifts.setter
  def sineWindowShifts(self, value:Sequence):
    self._setStdDataDimValue('sineWindowShift', value)

  # Attributes belonging to ExpDimRef and DataDimRef

  def _mainExpDimRefs(self) -> list:
    """Get main API ExpDimRef (serial=1) for each dimension"""

    result = []
    for ii,dataDim in enumerate(self._wrappedData.sortedDataDims()):
      # NB MUST loop over dataDims, in case of projection spectra
      result.append(dataDim.expDim.findFirstExpDimRef(serial=1))
    #
    return tuple(result)


  def _setExpDimRefAttribute(self, attributeName:str, value:Sequence, mandatory:bool=True):
    """Set main ExpDimRef attribute (serial=1) for each dimension"""
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      for ii,dataDim in enumerate(self._wrappedData.sortedDataDims()):
        # NB MUST loop over dataDims, in case of projection spectra
        expDimRef = dataDim.expDim.findFirstExpDimRef(serial=1)
        val = value[ii]
        if expDimRef is None and val is not None:
          raise ValueError("Attempt to set attribute %s in dimension %s to %s - must be None" %
                             (attributeName, ii+1, val))
        elif val is None and mandatory:
          raise ValueError(
            "Attempt to set mandatory attribute %s to None in dimension %s: %s" %
            (attributeName, ii+1, val))
        else:
          setattr(expDimRef, attributeName, val)

  @property
  def spectrometerFrequencies(self) -> Tuple[Optional[float], ...]:
    """Tuple of spectrometer frequency for main dimensions reference """
    return tuple(x and x.sf for x in self._mainExpDimRefs())

  @spectrometerFrequencies.setter
  def spectrometerFrequencies(self, value):
    self._setExpDimRefAttribute('sf', value)

  @property
  def measurementTypes(self) -> Tuple[Optional[str], ...]:
    """Type of value being measured, per dimension.

    In normal cases the measurementType will be 'Shift', but other values might be
    'MQSHift' (for multiple quantum axes), JCoupling (for J-resolved experiments),
    'T1', 'T2', ..."""
    return tuple(x and x.measurementType for x in self._mainExpDimRefs())

  @measurementTypes.setter
  def measurementTypes(self, value):
    self._setExpDimRefAttribute('measurementType', value)


  @property
  def isotopeCodes(self) -> Tuple[Optional[str], ...]:
    """isotopeCode of isotope being measured, per dimension - None if no unique code"""
    result = []
    for dataDim in self._wrappedData.sortedDataDims():
      expDimRef = dataDim.expDim.findFirstExpDimRef(serial=1)
      if expDimRef is None:
        result.append(None)
      else:
        isotopeCodes = expDimRef.isotopeCodes
        if len(isotopeCodes) == 1:
          result.append(isotopeCodes[0])
        else:
          result.append(None)
    #
    return tuple(result)

  @isotopeCodes.setter
  def isotopeCodes(self, value:Sequence):
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      if value != self.isotopeCodes and self.peaks:
        raise ValueError("Cannot reset isotopeCodes in a Spectrum that contains peaks")
      for ii,dataDim in enumerate(apiDataSource.sortedDataDims()):
        expDimRef = dataDim.expDim.findFirstExpDimRef(serial=1)
        val = value[ii]
        if expDimRef is None:
          if val is not None:
            raise ValueError("Cannot set isotopeCode %s in dimension %s" % (val, ii+1))
        elif val is None:
          expDimRef.isotopeCodes = ()
        else:
          expDimRef.isotopeCodes = (val,)
    else:
      raise ValueError("Value must have length %s, was %s" % (apiDataSource.numDim, value))

  @property
  def foldingModes(self) -> Tuple[Optional[str], ...]:
    """folding mode (values: 'circular', 'mirror', None), per dimension"""
    dd = {True:'mirror', False:'circular', None:None}
    return tuple(dd[x and x.isFolded] for x in self._mainExpDimRefs())

  @foldingModes.setter
  def foldingModes(self, value):

    # TODO For NEF we should support both True, False, and None
    # That requires an API change

    dd = {'circular':False, 'mirror':True, None:False}
    self._setExpDimRefAttribute('isFolded', [dd[x] for x in value])

  @property
  def axisCodes(self) -> Tuple[Optional[str], ...]:
    """axisCode, per dimension - None if no main ExpDimRef
    """

    # See if axis codes are set
    for expDim in self._wrappedData.experiment.expDims:
      if expDim.findFirstExpDimRef(axisCode=None) is not None:
        self._wrappedData.experiment.resetAxisCodes()
        break

    result = []
    for dataDim in self._wrappedData.sortedDataDims():
      expDimRef = dataDim.expDim.findFirstExpDimRef(serial=1)
      if expDimRef is None:
        result.append(None)
      else:
        axisCode = expDimRef.axisCode
        result.append(axisCode)

    return tuple(result)

  @axisCodes.setter
  def axisCodes(self, value):
    # TODO axisCodes shold be unique, but I am not sure this is enforced
    self._setExpDimRefAttribute('axisCode', value, mandatory=False)

  @property
  def acquisitionAxisCode(self) -> Optional[str]:
    """Axis code of acquisition axis - None if not known"""
    for dataDim in self._wrappedData.sortedDataDims():
      expDim = dataDim.expDim
      if expDim.isAcquisition:
        expDimRef = expDim.findFirstExpDimRef(serial=1)
        axisCode = expDimRef.axisCode
        if axisCode is None:
          self._wrappedData.experiment.resetAxisCodes()
          axisCode = expDimRef.axisCode
        return axisCode
    #
    return None

  @acquisitionAxisCode.setter
  def acquisitionAxisCode(self, value):
    if value is None:
      index = None
    else:
      index = self.axisCodes.index(value)

    for ii,dataDim in enumerate( self._wrappedData.sortedDataDims()):
      dataDim.expDim.isAcquisition = (ii == index)

  @property
  def axisUnits(self) -> Tuple[Optional[str], ...]:
    """Main axis unit (most commonly 'ppm'), per dimension - None if no unique code

    Uses first Shift-type ExpDimRef if there is more than one, otherwise first ExpDimRef"""
    return tuple(x and x.unit for x in self._mainExpDimRefs())

  @axisUnits.setter
  def axisUnits(self, value):
    self._setExpDimRefAttribute('unit', value, mandatory=False)

  # Attributes belonging to DataDimRef

  def _mainDataDimRefs(self) -> list:
    """ List of DataDimRef matching main ExpDimRef for each dimension"""
    result = []
    expDimRefs = self._mainExpDimRefs()
    for ii, dataDim in enumerate(self._wrappedData.sortedDataDims()):
      if hasattr(dataDim, 'dataDimRefs'):
        result.append(dataDim.findFirstDataDimRef(expDimRef=expDimRefs[ii]))
      else:
        result.append(None)
    #
    return result

  def _setDataDimRefAttribute(self, attributeName:str, value:Sequence, mandatory:bool=True):
    """Set main DataDimRef attribute for each dimension
    - uses first ExpDimRef with serial=1"""
    apiDataSource = self._wrappedData
    if len(value) == apiDataSource.numDim:
      expDimRefs = self._mainExpDimRefs()
      for ii, dataDim in  enumerate(self._wrappedData.sortedDataDims()):
        if hasattr(dataDim, 'dataDimRefs'):
          dataDimRef = dataDim.findFirstDataDimRef(expDimRef=expDimRefs[ii])
        else:
          dataDimRef = None

        if dataDimRef is None:
          if value[ii] is not None:
            raise ValueError("Cannot set value for attribute %s in dimension %s: %s" %
                             (attributeName, ii+1, value))
        elif value is None and mandatory:
          raise ValueError(
            "Attempt to set value to None for mandatory attribute %s in dimension %s: %s" %
            (attributeName, ii+1, value))
        else:
          setattr(dataDimRef, attributeName, value[ii])
    else:
      raise ValueError("Value must have length %s, was %s" % (apiDataSource.numDim, value))

  @property
  def referencePoints(self) -> Tuple[Optional[float], ...]:
    """point used for axis (chemical shift) referencing, per dimension."""
    return tuple(x and x.refPoint for x in self._mainDataDimRefs())

  @referencePoints.setter
  def referencePoints(self, value):
    self._setDataDimRefAttribute('refPoint', value)

  @property
  def referenceValues(self) -> Tuple[Optional[float], ...]:
    """value used for axis (chemical shift) referencing, per dimension."""
    return tuple(x and x.refValue for x in self._mainDataDimRefs())

  @referenceValues.setter
  def referenceValues(self, value):
    self._setDataDimRefAttribute('refValue', value)

  @property
  def assignmentTolerances(self) -> Tuple[Optional[float], ...]:
    """Assignment tolerance in axis unit (ppm), per dimension."""
    return tuple(x and x.assignmentTolerance for x in self._mainDataDimRefs())

  @assignmentTolerances.setter
  def assignmentTolerances(self, value):
    self._setDataDimRefAttribute('assignmentTolerance', value)

  @property
  def defaultAssignmentTolerances(self):
    """Default assignment tolerances, per dimension.

    NB for Fid or Sampled dimensions value will be None
    """
    tolerances = [None] * self.dimensionCount
    for ii, dimensionType in enumerate(self.dimensionTypes):
      if dimensionType == 'Frequency':
        tolerance = Constants.isotope2Tolerance.get(self.isotopeCodes[ii],
                                                    Constants.defaultAssignmentTolerance)
        tolerances[ii] = max(tolerance, self.spectralWidths[ii] / self.pointCounts[ii])
    #
    return tolerances

  @property
  def spectralWidths(self) -> Tuple[Optional[float], ...]:
    """spectral width after processing in axis unit (ppm), per dimension """
    return tuple(x and x.spectralWidth for x in self._mainDataDimRefs())

  @spectralWidths.setter
  def spectralWidths(self, value):
    oldValues = self.spectralWidths
    for ii,dataDimRef in enumerate(self._mainDataDimRefs()):
      if dataDimRef is not None:
        oldsw = oldValues[ii]
        sw = value[ii]
        localValuePerPoint = dataDimRef.localValuePerPoint
        if localValuePerPoint:
          dataDimRef.localValuePerPoint = localValuePerPoint*sw/oldsw
        else:
          dataDimRef.dataDim.valuePerPoint *= (sw/oldsw)

  @property
  def aliasingLimits(self) -> Tuple[Tuple[Optional[float], Optional[float]], ...]:
    """\- (*(float,float)*)\*dimensionCount

    tuple of tuples of (lowerAliasingLimit, higherAliasingLimit) for spectrum """
    result = [(x and x.minAliasedFreq, x and x.maxAliasedFreq) for x in self._mainExpDimRefs()]

    if any(None in tt for tt in result):
      # Some values not set, or missing. Try to get them as spectrum limits
      for ii,dataDimRef in enumerate(self._mainDataDimRefs()):
        if None in result[ii] and dataDimRef is not None:
          dataDim = dataDimRef.dataDim
          ff = dataDimRef.pointToValue
          point1 = 1 - dataDim.pointOffset
          result[ii] = tuple(sorted((ff(point1), ff(point1 + dataDim.numPointsOrig))))
    #
    return tuple(result)

  @aliasingLimits.setter
  def aliasingLimits(self, value):
    if len(value) != self.dimensionCount:
      raise ValueError("length of aliasingLimits must match spectrum dimension, was %s" % value)

    expDimRefs = self._mainExpDimRefs()
    for ii,tt in enumerate(value):
      expDimRef = expDimRefs[ii]
      if expDimRef:
        if len(tt) != 2:
          raise ValueError("Aliasing limits must have two value (min,max), was %s" % tt)
        expDimRef.minAliasedFreq = tt[0]
        expDimRef.maxAliasedFreq = tt[1]


  @property
  def spectrumLimits(self) -> Tuple[Tuple[Optional[float], Optional[float]], ...]:
    """\- (*(float,float)*)\*dimensionCount

    tuple of tuples of (lowerLimit, higherLimit) for spectrum """
    ll = []
    for ii,ddr in enumerate(self._mainDataDimRefs()):
      if ddr is None:
        ll.append((None,None))
      else:
        ll.append(tuple(sorted((ddr.pointToValue(1), ddr.pointToValue(ddr.dataDim.numPoints+1)))))
    return tuple(ll)

  @property
  def magnetisationTransfers(self) -> Tuple[MagnetisationTransferTuple, ...]:
    """tuple of MagnetisationTransferTuple describing magnetisation transfer between
    the spectrum dimensions.

    MagnetisationTransferTuple is a namedtuple with the fields
    ['dimension1', 'dimension2', 'transferType', 'isIndirect'] of types [int, int, str, bool]
    The dimensions are dimension numbers (one-origin]
    transfertype is one of (in order of increasing priority):
    'onebond', 'Jcoupling', 'Jmultibond', 'relayed', 'relayed-alternate', 'through-space'
    isIndirect is used where there is more than one successive transfer step;
    it is combined with the highest-priority transferType in the transfer path.

    The magnetisationTransfers are deduced from the experimentType and axisCodes.
    Only when the experimentType is unset or does not match any known reference experiment
    magnetisationTransfers are kept separately in the API layer.
    """

    result = []
    apiExperiment = self._wrappedData.experiment
    apiRefExperiment = apiExperiment.refExperiment

    if apiRefExperiment:
      # We should use the refExperiment - if present
      magnetisationTransferDict = apiRefExperiment.magnetisationTransferDict()
      refExpDimRefs = [x if x is None else x.refExpDimRef for x in self._mainExpDimRefs()]
      for ii, rxdr in enumerate(refExpDimRefs):
        dim1 = ii + 1
        if rxdr is not None:
          for jj in range(dim1, len(refExpDimRefs)):
            rxdr2 = refExpDimRefs[jj]
            if rxdr2 is not None:
              tt = magnetisationTransferDict.get(frozenset((rxdr, rxdr2)))
              if tt:
                result.append(MagnetisationTransferTuple(dim1, jj + 1, tt[0], tt[1]))

    else:
      # Without a refExperiment use parameters stored in the API (for reproducibility)
      ll = []
      for apiExpTransfer in apiExperiment.expTransfers:
        item = [x.expDim.dim for x in apiExpTransfer.expDimRefs]
        item.sort()
        item.append(apiExpTransfer.transferType)
        item.append(not(apiExpTransfer.isDirect))
        ll.append(item)
      for item in sorted(ll):
        result.append(MagnetisationTransferTuple(*item))


    #
    return tuple(result)

  def _setMagnetisationTransfers(self, value:Tuple[MagnetisationTransferTuple, ...]):
    """Setter for magnetisation transfers.


    The magnetisationTransfers are deduced from the experimentType and axisCodes.
    When the experimentType is set this function is a No-op.
    Only when the experimentType is unset or does not match any known reference experiment
    does this function set the magnetisation transfers, and the corresponding values are
    ignored if the experimentType is later set."""

    apiExperiment = self._wrappedData.experiment
    apiRefExperiment = apiExperiment.refExperiment
    if apiRefExperiment is None:
      for et in apiExperiment.expTransfers:
        et.delete()
      mainExpDimRefs = self._mainExpDimRefs()
      for tt in value:
        try:
          dim1, dim2, transferType, isIndirect = tt
          expDimRefs = (mainExpDimRefs[dim1 - 1], mainExpDimRefs[dim2 - 1])
        except:
          raise ValueError(
            "Attempt to set incorrect magnetisationTransfer value %s in spectrum %s"
            % (tt, self.pid)
          )
        apiExperiment.newExpTransfer(expDimRefs=expDimRefs, transferType=transferType,
                                     isDirect=(not isIndirect))
    else:
      apiRefExperiment.root._logger.warning(
  """An attempt to set Spectrum.magnetisationTransfers directly was ignored
because the spectrum experimentType was defined.
Use axisCodes to set magnetisation transfers instead.""")




  @property
  def intensities(self) -> numpy.ndarray:
    """ spectral intensities as NumPy array for 1D spectra """
    
    if self.dimensionCount != 1:
      raise Exception('Currently this method only works for 1D spectra')
      
    if self._intensities is None:
      self._intensities = self.getSliceData()
      # below not needed any more since now scaled in getSliceData()
      # if self._intensities is not None:
      #   self._intensities *= self.scale
      
    return self._intensities

  @property
  def positions(self) -> numpy.ndarray:
    """ spectral region in ppm as NumPy array for 1D spectra """
    
    if self.dimensionCount != 1:
      raise Exception('Currently this method only works for 1D spectra')
      
    if self._positions is None:
      spectrumLimits = self.spectrumLimits[0]
      pointCount = self.pointCounts[0]
      # WARNING: below assumes that spectrumLimits are "backwards" (as is true for ppm)
      scale = (spectrumLimits[0] - spectrumLimits[1]) / pointCount
      self._positions = spectrumLimits[1] + scale*numpy.arange(pointCount, dtype='float32')
      
    return self._positions

  # Implementation functions

  def rename(self, value:str):
    """Rename Spectrum, changing its name and Pid"""
    if value:
      self._startCommandEchoBlock('rename', value)
      try:
        self._wrappedData.name = value
      finally:
        self._endCommandEchoBlock()
    else:
      raise ValueError("Spectrum name must be set")

  @classmethod
  def _getAllWrappedData(cls, parent: Project)-> list:
    """get wrappedData (Nmr.DataSources) for all Spectrum children of parent Project"""
    return list(x for y in parent._wrappedData.sortedExperiments() for x in y.sortedDataSources())

  # Library functions

  def getPositionValue(self, position):

    return self._apiDataSource.getPositionValue(position)

  def getPlaneData(self, position=None, xDim:int=1, yDim:int=2):

    return self._apiDataSource.getPlaneData(position=position, xDim=xDim, yDim=yDim)

  def getSliceData(self, position=None, sliceDim:int=1):

    return self._apiDataSource.getSliceData(position=position, sliceDim=sliceDim)

  def automaticIntegration(self, spectralData):

    return self._apiDataSource.automaticIntegration(spectralData)

  def estimateNoise(self):
    return self._apiDataSource.estimateNoise()

  def projectedPlaneData(self, xDim:int=1, yDim:int=2, method:str='max'):
    return self._apiDataSource.projectedPlaneData(xDim, yDim, method)

  def projectedToFile(self, path:str, xDim:int=1, yDim:int=2, method:str='max', format:str=Formats.NMRPIPE):
    return self._apiDataSource.projectedToFile(path, xDim, yDim, method, format)

  def get1dSpectrumData(self):
    """Get position,scaledData numpy array for 1D spectrum.

    Gives first 1D slice for nD"""
    return self._apiDataSource.get1dSpectrumData()

  def reorderValues(self, values, newAxisCodeOrder):
    """Reorder values in spectrum dimension order to newAxisCodeOrder
    by matching newAxisCodeOrder to spectrum axis code order"""
    return commonUtil.reorder(values, self.axisCodes, newAxisCodeOrder)


  def getInAxisOrder(self, attributeName:str, axisCodes:Sequence[str]=None):
    """Get attributeName in order defined by axisCodes :
       (default order if None)
    """
    if not hasattr(self, attributeName):
      raise AttributeError('Spectrum object does not have attribute "%s"' % attributeName)

    values = getattr(self, attributeName)
    if axisCodes is None:
      return values
    else:
      # change to order defined by axisCodes
      return self.reorderValues(values, axisCodes)

  def setInAxisOrder(self, attributeName:str, values:Sequence, axisCodes:Sequence[str]=None):
    """Set attributeName from values in order defined by axisCodes
       (default order if None)
    """
    if not hasattr(self, attributeName):
      raise AttributeError('Spectrum object does not have attribute "%s"' % attributeName)

    if axisCodes is not None:
      # change values to the order appropriate for spectrum
      values = self.reorderValues(values, axisCodes)
    setattr(self, attributeName, values)

  def _clone1D(self):
    'Clone 1D spectrum to a new spectrum.'
    #FIXME Crude approach / hack

    newSpectrum = self.project.createDummySpectrum(name=self.name, axisCodes=self.axisCodes)
    newSpectrum._positions = self.positions
    newSpectrum._intensities = self.intensities
    for peakList in self.peakLists:
      peakList.copyTo(newSpectrum)

    import inspect
    attr = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
    filteredAttr = [a for a in attr if not (a[0].startswith('__') and a[0].endswith('__')) and not a[0].startswith('_')]
    for i in filteredAttr:
      att, val = i
      try:
        setattr(newSpectrum, att, val)
      except Exception as e:
        # print(e, att)
        pass
    return newSpectrum



def _newSpectrum(self:Project, name:str) -> Spectrum:
  """Creation of new Spectrum NOT IMPLEMENTED.
  Use Project.loadData or Project.createDummySpectrum instead"""

  raise NotImplementedError("Not implemented. Use loadSpectrum instead")


def _createDummySpectrum(self:Project, axisCodes:Sequence[str], name=None,
                         chemicalShiftList=None) -> Spectrum:
  """Make dummy spectrum from isotopeCodes list - without data and with default parameters """

  # TODO - change so isotopeCodes can be passed in instead of axisCodes

  apiShiftList = chemicalShiftList._wrappedData if chemicalShiftList else None

  if name:
    if Pid.altCharacter in name:
      raise ValueError("Character %s not allowed in ccpn.Spectrum.name" % Pid.altCharacter)
    values = {'name':name}
  else:
    values = {}

  self._startCommandEchoBlock('_createDummySpectrum', axisCodes, values=values,
                              parName='newSpectrum')
  try:
    result = self._data2Obj[self._wrappedData.createDummySpectrum(axisCodes, name=name,
                                                                  shiftList=apiShiftList)]
  finally:
    self._endCommandEchoBlock()
  return result

def _spectrumMakeFirstPeakList(project:Project, dataSource:Nmr.DataSource):
  """Add PeakList if none is present - also IntegralList for 1D. For notifiers."""
  if not dataSource.findFirstPeakList(dataType='Peak'):
    dataSource.newPeakList()
  if dataSource.numDim == 1 and not dataSource.findFirstPeakList(dataType='Integral'):
    dataSource.newPeakList(dataType='Integral')
Project._setupApiNotifier(_spectrumMakeFirstPeakList, Nmr.DataSource, 'postInit')
del _spectrumMakeFirstPeakList

# Connections to parents:

Project.newSpectrum = _newSpectrum
del _newSpectrum
Project.createDummySpectrum = _createDummySpectrum
del _createDummySpectrum

# Additional Notifiers:
Project._apiNotifiers.extend(
  (
    ('_finaliseApiRename', {}, Nmr.DataSource._metaclass.qualifiedName(), 'setName'),
    ('_notifyRelatedApiObject', {'pathToObject':'dataSources', 'action':'change'},
     Nmr.Experiment._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'dataSource', 'action':'change'},
     Nmr.AbstractDataDim._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'dataDim.dataSource', 'action':'change'},
     Nmr.DataDimRef._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'experiment.dataSources', 'action':'change'},
     Nmr.ExpDim._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'expDim.experiment.dataSources', 'action':'change'},
     Nmr.ExpDimRef._metaclass.qualifiedName(), ''),
    ('_notifyRelatedApiObject', {'pathToObject':'nmrDataSources', 'action':'change'},
     DataLocation.AbstractDataStore._metaclass.qualifiedName(), ''),
  )
)
