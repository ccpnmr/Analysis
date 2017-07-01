# df = pd.DataFrame({
#   'sampleName': ['Sample1', 'Sample1', 'Sample1', 'Sample2', 'Sample2', 'Sample2'],
#   'sampleComponents': ['DT', 'Org', 'Org', 'VBN', ' IN', 'Location'],
#   'pH': [5, 5, 5, 3, 3, 3]
#
# })
# df.groupby('sampleName', sort=False)['pH'].apply(set)


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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


import os
from os.path import isfile, join
import pathlib
import pandas as pd
from ccpn.util.Logging import getLogger , _debug3

######################### Excel Headers ##################
"""The excel headers for sample, sampleComponents, substances properties are named as the appear on the wrapper.
Changing these will fail to set the attribute"""

# SHEET NAMES
SUBSTANCES = 'Substances'
SAMPLES = 'Samples'
NOTGIVEN = 'Not Given'

# '''REFERENCES PAGE'''
SPECTRUM_GROUP_NAME = 'spectrumGroupName'
EXP_TYPE = 'expType'
SPECTRUM_PATH = 'spectrumPath'
SUBSTANCE_NAME = 'substanceName'
### Substance properties: # do not change these names
comment  = 'comment'
smiles = 'smiles'
synonyms = 'synonyms'
stereoInfo = 'stereoInfo'
molecularMass = 'molecularMass'
empiricalFormula = 'empiricalFormula'
atomCount = 'atomCount'
hBondAcceptorCount = 'hBondAcceptorCount'
hBondDonorCount = 'hBondDonorCount'
bondCount = 'bondCount'
ringCount = 'ringCount'
polarSurfaceArea = 'polarSurfaceArea'
logPartitionCoefficient = 'logPartitionCoefficient'
userCode = 'userCode'
sequenceString = 'sequenceString'
casNumber = 'casNumber'

# '''SAMPLES PAGE'''
SAMPLE_NAME = 'sampleName'

### other sample properties # do not change these names
SAMPLE_COMPONENTS = 'referenceComponents'
pH = 'pH'
ionicStrength = 'ionicStrength'
amount = 'amount'
amountUnit = 'amountUnit'
isHazardous = 'isHazardous'
creationDate = 'creationDate'
batchIdentifier = 'batchIdentifier'
plateIdentifier = 'plateIdentifier'
rowNumber = 'rowNumber'
columnNumber = 'columnNumber'


SAMPLE_PROPERTIES =     [comment, pH, ionicStrength,  amount , amountUnit,isHazardous,creationDate, batchIdentifier,
                         plateIdentifier,rowNumber,columnNumber]

SUBSTANCE_PROPERTIES =  [comment,smiles,synonyms,stereoInfo,molecularMass,empiricalFormula,atomCount,
                         hBondAcceptorCount,hBondDonorCount, bondCount,ringCount,polarSurfaceArea,
                         logPartitionCoefficient,userCode,]



