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
__dateModified__ = "$dateModified: 2017-07-07 16:32:32 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import numpy as np
from ccpn.util.Logging import getLogger
from collections import OrderedDict

POSITIONS = 'positions'
HEIGHT = 'height'
VOLUME = 'volume'
LINEWIDTHS = 'lineWidths'

MODES = [POSITIONS, HEIGHT, VOLUME, LINEWIDTHS]
OTHER = 'Other'
H = 'H'
N = 'N'
C = 'C'
DefaultAtomWeights = OrderedDict(((H, 7.00), (N, 1.00), (C, 4.00), (OTHER, 1.00)))

def getMultipletPosition(multiplet, dim, unit='ppm'):
    try:
      if multiplet.position[dim] is None:
        value = None              #"*NOT SET*"

      elif unit == 'ppm':
        value = multiplet.position[dim]

      #  NOT implemented for multiplets
      # elif unit == 'point':
      #   value = multiplet.pointPosition[dim]

      elif unit == 'Hz':
        # value = peak.position[dim]*peak._apiPeak.sortedPeakDims()[dim].dataDimRef.expDimRef.sf
        value = multiplet.position[dim] * multiplet.multipletList.spectrum.spectrometerFrequencies[dim]

      else: # sampled
        # value = unit.pointValues[int(peak._apiPeak.sortedPeakDims()[dim].position)-1]
        raise ValueError("Unit passed to getPeakPosition must be 'ppm', 'point', or 'Hz', was %s"
                       % unit)

      if isinstance(value, (int, float, np.float32, np.float64)):
        return '{0:.2f}'.format(value)
    except:
      print('Testing FAILED')
  # return None

def getMultipletLinewidth(peak, dim):
  if dim < len(peak.lineWidths):
    lw = peak.lineWidths[dim]
    if lw:
      return float(lw)

def getPeakPosition(peak, dim, unit='ppm'):

  if len(peak.dimensionNmrAtoms) > dim:
    # peakDim = peak.position[dim]

    if peak.position[dim] is None:
      value = None              #"*NOT SET*"

    elif unit == 'ppm':
      value = peak.position[dim]

    elif unit == 'point':
      value = peak.pointPosition[dim]

    elif unit == 'Hz':
      # value = peak.position[dim]*peak._apiPeak.sortedPeakDims()[dim].dataDimRef.expDimRef.sf
      value = peak.position[dim]*peak.peakList.spectrum.spectrometerFrequencies[dim]

    else: # sampled
      # value = unit.pointValues[int(peak._apiPeak.sortedPeakDims()[dim].position)-1]
      raise ValueError("Unit passed to getPeakPosition must be 'ppm', 'point', or 'Hz', was %s"
                     % unit)

    if isinstance(value, (int, float, np.float32, np.float64)):
      return '{0:.2f}'.format(value)

    return None

    # if isinstance(value, [int, float]):
    # # if type(value) is int or type(value) in (float, float32, float64):
    #   return '%7.2f' % float(value)

def getPeakAnnotation(peak, dim, separator=', '):
  if len(peak.dimensionNmrAtoms) > dim:
    return separator.join([dna.pid.id for dna in peak.dimensionNmrAtoms[dim]])

def getPeakLinewidth(peak, dim):
  if dim < len(peak.lineWidths):
    lw = peak.lineWidths[dim]
    if lw:
      return float(lw)

def _get1DPeaksPosAndHeightAsArray(peakList):
  import numpy as np
  positions = np.array([peak.position[0] for peak in peakList.peaks])
  heights = np.array([peak.height for peak in peakList.peaks])
  return [positions, heights]



import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array


