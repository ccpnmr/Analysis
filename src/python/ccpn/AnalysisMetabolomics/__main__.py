__author__ = 'TJ'

from ccpn.core.lib.Version import applicationVersion
from ccpn.framework import Framework
from ccpn.AnalysisMetabolomics.AnalysisMetabolomics import Metabolomics as Application


if __name__ == '__main__':

  # argument parser
  parser = Framework.defineProgramArguments()

  # add any additional commandline argument here
  commandLineArguments = parser.parse_args()

  application = Application('AnalysisMetabolomics', '3.0.a1', commandLineArguments)
  Framework._getApplication = lambda: application
  application.start()
