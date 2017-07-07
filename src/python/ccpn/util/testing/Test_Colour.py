"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:07 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.util.Colour import Colour

from nose.tools import raises

@raises(TypeError)
def test_color_create_blank():
  c = Colour()

def test_color_create_known_name():
  c = Colour('red')

@raises(KeyError)
def test_color_create_unknown_name():
  c = Colour('really-red')

def test_color_create_hex():
  c = Colour('#ff00ff')
  print(c.name)
  c = Colour('#FF00FFFF')
  print(c.name)

def test_color_create_rgb():
  c = Colour((255, 0, 255))
  print(c.name)
  c = Colour((255, 0, 255, 127))
  print(c.name)