def peakdet(v, delta, x=None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    """
    maxtab = []
    mintab = []

    if x is None:
        x = arange(len(v))

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN

    lookformax = True

    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx - delta:
                maxtab.append((float(mxpos), float(mx)))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((float(mnpos), float(mn)))
                mx = this
                mxpos = x[i]
                lookformax = True

    return maxtab, mintab

def _estimateDeltaPeakDetect(y,xPercent=20):
  deltas = y[1:] - y[:-1]
  delta = np.std(np.absolute(deltas))

  # just on the noisy part of spectrum
  partialYpercent = (len(y)*xPercent)/100
  partialY = y[:int(partialYpercent)]
  partialDeltas = partialY[1:] - partialY[:-1]
  partialDelta = np.std(np.absolute(partialDeltas))

  if delta > partialDelta:
    return delta
  else:
    return partialDelta


def _getAtomWeight(axisCode, atomWeights) -> float or int:
  '''

  :param axisCode: str of peak axis code
  :param atomWeights: dictionary of atomWeights eg {'H': 7.00, 'N': 1.00, 'C': 4.00, 'Other': 1.00}
  :return: float or int from dict atomWeights
  '''
  value = 1.0
  if len(axisCode) > 0:
    firstLetterAxisCode = axisCode[0]
    if firstLetterAxisCode in atomWeights:
      value = atomWeights[firstLetterAxisCode]
    else:
      if OTHER in atomWeights:
        if atomWeights[OTHER] != 1:
          value = atomWeights[OTHER]
      else:
        value = 1.0

  return value


def _traverse(o, tree_types=(list, tuple)):
  '''used to flat the state in a long list '''
  if isinstance(o, tree_types):
    for value in o:
      for subvalue in _traverse(value, tree_types):
        yield subvalue
  else:
    yield o

def __filterPeaksBySelectedNmrAtomOption(nmrResidue, nmrAtomsNames, spectra):
  peaks = []
  nmrAtoms = []
  for nmrAtomName in nmrAtomsNames:
    nmrAtom = nmrResidue.getNmrAtom(str(nmrAtomName))
    if nmrAtom is not None:
      nmrAtoms.append(nmrAtom)
  filteredPeaks = []
  nmrAtomsNamesAvailable = []
  for nmrAtom in nmrAtoms:
    for peak in nmrAtom.assignedPeaks:
      if peak.peakList.spectrum in spectra:
        if nmrAtom.name in nmrAtomsNames:
          filteredPeaks.append(peak)
          nmrAtomsNamesAvailable.append(nmrAtom.name)
  if len(list(set(filteredPeaks))) == len(spectra): # deals when a residue is assigned to multiple peaks
    if len(list(set(nmrAtomsNamesAvailable))) == len(nmrAtomsNames):
      peaks += filteredPeaks
  else:
    for peak in filteredPeaks:
      assignedNmrAtoms = _traverse(peak.assignedNmrAtoms)
      if all(assignedNmrAtoms):
        assignedNmrAtoms = [na.name for na in assignedNmrAtoms]
        if len(assignedNmrAtoms) > 1:
          if list(assignedNmrAtoms) == nmrAtomsNames:
            peaks += [peak]
        if len(nmrAtomsNames) == 1:
          if nmrAtomsNames[0] in assignedNmrAtoms:
            peaks += [peak]
  return peaks

def getNmrResidueDeltas(nmrResidue, nmrAtomsNames, spectra, mode=POSITIONS, atomWeights=None):
  '''
  
  :param nmrResidue: 
  :param nmrAtomsNames: nmr Atoms to compare. str 'H' , 'N' , 'CA' etc
  :param spectra: compare peaks only from given spectra
  :return: 
  '''

  deltas = []

  if len(spectra) <=1:
    return
  peaks = __filterPeaksBySelectedNmrAtomOption(nmrResidue, nmrAtomsNames, spectra)

  if atomWeights is None:
    atomWeights = DefaultAtomWeights

  if len(peaks)>0:
    for peak in peaks:
      if peak.peakList.spectrum in spectra:
        try: #some None value can get in here
          if mode == POSITIONS:
            delta = None
            for i, axisCode in enumerate(peak.axisCodes):
              if len(axisCode)>0:
                if any(s.startswith(axisCode[0]) for s in nmrAtomsNames):
                  weight = _getAtomWeight(axisCode, atomWeights)
                  if delta is None:
                    delta = 0.0
                  delta += ((peak.position[i] - list(peaks)[0].position[i]) * weight) ** 2
            if delta is not None:
              delta = delta ** 0.5
              deltas += [delta]

          if mode == VOLUME:
            delta1Atoms = (peak.volume - list(peaks)[0].volume)
            deltas += [((delta1Atoms)** 2 ) ** 0.5,]

          if mode == HEIGHT:
            delta1Atoms = (peak.height - list(peaks)[0].height)
            deltas += [((delta1Atoms) ** 2) ** 0.5,]

          if mode == LINEWIDTHS:
            delta = None
            for i, axisCode in enumerate(peak.axisCodes):
              if axisCode:
                if len(axisCode) > 0:
                  if any(s.startswith(axisCode[0]) for s in nmrAtomsNames):
                    weight = _getAtomWeight(axisCode, atomWeights)
                    if delta is None:
                      delta = 0.0
                    delta += ((peak.lineWidths[i] - list(peaks)[0].lineWidths[i]) * weight) ** 2
            if delta is not None:
              delta = delta ** 0.5
              deltas += [delta]

        except Exception as e:
          message = 'Error for calculation mode: %s on %s and %s. ' % (mode, peak.pid, list(peaks)[0].pid) + str(e)
          getLogger().debug(message)




  if deltas and not None in deltas:
    return round(float(np.mean(deltas)),3)
  return



































