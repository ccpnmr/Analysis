"""
Settings used in gui modules, widgets and popups

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2016-11-15 21:37:50 +0000 (Tue, 15 Nov 2016) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: geertenv $"
__date__ = "$Date: 2016-11-15 21:37:50 +0000 (Tue, 15 Nov 2016) $"
__version__ = "$Revision: 9996 $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui
from ccpn.ui.gui.widgets.Font import Font

# fonts
monaco12              = Font('Monaco', 12)

helvetica12           = Font('Helvetica', 12)
helveticaItalic12     = Font('Helvetica', 12, italic=True)
helveticaBold12       = Font('Helvetica', 12, bold=True)
helveticaUnderline12  = Font('Helvetica', 12, underline=True)
helveticaStrikeout12  = Font('Helvetica', 12, strikeout=True)

helvetica14           = Font('Helvetica', 14)
helveticaBold14       = Font('Helvetica', 14, bold=True)

helvetica20           = Font('Helvetica', 20)
helveticaBold20       = Font('Helvetica', 20, bold=True)

lucidaGrande12        = Font('Lucida Grande', 12)
lucidaGrande14        = Font('Lucida Grande', 14)

# widgets and modules
textFont        = helvetica12        # general text font
textFontBold    = helveticaBold12    # general text font bold
textFontLarge   = helvetica14        # general text font large
textFontLargeBold = helveticaBold14  # general text font large bold
textFontHuge    = helvetica20        # general text font huge
textFontHugeBold = helveticaBold20   # general text font huge bold

fixedWidthFont  = monaco12           # for TextEditor, ipythonconsole
moduleLabelFont = helveticaBold12    # for text of left-label of modules
sidebarFont     = lucidaGrande12     # sidebar
menuFont        = lucidaGrande14     # Menus
messageFont     = helvetica14        # use in popup messages; does not seem to affect the dialog on OSX