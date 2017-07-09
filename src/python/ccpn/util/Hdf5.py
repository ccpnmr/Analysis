"""Module Documentation here

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
__dateModified__ = "$dateModified: 2017-07-07 16:32:58 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: rhf22 $"
__date__ = "$Date: 2016-05-16 02:12:40 +0100 (Mon, 16 May 2016) $"
#=========================================================================================
# Start of code
#=========================================================================================

import h5py
import numpy

from ccpn.core.Spectrum import Spectrum

SPECTRUM_DATASET_NAME = 'spectrumData'

def _cumulativeArray(array):
  ndim = len(array)
  cumul = ndim * [0]
  n = 1
  for i, size in enumerate(array):
    cumul[i] = n
    n = n * size

  return (n, cumul)

def _arrayOfIndex(index, cumul):
  ndim = len(cumul)
  array = ndim * [0]
  for i in range(ndim-1, -1, -1):
    c = cumul[i]
    array[i], index = divmod(index, c)
    
  return numpy.array(array)
  
def convertDataToHdf5(spectrum:Spectrum, outputPath:str):
  """ Convert binary data of spectrum into HDF5 and store at outputPath
      File suffix is made to end with .hdf5
  """
  if not outputPath.endswith('.hdf5'):
    n = outputPath.rfind('.')
    if n >= 0:
      outputPath = outputPath[:n]
    outputPath += '.hdf5'
    
  pointCounts = spectrum.pointCounts
  
  hdf5file = h5py.File(outputPath, 'w')
  dataset = hdf5file.create_dataset(SPECTRUM_DATASET_NAME, pointCounts[::-1], chunks=True, dtype='float32')
  attrs = dataset.attrs
  
  # attributes

  attrs['pointCounts'] = pointCounts
  attrs['blockSizes'] = dataset.chunks[::-1]
  for key in ('referenceValues', 'referencePoints', 'spectralWidths', 'spectrometerFrequencies'):
    attrs[key] = getattr(spectrum, key)
  for key in ('isotopeCodes',):
    attrs[key] = [bytes(value, 'utf-8') for value in getattr(spectrum, key)]

  attrs['spectralWidths'] *= attrs['spectrometerFrequencies'] # wrapper has sw in ppm not Hz
  
  dimensionCount = spectrum.dimensionCount
  if dimensionCount == 1:
    dataset[...] = spectrum.intensities #spectrum.getSliceData()
  else:
    pointCounts = numpy.array(pointCounts)
    (n, cumulPoints) = _cumulativeArray(pointCounts[2:])
    position = numpy.ones(dimensionCount, dtype='int32') # position values start at 1, not 0
    slices = dimensionCount * [0]
    for i in range(2):
      slices[dimensionCount-i-1] = slice(pointCounts[i])
    for j in range(n):
      position[2:] = 1 + _arrayOfIndex(j, cumulPoints) # position values start at 1, not 0
      for i in range(2, dimensionCount):
        slices[dimensionCount-i-1] = slice(position[i]-1, position[i])
      dataset[tuple(slices)] = spectrum.getPlaneData(tuple(position))

  hdf5file.close()