class ExcelReader(object):
  def __init__(self, project, excelPath):
    """
    :param project: the ccpnmr Project object
    :param excelPath: excel file path

    This reader will process excel files containing one or more sheets.
    The file needs to contain  either the word Substances or Samples in the sheets name.

    The user can load a file only with Substances or Samples sheet or both. Or a file with enumerate sheets
    called eg Samples_Exp_1000, Samples_Exp_1001 etc.

    The project will create new Substances and/or Samples and SpectrumGroups only once for a given name.
    Therefore, dropping twice the same file, or giving two sheets with same sample/substance/spectrumGroup name
    will fail to create new objects.



    Reader Steps:

    - Parse the sheet/s and return a dataframe for each sheet containing at least the str name Substances or Samples
    - Create Substances and/or samples if not existing in the project else skip with warning
    - For each row create a dict and link to the obj eg. {Substance: {its dataframe row as dict}
    - Create SpectrumGroups if not existing in the project else add a suffix 
    - Load spectra on project and dispatch to the object. (e.g. SU.referenceSpectra, SA.spectra, SG.spectra)
    - set all attributes for each object as in the wrapper


    """

    self._project = project
    self.excelPath = excelPath
    self.pandasFile = pd.ExcelFile(self.excelPath)
    self.sheets = self._getSheets(self.pandasFile)
    self.dataframes = self._getDataFrameFromSheets(self.sheets)

    self.substancesDicts = self._createSubstancesDataFrames(self.dataframes)
    self.spectrumGroups = self._createSpectrumGroups(self.dataframes)

    self._dispatchAttrsToObjs(self.substancesDicts)
    self._loadSpectraForSheet(self.substancesDicts)

    self.samplesDicts = self._createSamplesDataDicts(self.dataframes)
    self._dispatchAttrsToObjs(self.samplesDicts)
    self._loadSpectraForSheet(self.samplesDicts)






    # self._loadReferenceSpectrumToProject()
    # self._createReferencesDataDicts()
    # self._initialiseParsingSamples()

  ######################################################################################################################
  ######################                  PARSE EXCEL                     ##############################################
  ######################################################################################################################

  def _getSheets(self, pandasfile):
    '''return: list of the sheet names'''
    return  pandasfile.sheet_names

  def _getDataFrameFromSheet(self, sheetName):
    'Creates the dataframe for the sheet. If Values are not set, fills None with NOTGIVEN (otherwise can give errors)'
    dataFrame = self.pandasFile.parse(sheetName)
    dataFrame.fillna(NOTGIVEN, inplace=True)
    return dataFrame

  def _getDataFrameFromSheets(self, sheetNamesList):
    '''Reads sheets containing the names SUBSTANCES or SAMPLES and creates a dataFrame for each'''

    dataFrames = []
    for sheetName in [name for name in sheetNamesList if SUBSTANCES in name]:
      dataFrames.append(self._getDataFrameFromSheet(sheetName))
    for sheetName in [name for name in sheetNamesList if SAMPLES in name]:
      dataFrames.append(self._getDataFrameFromSheet(sheetName))

    return dataFrames



  ######################################################################################################################
  ######################                  CREATE SUBSTANCES               ##############################################
  ######################################################################################################################

  def _createSubstancesDataFrames(self, dataframesList):
    '''Creates substances in the project if not already present, For each substance link a dictionary of all its values
     from the dataframe row. '''

    substancesDataFrames = []
    for dataFrame in dataframesList:
      for dataFrameAsDict in dataFrame.to_dict(orient="index").values():
        if SUBSTANCE_NAME in dataFrame.columns:
          for key, value in dataFrameAsDict.items():
            if key == SUBSTANCE_NAME:
              if self._project is not None:
                if not self._project.getByPid('SU:'+str(value)+'.'):
                  substance = self._project.newSubstance(name=str(value))
                  substancesDataFrames.append({substance:dataFrameAsDict})
                else:
                  getLogger().warning('Impossible to create substance %s. A substance with the same name already '
                                      'exsists in the project. ' % value)

    return substancesDataFrames



  ######################################################################################################################
  ######################                  CREATE SAMPLES                  ##############################################
  ######################################################################################################################

  def _createSamplesDataDicts(self, dataframesList):
    '''Creates samples in the project if not already present , For each sample link a dictionary of all its values
     from the dataframe row. '''

    samplesDataFrames = []
    for dataFrame in dataframesList:
      for dataFrameAsDict in dataFrame.to_dict(orient="index").values():
        if SAMPLE_NAME in dataFrame.columns:
          for key, value in dataFrameAsDict.items():
            if key == SAMPLE_NAME:
              if self._project is not None:
                if not self._project.getByPid('SA:'+str(value)):
                  sample = self._project.newSample(name=str(value))

                else:
                  getLogger().warning('Impossible to create sample %s. A sample with the same name already '
                                      'exsists in the project. ' % value)

                sample = self._project.getByPid('SA:'+str(value))
                if sample is not None:
                  samplesDataFrames.append({sample: dataFrameAsDict})

    return samplesDataFrames


  ######################################################################################################################
  ######################            CREATE SPECTRUM GROUPS                ##############################################
  ######################################################################################################################



  def _createSpectrumGroups(self, dataframesList):
    '''Creates SpectrumGroup in the project if not already present. Otherwise finds another name a creates new one.
    dropping the same file over and over will create new spectrum groups each time'''
    spectrumGroups = []
    for dataFrame in dataframesList:
      if SPECTRUM_GROUP_NAME in dataFrame.columns:
        for groupName in list(set((dataFrame[SPECTRUM_GROUP_NAME]))):
          # name = self._checkDuplicatedSpectrumGroupName(groupName)
          newSG =  self._createNewSpectrumGroup(groupName)
          spectrumGroups.append(newSG)
    return spectrumGroups

  ##keep this code
  # def _checkDuplicatedSpectrumGroupName(self, name):
  #   'Checks in the preject if a spectrumGroup name exists already and returns a new available name '
  #   if self._project:
  #     for sg in self._project.spectrumGroups:
  #       if sg.name == name:
  #         name += '@'
  #     return name

  def _createNewSpectrumGroup(self, name):
    if self._project:
      if not self._project.getByPid('SG:' + name):
        return self._project.newSpectrumGroup(name=str(name))
      else:
        getLogger().warning('Impossible to create the spectrumGroup %s. A spectrumGroup with the same name already '
                            'exsists in the project. ' % name)

        # name = self._checkDuplicatedSpectrumGroupName(name)
        # self._createNewSpectrumGroup(name)


  ######################################################################################################################
  ######################             LOAD SPECTRA ON PROJECT              ##############################################
  ######################################################################################################################


  def _loadSpectraForSheet(self, dictLists):
    '''
    If only the file name is given:
    - All paths are relative to the excel file! So the spectrum file of bruker top directory must be in the same directory
    of the excel file.
    If the full path is given, from the root to the spectrum file name, then it uses that.
    '''
    if self._project is not None:
      for objDict in dictLists:
        for obj , dct in objDict.items():
          for key, value in dct.items():
            # for path in dataFrame[SPECTRUM_PATH]:
            if key == SPECTRUM_PATH:
              if os.path.exists(value):                     ### the full path is given:
                data = self._project.loadData(value)
                if data is not None:
                  if len(data)>0:
                    data[0].filePath = value
                    self._linkSpectrumToObj(obj, data[0],dct)

              else:                                        ### needs to find the path from the excel file:
                self.directoryPath = str(pathlib.Path(self.excelPath).parent)
                filePath = self.directoryPath+'/'+value
                if os.path.exists(filePath):               ### is a folder, e.g Bruker type. The project can handle.
                  data = self._project.loadData(filePath)
                  if data is not None:
                    if len(data) > 0:
                      data[0].filePath = filePath
                      self._linkSpectrumToObj(obj, data[0],dct)

                else:                       ### is a spectrum file, The project needs to get the extension: e.g .hdf5
                  filesWithExtension = [f for f in os.listdir(self.directoryPath) if isfile(join(self.directoryPath, f))]
                  for fileWithExtension in filesWithExtension:
                    if len(os.path.splitext(fileWithExtension))>0:
                      if os.path.splitext(fileWithExtension)[0] == value:
                        filePath = self.directoryPath + '/' + fileWithExtension
                        data = self._project.loadData(filePath)
                        if data is not None:
                          if len(data)>0:
                            data[0].filePath = filePath
                            self._linkSpectrumToObj(obj, data[0],dct)


  ######################################################################################################################
  ######################              ADD SPECTRUM TO RELATIVE OBJECTS              ####################################
  ######################################################################################################################


  def _linkSpectrumToObj(self, obj, spectrum, dct):
    from ccpn.core.Sample import Sample
    from ccpn.core.Substance import Substance

    if isinstance(obj, Substance):
      obj.referenceSpectra += (spectrum,)

    if isinstance(obj, Sample):
      obj.spectra += (spectrum,)

    for key, value in dct.items():
      if key == SPECTRUM_GROUP_NAME:
        spectrumGroup = self._project.getByPid('SG:'+str(value))
        if spectrumGroup is not None:
          spectrumGroup.spectra += (spectrum,)


  ######################################################################################################################
  ######################            DISPATCH ATTRIBUTES TO RELATIVE OBJECTS         ####################################
  ######################################################################################################################


  def _dispatchAttrsToObjs(self, dataDicts):
    from ccpn.core.Sample import Sample
    from ccpn.core.Substance import Substance

    for objDict in dataDicts:
      for obj, dct in objDict.items():
        if isinstance(obj, Substance):
          self._setWrapperProperties(obj, SUBSTANCE_PROPERTIES, dct)

        if isinstance(obj, Sample):
          self._setWrapperProperties(obj, SAMPLE_PROPERTIES, dct)


  def _setWrapperProperties(self, wrapperObject, properties, dataframe):
    for property in properties:
      if property == 'synonyms':
        setattr(wrapperObject, property, (self._getDFValue(property, dataframe),))
      else:
        try:
          setattr(wrapperObject, property, self._getDFValue(property, dataframe))
        except Exception as e:
          _debug3(getLogger(), msg=(e, property))


  def _getDFValue(self, header, data):
    value = [[excelHeader, value] for excelHeader, value in data.items()
                     if excelHeader == str(header) and value != NOTGIVEN]
    if len(value) > 0:
      return value[0][1]



  ######################################################################################################################
  ######################                    ADD SAMPLE COMPONENTS                   ####################################
  ######################################################################################################################

  def _addSampleComponents(self, sample, data):
    sampleComponents = [[header, sampleComponentName] for header, sampleComponentName in data.items() if
                        header == SAMPLE_COMPONENTS]
    for name in sampleComponents[0][1].split(','):
      sampleComponent = sample.newSampleComponent(name=(str(name) + '-1'))
      sampleComponent.role = 'Compound'








if False:
  ExcelReader(project=None, excelPath='/Users/luca/AnalysisV3/data/testProjects/AnalysisScreen_Demo1/demoDataset_Lookup/Lookup_Demo.xls')