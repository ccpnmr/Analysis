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
__dateModified__ = "$dateModified: 2017-07-07 16:32:37 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


from ccpn.framework.lib.Extension import ExtensionABC



class Hair(ExtensionABC):
  METHODNAME = 'Useless Extension 1'

  def runMethod(self, dataset):
    return 1



class Fingernail(ExtensionABC):
  METHODNAME = 'Useless Extension 1'

  def runMethod(self, dataset):
    return 2



class UselessNotExtension1:
  METHODNAME = 'Useless Not Extension 1'

  def runMethod(self, dataset):
    return



class UselessNotExtension2:
  METHODNAME = 'Useless Not Extension 2'

  def runMethod(self, dataset):
    return
