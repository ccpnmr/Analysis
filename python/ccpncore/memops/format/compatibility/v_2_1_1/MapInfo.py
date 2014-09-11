"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = "$Revision: 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

# Packages, classElements and AbstractDataTypes skipped in new model
# (prefix, typeName, elemName, newGuid, elemType)
skipElements = [
 (None, None, None, 'www.ccpn.ac.uk_Fogh_2006-08-17-14:16:20_00001', 'MetaPackage'), 
 ('ACCO', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00015', 'MetaPackage'), 
 ('AFFI', 'Group', 'experiments', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:15_00001', 'MetaRole'), 
 ('AFFI', 'Person', 'createdExps', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:47_00009', 'MetaRole'), 
 ('AFFI', 'Person', 'createdProtocols', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:51_00002', 'MetaRole'), 
 ('AFFI', 'Person', 'dropAnnotations', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:36_00003', 'MetaRole'), 
 ('AFFI', 'Person', 'editedExps', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:47_00011', 'MetaRole'), 
 ('AFFI', 'Person', 'editedProtocols', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:51_00004', 'MetaRole'), 
 ('AFFI', 'Person', 'expBlueprints', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00002', 'MetaRole'), 
 ('AFFI', 'Person', 'targets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00019', 'MetaRole'), 
 ('AFFI', 'Person', 'users', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00009', 'MetaRole'), 
 ('ANNO', 'Annotation', 'experiments', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00105', 'MetaRole'), 
 ('ANNO', 'Annotation', 'projects', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:18_00018', 'MetaRole'), 
 ('ANNO', 'Annotation', 'targetGroups', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00107', 'MetaRole'), 
 ('ANNO', 'Annotation', 'targets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00023', 'MetaRole'), 
 ('CITA', 'Citation', 'protocols', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:51_00006', 'MetaRole'), 
 ('CITA', 'Citation', 'targetGroups', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:18_00030', 'MetaRole'), 
 ('CITA', 'Citation', 'targets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00021', 'MetaRole'), 
 ('CLAS', None, None, 'www.ccpn.ac.uk_Fogh_2006-09-04-17:18:54_00001', 'MetaPackage'), 
 ('COOR', 'StructureEnsemble', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00003', 'MetaRole'), 
 ('COOR', 'StructureEnsemble', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00039', 'MetaRole'), 
 ('CRYZ', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00056', 'MetaPackage'), 
 ('DBR', 'Entry', 'blueprintDbRefs', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:18_00058', 'MetaRole'), 
 ('DBR', 'Entry', 'targetGroups', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:18_00032', 'MetaRole'), 
 ('DBR', 'Entry', 'targets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00029', 'MetaRole'), 
 ('EXPB', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:51_00041', 'MetaPackage'), 
 ('EXPE', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:44_00010', 'MetaPackage'), 
 ('HOLD', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:52_00042', 'MetaPackage'), 
 ('IMPL', 'AppDataDouble', None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00042', 'MetaDataObjType'), 
 ('IMPL', 'AppDataLong', None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00040', 'MetaDataObjType'), 
 ('IMPL', 'DataObject', 'access', 'www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014', 'MetaRole'), 
 ('IMPL', 'Double', None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00030', 'MetaDataType'), 
 ('IMPL', 'Long', None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00034', 'MetaDataType'), 
 ('IMPL', 'MemopsRoot', 'accessControlStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.accessControlStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'analysisProfiles', 'ccpn_automatic_memops.Implementation.MemopsRoot.analysisProfile', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'analysisProjectV3s', 'www.ccpn.ac.uk_Fogh_2011-11-30-11:04:35_00010', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'analysisProjects', 'ccpn_automatic_memops.Implementation.MemopsRoot.analysisProject', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'analysisWindowStores', 'www.ccpn.ac.uk_Fogh_2011-11-30-11:04:35_00008', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'classifications', 'ccpn_automatic_memops.Implementation.MemopsRoot.classification', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'crystallizationStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.crystallizationStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentAccessControlStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentAccessControlStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentAnalysisProfile', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentAnalysisProfile', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentAnalysisProject', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentAnalysisProject', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentAnalysisProjectV3', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentAnalysisProjectV3', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentAnalysisWindowStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentAnalysisWindowStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentClassification', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentClassification', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentCrystallizationStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentCrystallizationStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentExpBlueprintStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentExpBlueprintStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentExperimentStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentExperimentStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentHolderStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentHolderStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentLayout', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentLayout', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentLocationStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentLocationStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentNameMappingStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentNameMappingStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentProtocolStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentProtocolStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentTargetStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentTargetStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentWmsQueryStore', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentWmsQueryStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'currentWmsSegment', 'ccpn_automatic_memops.Implementation.MemopsRoot.currentWmsSegment', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'expBlueprintStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.expBlueprintStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'experimentStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.experimentStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'holderStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.holderStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'layouts', 'www.ccpn.ac.uk_Fogh_2011-11-30-11:04:35_00012', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'locationStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.locationStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'nameMappingStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.nameMappingStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'protocolStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.protocolStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'targetStores', 'ccpn_automatic_memops.Implementation.MemopsRoot.targetStore', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'wmsProtocols', 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00062', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'wmsQueryStores', 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00064', 'MetaRole'), 
 ('IMPL', 'MemopsRoot', 'wmsSegments', 'www.ccpn.ac.uk_Fogh_2009-01-29-15:16:54_00002', 'MetaRole'), 
 ('IMPL', 'NegativeDouble', None, 'www.ccpn.ac.uk_Fogh_2008-05-29-14:27:55_00005', 'MetaDataType'), 
 ('IMPL', 'NonNegativeDouble', None, 'www.ccpn.ac.uk_Fogh_2007-12-11-18:15:49_00003', 'MetaDataType'), 
 ('IMPL', 'PaperFormat', None, 'www.ccpn.ac.uk_Fogh_2008-05-05-15:12:50_00010', 'MetaDataType'), 
 ('IMPL', 'PaperOrientation', None, 'www.ccpn.ac.uk_Fogh_2008-05-05-15:12:50_00013', 'MetaDataType'), 
 ('IMPL', 'PaperUnit', None, 'www.ccpn.ac.uk_Fogh_2008-05-05-15:12:50_00011', 'MetaDataType'), 
 ('IMPL', 'PositiveDouble', None, 'www.ccpn.ac.uk_Fogh_2007-12-11-18:15:49_00001', 'MetaDataType'), 
 ('IMPL', 'PrintFormat', None, 'www.ccpn.ac.uk_Fogh_2008-05-05-15:12:50_00012', 'MetaDataType'), 
 ('IMPL', 'Text', None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00036', 'MetaDataType'), 
 ('INST', 'Instrument', 'experiments', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:47_00002', 'MetaRole'), 
 ('INST', 'Instrument', 'instrumentTypes', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:04_00006', 'MetaRole'), 
 ('LOCA', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00063', 'MetaPackage'), 
 ('METH', 'Method', 'experiments', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:48_00005', 'MetaRole'), 
 ('METH', 'Software', 'dropAnnotations', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:35_00068', 'MetaRole'), 
 ('MOLS', 'Chain', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00007', 'MetaRole'), 
 ('MOLS', 'Chain', 'analysisPanel', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00035', 'MetaRole'), 
 ('MOLS', 'MolSystem', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00005', 'MetaRole'), 
 ('MOLS', 'MolSystem', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00037', 'MetaRole'), 
 ('NMR', 'AbstractDataDim', 'analysisDataDim', 'www.ccpn.ac.uk_Fogh_2008-05-05-18:37:56_00002', 'MetaRole'), 
 ('NMR', 'AbstractDataDim', 'analysisDataDims', 'www.ccpn.ac.uk_Fogh_2011-11-30-10:53:58_00001', 'MetaRole'), 
 ('NMR', 'DataSource', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00019', 'MetaRole'), 
 ('NMR', 'DataSource', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00023', 'MetaRole'), 
 ('NMR', 'DataSource', 'analysisSpectra', 'www.ccpn.ac.uk_Fogh_2011-11-30-11:04:36_00002', 'MetaRole'), 
 ('NMR', 'DataSource', 'analysisSpectrum', 'www.ccpn.ac.uk_Fogh_2008-05-05-17:24:14_00009', 'MetaRole'), 
 ('NMR', 'NmrProject', 'analysisProject', 'www.ccpn.ac.uk_Fogh_2006-08-24-15:51:17_00001', 'MetaRole'), 
 ('NMR', 'NmrProject', 'analysisProjectV3', 'www.ccpn.ac.uk_Fogh_2011-12-01-15:00:59_00003', 'MetaRole'), 
 ('NMR', 'Peak', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00015', 'MetaRole'), 
 ('NMR', 'Peak', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00027', 'MetaRole'), 
 ('NMR', 'PeakList', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00017', 'MetaRole'), 
 ('NMR', 'PeakList', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00025', 'MetaRole'), 
 ('NMR', 'PeakList', 'analysisPeakList', 'www.ccpn.ac.uk_Fogh_2008-05-05-18:37:55_00009', 'MetaRole'), 
 ('NMR', 'PeakList', 'analysisPeakLists', 'www.ccpn.ac.uk_Fogh_2011-11-30-11:04:36_00004', 'MetaRole'), 
 ('NMR', 'Resonance', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00011', 'MetaRole'), 
 ('NMR', 'Resonance', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00031', 'MetaRole'), 
 ('NMR', 'ResonanceGroup', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00009', 'MetaRole'), 
 ('NMR', 'ResonanceGroup', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00033', 'MetaRole'), 
 ('NMRC', 'NmrConstraintStore', 'analysisLayouts', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00013', 'MetaRole'), 
 ('NMRC', 'NmrConstraintStore', 'analysisPanels', 'www.ccpn.ac.uk_Fogh_2011-12-02-15:08:31_00029', 'MetaRole'), 
 ('PROT', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:44_00017', 'MetaPackage'), 
 ('REFS', 'AbstractComponent', 'categories', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:30_00015', 'MetaRole'), 
 ('REFS', 'MolComponent', 'blueprintComponents', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:30_00025', 'MetaRole'), 
 ('REFS', 'MolComponent', 'nucTargets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00033', 'MetaRole'), 
 ('REFS', 'MolComponent', 'protTargets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00031', 'MetaRole'), 
 ('REFS', 'MolComponent', 'relatedExpBlueprints', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:30_00027', 'MetaRole'), 
 ('SAM', 'AbstractSample', 'hazardPhrases', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:28_00013', 'MetaRole'), 
 ('SAM', 'AbstractSample', 'sampleCategories', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:46_00003', 'MetaRole'), 
 ('SAM', 'RefSample', 'refInputSamples', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:57_00008', 'MetaRole'), 
 ('SAM', 'RefSample', 'refOutputSamples', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:57_00023', 'MetaRole'), 
 ('SAM', 'RefSample', 'refSamplePositions', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:44_00010', 'MetaRole'), 
 ('SAM', 'Sample', 'dropAnnotations', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:36_00001', 'MetaRole'), 
 ('SAM', 'Sample', 'holder', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:27_00003', 'MetaRole'), 
 ('SAM', 'Sample', 'inputSamples', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:49_00011', 'MetaRole'), 
 ('SAM', 'Sample', 'outputSample', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:50_00010', 'MetaRole'), 
 ('SAM', 'SampleComponent', 'blueprintComponent', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:42_00006', 'MetaRole'), 
 ('TARG', None, None, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:51_00034', 'MetaPackage'), 
 ('TAXO', 'NaturalSource', 'targets', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00115', 'MetaRole'), 
 ('WMS', None, None, 'www.ccpn.ac.uk_Fogh_2009-01-29-15:16:52_00001', 'MetaPackage'), 
 ('WMSP', 'WmsProtocol', 'memopsRoot', 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00061', 'MetaRole'), 
 ('WMSQ', None, None, 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00006', 'MetaPackage'), 
]

# classElements skipped in new model, but available for simple data transfer
# (prefix, typeName, elemName, newGuid, elemMap, valueTypeGuid)
delayElements = [
 ('CALC', 'NmrCalcStore', 'methodStoreName', 'www.ccpn.ac.uk_Fogh_2010-05-10-13:46:58_00003', {'name': 'methodStoreName', 'eType': 'cplx', 'tag': 'CALC.NmrCalcStore.methodStoreName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033'), 
 ('CALC', 'NmrCalcStore', 'softwareName', 'www.ccpn.ac.uk_Fogh_2010-05-10-13:46:58_00004', {'name': 'softwareName', 'eType': 'cplx', 'tag': 'CALC.NmrCalcStore.softwareName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033'), 
 ('CALC', 'NmrCalcStore', 'softwareVersion', 'www.ccpn.ac.uk_Fogh_2010-05-10-13:46:58_00005', {'name': 'softwareVersion', 'eType': 'cplx', 'tag': 'CALC.NmrCalcStore.softwareVersion', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033'), 
]

# MetaConstraints added in new model
# (qualifiedName, guid)
newConstraints = [
 ('cambridge.WmsProtocol.InterfaceParameter.hicard.hicard_consistent_with_ProtocolParameter_hicard', 'www.ccpn.ac.uk_Fogh_2013-10-11-09:59:51_00001'), 
 ('cambridge.WmsProtocol.InterfaceParameter.locard.locard_consistent_with_ProtocolParameter_locard', 'www.ccpn.ac.uk_Fogh_2013-10-11-09:59:51_00002'), 
 ('ccp.nmr.NmrCalc.Run.masterRun.derived_runs_cannot_be_nested', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00003'), 
 ('memops.Implementation.KeyWord.only_keyword_characters', 'www.ccpn.ac.uk_Fogh_2014-03-07-15:48:27_00002'), 
]

# Mandatory classElements added in new model
# New ClassElements with locard !=0, no default, not derived or Implementation
# (prefix, typeName, elemName, newGuid)
newMandatories = [
 ('IMPL', 'DataObject', '_ID', 'www.ccpn.ac.uk_Fogh_2014-03-03-16:24:15_00001'), 
 ('IMPL', 'ImplementationObject', '_ID', 'www.ccpn.ac.uk_Fogh_2014-03-03-16:24:15_00002'), 
 ('NMRS', 'ExperimentWeight', 'expCode', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00001'), 
 ('NMRS', 'ExperimentWeight', 'trialSet', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00005'), 
 ('WMSP', 'WmsProtocol', 'memopsRoot', 'ccpn_automatic_cambridge.WmsProtocol.WmsProtocol.memopsRoot'), 
]

# Packages, classElements and AbstractDataTypes added in new model
# Optional, i.e. excluding mandatory classElements given above
# (prefix, typeName, elemName, newGuid)
newElements = [
 ('CALC', 'Run', 'derivedRuns', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00001'), 
 ('CALC', 'Run', 'masterRun', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00002'), 
 ('CALC', 'Run', 'methodStoreName', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00004'), 
 ('CALC', 'Run', 'softwareName', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00005'), 
 ('CALC', 'Run', 'softwareVersion', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00006'), 
 ('CALC', 'Run', 'wmsProtocolName', 'www.ccpn.ac.uk_Fogh_2012-06-04-14:36:41_00007'), 
 ('IMPL', 'KeyWord', None, 'www.ccpn.ac.uk_Fogh_2014-03-07-15:48:27_00001'), 
 ('IMPL', 'MemopsRoot', 'wmsProtocols', 'ccpn_automatic_memops.Implementation.MemopsRoot.wmsProtocol'), 
 ('IMPL', 'TopObject', '_lastId', 'www.ccpn.ac.uk_Fogh_2014-03-05-13:04:27_00001'), 
 ('NMR', 'Experiment', 'userExpCode', 'www.ccpn.ac.uk_Fogh_2012-07-23-11:52:27_00001'), 
 ('NMRC', 'FixedResonance', 'covalentlyBound', 'www.ccpn.ac.uk_Fogh_2012-06-25-14:41:56_00001'), 
 ('NMRS', 'ExperimentWeight', None, 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:44_00001'), 
 ('NMRS', 'ExperimentWeight', 'changeIsPositive', 'www.ccpn.ac.uk_Fogh_2012-07-09-10:23:18_00001'), 
 ('NMRS', 'ExperimentWeight', 'intensityScale', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00003'), 
 ('NMRS', 'ExperimentWeight', 'meritThreshold', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00002'), 
 ('NMRS', 'ExperimentWeight', 'weight', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00004'), 
 ('NMRS', 'NmrScreen', 'pH', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:16:06_00002'), 
 ('NMRS', 'NmrScreen', 'temperature', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:16:06_00001'), 
 ('NMRS', 'NmrScreen', 'userProtocolCode', 'www.ccpn.ac.uk_Fogh_2012-07-23-11:52:27_00002'), 
 ('NMRS', 'TrialSet', 'evaluateOnlyUnambiguous', 'www.ccpn.ac.uk_Fogh_2012-07-16-12:06:02_00001'), 
 ('NMRS', 'TrialSet', 'evaluateSingleResonance', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00008'), 
 ('NMRS', 'TrialSet', 'experimentWeights', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00006'), 
 ('NMRS', 'TrialSet', 'identifyAllosteric', 'www.ccpn.ac.uk_Fogh_2012-07-06-13:03:50_00007'), 
]

# Class elements that exist in both models but that require handcode for
# transfer. E.g. elements that go from derived to non-derived.
# Note that old derivation functions can not be relied on to work during
# data transfer
# (prefix, typeName, elemName, newGuid, elemType)
neutraliseElements = [
]

# Differences between equivalent classElements and AbstractDataTypes :

# name changes
# (prefix, typeName, elemName, newName, newGuid
renames = [
 ('CALC', 'ParameterGroup', 'datas', 'data', 'www.ccpn.ac.uk_Fogh_2011-10-11-16:36:23_00002'), 
 ('MOLS', 'StructureGroup', 'detail', 'details', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:33_00030'), 
 ('NMRS', 'Mixture', 'trial', 'trials', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:50:38_00015'), 
 ('NMRS', 'RegionWeight', 'maxppm', 'maxPpm', 'www.ccpn.ac.uk_Fogh_2012-05-21-18:09:12_00005'), 
]

# ValueType changes
# change types are : 'ignore': do nothing, 'delay': available for calculation
# (prefix, typeName, elemName, action, newGuid, elemMap, valueTypeGuid)
typeChanges = [
 ('AFFI', 'Group', 'url', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:15_00004', {'name': 'url', 'eType': 'cplx', 'tag': 'AFFI.Group.url', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('AFFI', 'Organisation', 'addresses', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00024', {'name': 'addresses', 'eType': 'cplx', 'tag': 'AFFI.Organisation.addresses', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('AFFI', 'Organisation', 'url', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00031', {'name': 'url', 'eType': 'cplx', 'tag': 'AFFI.Organisation.url', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('AFFI', 'PersonInGroup', 'deliveryAddress', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00035', {'name': 'deliveryAddress', 'eType': 'cplx', 'tag': 'AFFI.PersonInGroup.deliveryAddress', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('AFFI', 'PersonInGroup', 'mailingAddress', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:14_00034', {'name': 'mailingAddress', 'eType': 'cplx', 'tag': 'AFFI.PersonInGroup.mailingAddress', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ANNO', 'Annotation', 'description', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00110', {'name': 'description', 'eType': 'cplx', 'tag': 'ANNO.Annotation.description', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ANPR', 'AnnealProtocol', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-06-06-13:18:31_00003', {'name': 'details', 'eType': 'cplx', 'tag': 'ANPR.AnnealProtocol.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ANPR', 'EnergyTerm', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-06-06-13:18:31_00011', {'name': 'details', 'eType': 'cplx', 'tag': 'ANPR.EnergyTerm.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ANPR', 'RefPotentialTerm', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-06-06-13:18:31_00002', {'name': 'details', 'eType': 'cplx', 'tag': 'ANPR.RefPotentialTerm.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ANPR', 'RefTermParameter', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-02-20-13:49:37_00010', {'name': 'details', 'eType': 'cplx', 'tag': 'ANPR.RefTermParameter.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CALC', 'Data', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-04-16-16:24:03_00013', {'name': 'details', 'eType': 'cplx', 'tag': 'CALC.Data.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CALC', 'Run', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-04-16-16:24:04_00024', {'name': 'details', 'eType': 'cplx', 'tag': 'CALC.Run.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CCCA', 'ChemCompCharge', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00048', {'name': 'details', 'eType': 'cplx', 'tag': 'CCCA.ChemCompCharge.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CCCO', 'ChemCompCoord', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:36_00082', {'name': 'details', 'eType': 'cplx', 'tag': 'CCCO.ChemCompCoord.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CCLB', 'LabelingScheme', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-01-24-12:23:55_00005', {'name': 'details', 'eType': 'cplx', 'tag': 'CCLB.LabelingScheme.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CHEM', 'ChemComp', 'commonNames', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:21_00013', {'name': 'commonNames', 'eType': 'cplx', 'tag': 'CHEM.ChemComp.commonNames', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CHEM', 'ChemComp', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:22_00006', {'name': 'details', 'eType': 'cplx', 'tag': 'CHEM.ChemComp.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CHEM', 'ChemComp', 'name', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:21_00008', {'name': 'name', 'eType': 'cplx', 'tag': 'CHEM.ChemComp.name', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CHEM', 'ChemCompVar', 'varName', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:23_00034', {'name': 'varName', 'eType': 'cplx', 'tag': 'CHEM.ChemCompVar.varName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'BookCitation', 'bookSeries', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00023', {'name': 'bookSeries', 'eType': 'cplx', 'tag': 'CITA.BookCitation.bookSeries', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'BookCitation', 'bookTitle', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00021', {'name': 'bookTitle', 'eType': 'cplx', 'tag': 'CITA.BookCitation.bookTitle', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'BookCitation', 'publisher', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00024', {'name': 'publisher', 'eType': 'cplx', 'tag': 'CITA.BookCitation.publisher', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'BookCitation', 'publisherCity', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00025', {'name': 'publisherCity', 'eType': 'cplx', 'tag': 'CITA.BookCitation.publisherCity', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'Citation', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00020', {'name': 'details', 'eType': 'cplx', 'tag': 'CITA.Citation.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'Citation', 'doi', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00013', {'name': 'doi', 'eType': 'cplx', 'tag': 'CITA.Citation.doi', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'ConferenceCitation', 'conferenceTitle', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00027', {'name': 'conferenceTitle', 'eType': 'cplx', 'tag': 'CITA.ConferenceCitation.conferenceTitle', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'JournalCitation', 'journalFullName', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00040', {'name': 'journalFullName', 'eType': 'cplx', 'tag': 'CITA.JournalCitation.journalFullName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('CITA', 'ThesisCitation', 'institution', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:13_00035', {'name': 'institution', 'eType': 'cplx', 'tag': 'CITA.ThesisCitation.institution', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('COOR', 'DataMatrix', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2011-04-06-10:33:05_00002', {'name': 'details', 'eType': 'cplx', 'tag': 'COOR.DataMatrix.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('COOR', 'Model', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-07-11-16:03:09_00002', {'name': 'details', 'eType': 'cplx', 'tag': 'COOR.Model.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('COOR', 'StructureEnsemble', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-01-21-15:56:25_00001', {'name': 'details', 'eType': 'cplx', 'tag': 'COOR.StructureEnsemble.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('DLOC', 'AbstractDataStore', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-11-07-17:54:39_00001', {'name': 'details', 'eType': 'cplx', 'tag': 'DLOC.AbstractDataStore.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ENTR', 'Entry', 'bmrbProcessing', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:11_00052', {'name': 'bmrbProcessing', 'eType': 'cplx', 'tag': 'ENTR.Entry.bmrbProcessing', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ENTR', 'Entry', 'experimentListDetails', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-09-26-14:12:30_00007', {'name': 'experimentListDetails', 'eType': 'cplx', 'tag': 'ENTR.Entry.experimentListDetails', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ENTR', 'Entry', 'title', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:11_00051', {'name': 'title', 'eType': 'cplx', 'tag': 'ENTR.Entry.title', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('ENTR', 'RelatedEntry', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-01-19-14:21:01_00007', {'name': 'details', 'eType': 'cplx', 'tag': 'ENTR.RelatedEntry.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('HADD', 'HaddockEnergyTerm', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-02-20-15:13:04_00001', {'name': 'details', 'eType': 'cplx', 'tag': 'HADD.HaddockEnergyTerm.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('METH', 'Parameter', 'value', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00011', {'name': 'value', 'eType': 'cplx', 'tag': 'METH.Parameter.value', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('METH', 'Software', 'vendorAddress', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00007', {'name': 'vendorAddress', 'eType': 'cplx', 'tag': 'METH.Software.vendorAddress', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('METH', 'Software', 'vendorName', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:17_00006', {'name': 'vendorName', 'eType': 'cplx', 'tag': 'METH.Software.vendorName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLE', 'Alignment', 'alignmentProgram', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-11-26-10:15:39_00005', {'name': 'alignmentProgram', 'eType': 'cplx', 'tag': 'MOLE.Alignment.alignmentProgram', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLE', 'Molecule', 'fragmentDetails', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-01-19-14:20:59_00001', {'name': 'fragmentDetails', 'eType': 'cplx', 'tag': 'MOLE.Molecule.fragmentDetails', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLE', 'Molecule', 'longName', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:34_00011', {'name': 'longName', 'eType': 'cplx', 'tag': 'MOLE.Molecule.longName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLE', 'Molecule', 'mutationDetails', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-01-19-14:20:59_00002', {'name': 'mutationDetails', 'eType': 'cplx', 'tag': 'MOLE.Molecule.mutationDetails', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLE', 'Molecule', 'seqDetails', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:34_00027', {'name': 'seqDetails', 'eType': 'cplx', 'tag': 'MOLE.Molecule.seqDetails', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'Chain', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:32_00013', {'name': 'details', 'eType': 'cplx', 'tag': 'MOLS.Chain.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'MolSystem', 'commonNames', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:31_00023', {'name': 'commonNames', 'eType': 'cplx', 'tag': 'MOLS.MolSystem.commonNames', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'MolSystem', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:31_00028', {'name': 'details', 'eType': 'cplx', 'tag': 'MOLS.MolSystem.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'MolSystem', 'name', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:31_00020', {'name': 'name', 'eType': 'cplx', 'tag': 'MOLS.MolSystem.name', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'Residue', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:33_00008', {'name': 'details', 'eType': 'cplx', 'tag': 'MOLS.Residue.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('MOLS', 'StructureGroup', 'detail', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:33_00030', {'name': 'detail', 'eType': 'cplx', 'tag': 'MOLS.StructureGroup.detail', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'AbstractDataDerivation', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:19:57_00042', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.AbstractDataDerivation.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'AbstractMeasurement', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:19:58_00018', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.AbstractMeasurement.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'ChainState', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:02_00010', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.ChainState.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'ChainStateSet', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:02_00016', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.ChainStateSet.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'FidDataDim', 'oversamplingInfo', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:07_00014', {'name': 'oversamplingInfo', 'eType': 'cplx', 'tag': 'NMR.FidDataDim.oversamplingInfo', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'IsotropicS2', 'modelFit', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:08_00003', {'name': 'modelFit', 'eType': 'cplx', 'tag': 'NMR.IsotropicS2.modelFit', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'NmrExpSeries', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:28_00003', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.NmrExpSeries.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'NoeList', 'refDescription', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:07_00060', {'name': 'refDescription', 'eType': 'cplx', 'tag': 'NMR.NoeList.refDescription', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'Peak', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:00_00005', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.Peak.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'Resonance', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:10_00012', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.Resonance.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'SampledDataDim', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:11_00028', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.SampledDataDim.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'ShiftReference', 'indirectShiftRatio', 'delay', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:20:12_00012', {'name': 'indirectShiftRatio', 'eType': 'cplx', 'tag': 'NMR.ShiftReference.indirectShiftRatio', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'StructureAnalysis', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-03-06-18:40:32_00004', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.StructureAnalysis.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMR', 'StructureGeneration', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:30_00001', {'name': 'details', 'eType': 'cplx', 'tag': 'NMR.StructureGeneration.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRC', 'AbstractConstraint', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:10_00017', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRC.AbstractConstraint.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRC', 'ConditionState', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2008-04-16-13:49:39_00007', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRC.ConditionState.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRC', 'ConstraintGroup', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:08_00026', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRC.ConstraintGroup.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRC', 'FixedResonance', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:11_00013', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRC.FixedResonance.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRC', 'ViolationList', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:06_00003', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRC.ViolationList.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRR', 'ChemCompNmrRef', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:37_00001', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRR.ChemCompNmrRef.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'Mixture', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:50:38_00021', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.Mixture.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'NmrScreen', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:50:38_00040', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.NmrScreen.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'NmrScreen', 'objective', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:50:38_00037', {'name': 'objective', 'eType': 'cplx', 'tag': 'NMRS.NmrScreen.objective', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'Trial', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:51:56_00010', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.Trial.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'TrialExperiment', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:51:56_00015', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.TrialExperiment.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'TrialGroup', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:51:56_00018', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.TrialGroup.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'TrialHit', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:51:56_00025', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.TrialHit.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRS', 'TrialSet', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2012-05-21-18:09:12_00016', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRS.TrialSet.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('NMRX', 'NmrExpPrototype', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:58_00017', {'name': 'details', 'eType': 'cplx', 'tag': 'NMRX.NmrExpPrototype.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFD', 'RefNmrSpectrum', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2009-11-19-14:50:38_00056', {'name': 'details', 'eType': 'cplx', 'tag': 'REFD.RefNmrSpectrum.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Cell', 'competentMethod', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00016', {'name': 'competentMethod', 'eType': 'cplx', 'tag': 'REFS.Cell.competentMethod', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Cell', 'cultureCollection', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00015', {'name': 'cultureCollection', 'eType': 'cplx', 'tag': 'REFS.Cell.cultureCollection', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Cell', 'divided', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00018', {'name': 'divided', 'eType': 'cplx', 'tag': 'REFS.Cell.divided', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Cell', 'features', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00017', {'name': 'features', 'eType': 'cplx', 'tag': 'REFS.Cell.features', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Cell', 'phase', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00019', {'name': 'phase', 'eType': 'cplx', 'tag': 'REFS.Cell.phase', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'ComponentDbRef', 'threadingProg', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00042', {'name': 'threadingProg', 'eType': 'cplx', 'tag': 'REFS.ComponentDbRef.threadingProg', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Composite', 'assessmentMethod', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00024', {'name': 'assessmentMethod', 'eType': 'cplx', 'tag': 'REFS.Composite.assessmentMethod', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'Composite', 'molecularMassMethod', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00026', {'name': 'molecularMassMethod', 'eType': 'cplx', 'tag': 'REFS.Composite.molecularMassMethod', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'CompositeInteraction', 'assessmentMethod', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00007', {'name': 'assessmentMethod', 'eType': 'cplx', 'tag': 'REFS.CompositeInteraction.assessmentMethod', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('REFS', 'CompositeInteraction', 'interactionType', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:29_00005', {'name': 'interactionType', 'eType': 'cplx', 'tag': 'REFS.CompositeInteraction.interactionType', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('SAM', 'CrystalSample', 'colour', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:44_00014', {'name': 'colour', 'eType': 'cplx', 'tag': 'SAM.CrystalSample.colour', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('SAM', 'CrystalSample', 'crystalType', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:44_00013', {'name': 'crystalType', 'eType': 'cplx', 'tag': 'SAM.CrystalSample.crystalType', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('SAM', 'CrystalSample', 'morphology', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:44_00012', {'name': 'morphology', 'eType': 'cplx', 'tag': 'SAM.CrystalSample.morphology', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('SAM', 'RefSampleSource', 'dataPageUrl', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:22:46_00018', {'name': 'dataPageUrl', 'eType': 'cplx', 'tag': 'SAM.RefSampleSource.dataPageUrl', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('SYMM', 'MolSystemSymmetrySet', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2011-08-05-11:53:29_00002', {'name': 'details', 'eType': 'cplx', 'tag': 'SYMM.MolSystemSymmetrySet.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'fraction', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00011', {'name': 'fraction', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.fraction', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'geneMnemonic', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00015', {'name': 'geneMnemonic', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.geneMnemonic', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'ictvCode', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00009', {'name': 'ictvCode', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.ictvCode', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'ncbiTaxonomyId', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00003', {'name': 'ncbiTaxonomyId', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.ncbiTaxonomyId', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'organelle', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00017', {'name': 'organelle', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.organelle', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'organismAcronym', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00007', {'name': 'organismAcronym', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.organismAcronym', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'organismName', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00002', {'name': 'organismName', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.organismName', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'plasmid', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00021', {'name': 'plasmid', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.plasmid', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('TAXO', 'NaturalSource', 'subVariant', 'ignore', 'www.ccpn.ac.uk_Fogh_2006-08-16-18:23:38_00020', {'name': 'subVariant', 'eType': 'cplx', 'tag': 'TAXO.NaturalSource.subVariant', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('VALD', 'ValidationResult', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2007-11-13-15:55:55_00014', {'name': 'details', 'eType': 'cplx', 'tag': 'VALD.ValidationResult.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('WMSP', 'ProtocolInterface', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2011-03-22-17:23:24_00029', {'name': 'details', 'eType': 'cplx', 'tag': 'WMSP.ProtocolInterface.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
 ('WMSP', 'WmsProtocol', 'details', 'ignore', 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:57_00015', {'name': 'details', 'eType': 'cplx', 'tag': 'WMSP.WmsProtocol.details', 'type': 'attr'}, 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035'), 
]

# Different elements with matching qualifiedNames
# (element.qName, differentTags, oldGuid, newGuid
nameMatches = [
 ('cambridge.WmsProtocol.WmsProtocol.memopsRoot', ({'documentation', 'otherRole'}, 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00061', 'ccpn_automatic_cambridge.WmsProtocol.WmsProtocol.memopsRoot')), 
 ('memops.Implementation.MemopsRoot.wmsProtocols', ({'documentation', 'otherRole'}, 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00062', 'ccpn_automatic_memops.Implementation.MemopsRoot.wmsProtocol')), 
]

# Differences for matching elements, 
# excluding those where only names and/or valueTypes differ
# (oldElem.qName, newElem.name, oldGuid, newGuid, differentTags
allDiffs = [
 ('cambridge.WmsProtocol.InterfaceParameter.hicard', 'hicard', 'www.ccpn.ac.uk_Fogh_2011-03-22-17:23:24_00005', 'www.ccpn.ac.uk_Fogh_2011-03-22-17:23:24_00005', {'documentation', 'locard', 'defaultValue'}), 
 ('cambridge.WmsProtocol.InterfaceParameter.locard', 'locard', 'www.ccpn.ac.uk_Fogh_2011-03-22-17:23:24_00006', 'www.ccpn.ac.uk_Fogh_2011-03-22-17:23:24_00006', {'documentation', 'defaultValue'}), 
 ('cambridge.WmsProtocol.WmsProtocol', 'WmsProtocol', 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00002', 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00002', {'parentRole'}), 
 ('ccp.general.DataLocation.NumberType', 'NumberType', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00034', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00034', {'supertype', 'supertypes'}), 
 ('ccp.nmr.Nmr.IntensityType', 'IntensityType', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00038', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00038', {'supertype', 'supertypes'}), 
 ('ccp.nmr.Nmr.ShiftRefType', 'ShiftRefType', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00033', 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:48_00033', {'supertype', 'supertypes'}), 
 ('ccp.nmr.NmrScreen.RegionWeight.weight', 'weight', 'www.ccpn.ac.uk_Fogh_2012-05-21-18:09:12_00006', 'www.ccpn.ac.uk_Fogh_2012-05-21-18:09:12_00006', {'defaultValue'}), 
]
