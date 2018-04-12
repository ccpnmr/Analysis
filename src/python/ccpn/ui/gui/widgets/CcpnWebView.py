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
__dateModified__ = "$dateModified: 2017-07-07 16:32:52 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from ccpn.ui.gui.modules.CcpnModule import CcpnModule


class CcpnWebView(CcpnModule):

  className = 'CcpnWebView'

  def __init__(self, mainWindow=None, name='CcpNmr V3 Documentation', urlPath=None):
    """
    Initialise the Module widgets
    """
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name)

    self.webView = QWebEngineView()
    self.addWidget(self.webView, 0, 0, 1, 1)  # make it the first item

    urlPath = 'file://'+urlPath               # webEngine needs to prefix
    self.webView.load(QUrl(urlPath))
    self.webView.show()

  def __del__(self):
    del self.webView
    # super(CcpnWebView, self).__del__()

  def _closeModule(self):
    self.close()