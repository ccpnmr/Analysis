#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: LucaM $"
__dateModified__ = "$dateModified: 2019-10-31 16:32:32 +0100 (Thu, Oct 31, 2019) $"
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: LucaM $"
__date__ = "$Date: 2019-10-31 16:32:32 +0100 (Thu, Oct 31, 2019) $"
#=========================================================================================



"""

This macro doesn't want to be an automated Backbone assignment and is aimed only to add initial labels to a project containing:
 15N-HSQC,  HNCA,  HNCOCA,  HNCACB,  CBCACONH, which will be carefully inspected manually and amended as needed it.

However can be run also if at least a 15N-HSQC and a HNCACB are present.

The macro uses the picking peak routines present in 3.0.0 to pick the HSQC first and label with incremental numbered nmrResidues.
Then picks restricted peak for all the 3Ds.
It guesses the "i-1" and "i" by peak heights for HNCA and HNCACB
It cannot guess for CBCACONH so an NmrAtom C is given, Ca i-1 and CB i-1 are propagated from the HNCACB if the two spectral peaks are within tollerances

Searches for "i-1"s which are present in same spectra but missing and expected in others and copies them. 
Deletes obsolete peaks assigned to C if properly reassigned to CA or/and CB i-1 
Deletes unassigned peaks

User Parameters needed:
 - spectra names (mandatory for 15N-HSQC and  HNCACB,  
 - picking limits (defaults given)
 - tolerances (defaults given)

Modify as you need and share your macros on the forum!

"""
from collections import OrderedDict as od # rest of import are set further down

##################################################################################################
#####################################    User's  Parameters  #####################################
##################################################################################################

# Replace with your spectra names. Leave empty quotes '' if don't have
HSQC_spectrumName = 'hsqc' # mandatory
HNCACB_spectrumName = 'hncacb'
HNCA_spectrumName = 'hnca'
HNCOCA_spectrumName = 'hncoca'
CBCACONH_spectrumName = 'cbcaconh'


# labels used to create nmrAtoms, NB on the current version 3.0.0 changing H to Hn and N to Nh
# might break the assignment prediction for sequential matches! It could work on other labelling eg 13C but not tested)
H  = 'H'
N  = 'N'
CA = 'CA'
CB = 'CB'
C  = 'C'
CH = 'CH'

OFFSET = '-1' # implemented only for -1 at the moment!
nmrChainName = '@-' # use the default. Change this name to create a different one

# Picking parameters: HSQC
minDropFactor = 0.01  # (1%) # pick more then less, unlabeled peaks will be deleted afterwards
HSQC_limits = od(((H, [6,11]),  (N, [100,134]) )) # ppm limits where to find the signal on HSQC

# regions of search on 3D
# H and N limits +/- to the HSQC position for restricted  peak picking
# C: the actual region of search. All in ppm
HNCA_limits   =   od(((H, [0.05, 0.05]),   (N, [1, 1]), (C, [40,80])))
HNCOCA_limits =   od(((H, [0.05, 0.05]),   (N, [1, 1]), (C, [40,80])))
HNCACB_limits =   od(((H, [0.05, 0.05]),   (N, [1, 1]), (C, [10,80])))
CBCACONH_limits = od(((H, [0.05, 0.05]),   (N, [1, 1]), (C, [10,80])))

# tolerances in ppm for matching peaks across different Experiment types. Used when propagating assignments.
tolerances   =   od(((H, 0.1),  (N, 2), (C, 4)))

# Contours, in case you don't want set it manually from display ...
setContours = False # set False if not needed
hsqcContours      =  (64194.19080018526, -64194.19080018526) # positive and negative Contours values
hncaContours      =  (5835252.217157302, -5835252.217157302)
hncocaContours    =  (15051295.29692141, -15051295.29692142)
hncacbContours    =  (13094258.00380035, -13094258.00380035)
cbcaconhContours  =  (8161392.113049264, -8161392.113049264)


##################################################################################################
#######################################  start of the code #######################################
##################################################################################################

# imports
from ccpn.core.lib.ContextManagers import undoBlock, undoBlockWithoutSideBar, notificationEchoBlocking
from ccpn.ui.gui.widgets.MessageDialog import _stoppableProgressBar, showWarning
from ccpn.core.lib.AssignmentLib import _assignNmrAtomsToPeaks, assignAlphas,assignBetas
from ccpn.util.Common import makeIterableList
from collections import defaultdict
import numpy as np

# get spectra objects
hsqc = project.getByPid('SP:'+ HSQC_spectrumName)
hnca = project.getByPid('SP:'+ HNCA_spectrumName)
hncoca = project.getByPid('SP:'+ HNCOCA_spectrumName)
hncacb = project.getByPid('SP:'+ HNCACB_spectrumName)
cbcaconh = project.getByPid('SP:'+ CBCACONH_spectrumName)


if not hsqc: #not point in continue if not at least the HSQC!
    showWarning('Error', 'hsqc has to be in the project for this macro')
    raise ValueError

# get nmrChain object
nmrChain = project.fetchNmrChain(nmrChainName)

# set Contours
application.preferences.general.peakDropFactor = minDropFactor
if setContours:
    if hnca: hnca.positiveContourBase, hnca.negativeContourBase = hncaContours[0],  hncaContours[1]
    if hncoca: hncoca.positiveContourBase, hncoca.negativeContourBase = hncocaContours[0],  hncocaContours[1]
    if hncacb: hncacb.positiveContourBase, hncacb.negativeContourBase = hncacbContours[0],  hncacbContours[1]
    if cbcaconh: cbcaconh.positiveContourBase, cbcaconh.negativeContourBase = cbcaconhContours[0],  cbcaconhContours[1]

def pickPeaksHSQC():
    """
    picks on the last peakList of the HSQC. should be always one as default.
    :return:  peaks
    """
    with notificationEchoBlocking():
        peakList = hsqc.peakLists[-1]
        peaks = peakList.pickPeaksRegion(regionToPick=HSQC_limits, doPos=True, doNeg=False,
                                         minDropFactor=minDropFactor,estimateLineWidths=True)
        return peaks

def addLabelsHSQC():
    """
    adds label for each hsqc peak
    """
    hsqcPeaks = hsqc.peakLists[-1].peaks
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for peak in _stoppableProgressBar(hsqcPeaks, title='Labelling HSQC... (1/2)'):
                nmrResidue = nmrChain.fetchNmrResidue()
                hNmrAtom = nmrResidue.fetchNmrAtom(name=H)
                nNmrAtom = nmrResidue.fetchNmrAtom(name=N)
                _assignNmrAtomsToPeaks([peak], [hNmrAtom, nNmrAtom])


def _orderPeaksByHeight(peaks):
    """
    :param peaks: sort peaks in descending height. First the strongest....
    :type peaks:
    :return:
    :rtype:
    """
    aPeaks = np.array(peaks)
    heights = np.array([abs(j.height) for j in aPeaks])
    indices = heights.argsort()
    return list(aPeaks[indices[::-1]])

def _assignByHeights(nmrResidue, peaks, label='CA', propagateNmrAtoms=[]):

    """
    The easiest way to estimate "i-1" and "i" by peak heights
    nmrResidue: Obj nmrResidue.
    peaks: obj peaks to be assigned.
    label: str of label to assign. E.g. CA or CB
    propagateNmrAtoms: nmrAtoms  E.G H,N atoms to be propagated to the peak(s)
    Assigns "i" and "i-1" NmrAtoms by peak height.
    The peak with the max height will be the "i"
    The peak with the min height will be the "i-1"
    If only one peak, then it is assigned to "i" by default.
    """
    lowestP = [i for i in peaks if abs(i.height) == min([abs(j.height) for j in peaks])]
    highestP = [i for i in peaks if abs(i.height) == max([abs(j.height) for j in peaks])]

    if highestP:
        i_NmrAtom = nmrResidue.fetchNmrAtom(name=label)
        _assignNmrAtomsToPeaks(highestP, propagateNmrAtoms+[i_NmrAtom])
    if highestP == lowestP:
        return
    elif lowestP:
        i_m_1_NmrResidue = nmrResidue.nmrChain.fetchNmrResidue(nmrResidue.sequenceCode + '-1')
        i_m_1_NmrAtom = i_m_1_NmrResidue.fetchNmrAtom(name=label)
        _assignNmrAtomsToPeaks(lowestP, propagateNmrAtoms+[i_m_1_NmrAtom])

def _isPeakWithinTollerances(referencePeak, targetPeak, tolerances):
    referencePeakPos = np.array(referencePeak.position)
    targetPeakPeakPos = np.array(targetPeak.position)
    tolerancesArray = np.array(list(tolerances.values()))
    diff = abs(targetPeakPeakPos-referencePeakPos)
    return all(diff<tolerancesArray)

def _getPeakForNmrAtom(peaks, queryNA):
    for peak in peaks:
        for na in makeIterableList(peak.assignedNmrAtoms):
            if na == queryNA:
                return peak

def _copyPeakFromOtherExpType(tobeCopiedPeak, targetPeakList, nmrAtomLabel = 'CA-1'):
    if tobeCopiedPeak:
        missingPeak = tobeCopiedPeak.copyTo(targetPeakList)
        missingPeak.comment = '%s Copied from %s. Inspect it' % (nmrAtomLabel,tobeCopiedPeak.peakList.id)
        return missingPeak

def getRegions(hsqcPosition, limits):
    dd = limits.copy()
    dd[H] = [hsqcPosition[0]-limits[H][0], hsqcPosition[0]+limits[H][1]]
    dd[N] =  [hsqcPosition[1]-limits[N][0], hsqcPosition[1]+limits[N][1]]
    return dd

def _pickAndAssign_HNCA(hnca,hsqcPosition, hsqc_nmrAtoms,nmrResidue, expectedPeakCount=2):
    regions = getRegions(hsqcPosition, HNCA_limits)
    hncaPeaks = hnca.peakLists[-1].pickPeaksRegion(regionToPick=regions, doPos=True, doNeg=False,
                                         minDropFactor=minDropFactor)
    _assignNmrAtomsToPeaks(hncaPeaks, hsqc_nmrAtoms)
    peaks = _orderPeaksByHeight(hncaPeaks)
    _assignByHeights(nmrResidue, peaks[:expectedPeakCount], label=CA)
    return hncaPeaks

def _pickAndAssign_HNCOCA(hncoca,hsqcPosition, hsqc_nmrAtoms, m1nmrResidue, expectedPeakCount=1):
    regions = getRegions(hsqcPosition, HNCOCA_limits)
    hncocaPeaks = hncoca.peakLists[-1].pickPeaksRegion(regionToPick=regions, doPos=True, doNeg=False,
                                                       minDropFactor=minDropFactor)
    peaks = _orderPeaksByHeight(hncocaPeaks)
    m1nmrAtomCA = m1nmrResidue.fetchNmrAtom(CA)
    _assignNmrAtomsToPeaks(peaks[:expectedPeakCount], hsqc_nmrAtoms + [m1nmrAtomCA])
    return hncocaPeaks

def _pickAndAssign_CBCACONH(cbcaconh, hsqcPosition, hsqc_nmrAtoms, m1nmrResidue, expectedPeakCount=2):
    regions = getRegions(hsqcPosition, CBCACONH_limits)
    cbcaconhPeaks = cbcaconh.peakLists[-1].pickPeaksRegion(regionToPick=regions, doPos=True, doNeg=False,
                                                       minDropFactor=minDropFactor)
    peaks = _orderPeaksByHeight(cbcaconhPeaks)
     # cannot guess yet which one is CA or CB  so give it a C !
    m1nmrAtomC = m1nmrResidue.fetchNmrAtom(C)
    _assignNmrAtomsToPeaks(peaks[:expectedPeakCount], hsqc_nmrAtoms + [m1nmrAtomC])  # assign first generic C
    return cbcaconhPeaks

def _pickAndAssign_HNCACB(hncacb, hsqcPosition, hsqc_nmrAtoms, nmrResidue , expectedPeakCount=4):
    regions = getRegions(hsqcPosition, HNCACB_limits)
    hncacbPeaks = hncacb.peakLists[-1].pickPeaksRegion(regionToPick=regions, doPos=True, doNeg=True, minDropFactor=minDropFactor)
    _assignNmrAtomsToPeaks(hncacbPeaks, hsqc_nmrAtoms)
    posPeaks = [p for p in hncacbPeaks if p.height > 0]
    negPeaks = [p for p in hncacbPeaks if p.height < 0]
    sortedPosPeaks = _orderPeaksByHeight(posPeaks)
    sortednegPeaks = _orderPeaksByHeight(negPeaks)
    _assignByHeights(nmrResidue, sortedPosPeaks[:int(expectedPeakCount/2)], CA, hsqc_nmrAtoms)
    _assignByHeights(nmrResidue, sortednegPeaks[:int(expectedPeakCount/2)], CB, hsqc_nmrAtoms)
    return hncacbPeaks

def pickRestrictedPeaksAndAddLabels():
    hsqcPeaks = hsqc.peakLists[-1].peaks
    allPeaks = []
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for peak in _stoppableProgressBar(hsqcPeaks, title='Labelling 3Ds...(2/2)'):
                _CAm1Peak = None
                _CBm1Peak = None
                # hsqc nmrAtoms
                hsqcPosition = peak.position
                hsqc_nmrAtoms = makeIterableList(peak.assignedNmrAtoms)
                nmrResidue = hsqc_nmrAtoms[-1].nmrResidue
                m1nmrResidue = nmrChain.fetchNmrResidue(nmrResidue.sequenceCode + OFFSET)

                if hncacb:
                    hncacbPeaks = _pickAndAssign_HNCACB(hncacb, hsqcPosition, hsqc_nmrAtoms, nmrResidue)
                    allPeaks.extend(hncacbPeaks)

                if cbcaconh:
                    cbcaconhPeaks = _pickAndAssign_CBCACONH(cbcaconh, hsqcPosition, hsqc_nmrAtoms, m1nmrResidue)
                    allPeaks.extend(cbcaconhPeaks)

                if hnca:
                    hncaPeaks = _pickAndAssign_HNCA(hnca, hsqcPosition, hsqc_nmrAtoms,nmrResidue)
                    allPeaks.extend(hncaPeaks)

                if hncoca:
                    hncocaPeaks = _pickAndAssign_HNCOCA(hncoca,hsqcPosition, hsqc_nmrAtoms, m1nmrResidue)
                    allPeaks.extend(hncocaPeaks)


            toBeDeleted3DsPeaks = [p for p in allPeaks if not p.isFullyAssigned() if not p.isDeleted]
            project.deleteObjects(*toBeDeleted3DsPeaks)
    return allPeaks

def deleteDuplicatedCACBm1():
    """
    Removes weaker peaks which are assigned to the same nmrAtoms in the same peakList.
    """
    tobeDeletedPeaks = []
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for nmrResidue in _stoppableProgressBar(project.nmrResidues, title='Cleaning up...(3/3)'):
                if nmrResidue.relativeOffset == -1:
                    for nmrAtom in nmrResidue.nmrAtoms:
                        if len(nmrAtom.assignedPeaks) > 0:
                            pls = [{peak.peakList: peak} for peak in nmrAtom.assignedPeaks]
                            dd = defaultdict(list)
                            for d in pls:
                                for pl, peak in d.items(): # make a dict with key the peakList and as value a list of all peak belonging to that peakList
                                    dd[pl].append(peak)
                            for pl, peaks in dd.items():
                                tobeDeletedPeaks.extend([peak for peak in peaks if abs(peak.height)!= max([abs(peak.height) for peak in peaks])])
            project.deleteObjects(*tobeDeletedPeaks)

def findPeaksAssignedOnlyToHSQC():
    peaks = []
    unAssignedNmrResidues = []
    print('NmrResidues which contain Peaks assigned only on the HSQC and unassigned on 3Ds. Might be noisy or sidechain peaks:')
    for nmrResidue in nmrChain.nmrResidues:
        l1 = [peak for na in nmrResidue.nmrAtoms for peak in na.assignedPeaks]
        if len(l1) == 0:
            unAssignedNmrResidues.append(nmrResidue)
        if len(set(l1)) == 1:
            peaks.extend(l1)
            print(nmrResidue.pid)
    print('If you want to delete these peaks run: \nproject.deleteObjects(*unAssigned)')
    # project.deleteObjects(*unAssignedNmrResidues) # not assigned to any peak. No point in keeping it for now
    return peaks


def _propagate_toOther(nmrAtomName = CA, originSpectrum=None, targetPeakLists=[]):
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for nr in _stoppableProgressBar(project.nmrResidues, title='Propagating NmrAtoms...'):
                if nr.relativeOffset == -1:
                    na = nr.getNmrAtom(nmrAtomName)
                    if na:
                        aaPeaks = makeIterableList(na.assignedPeaks)
                        if len(aaPeaks):
                            aaPeaksOrigin = [p for p in aaPeaks if p.peakList.spectrum == originSpectrum]

                            for aPeak in aaPeaksOrigin:
                                for peakList in targetPeakLists:
                                    for otherPeak in peakList.peaks:
                                        if _isPeakWithinTollerances(aPeak, otherPeak, tolerances):
                                            tbPropagated = makeIterableList(aPeak.assignedNmrAtoms)
                                            _assignNmrAtomsToPeaks([otherPeak], tbPropagated)






def _copyPeaksToOthePeakList(originPeakList, targetPeakList, nmrAtomLabel=CA):
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for peak in originPeakList.peaks:
                tobeCopied = []
                for targetPeak in targetPeakList.peaks:
                    if _isPeakWithinTollerances(peak, targetPeak, tolerances):
                        a1 = makeIterableList(peak.assignedNmrAtoms)
                        a2 = makeIterableList(targetPeak.assignedNmrAtoms)
                        # _assignNmrAtomsToPeaks([otherPeak], tbPropagated)
                        if a2 != a1:
                            tobeCopied.append(peak)
                newPeak =_copyPeakFromOtherExpType(peak, targetPeakList, nmrAtomLabel)

def checkNmrAtomCount():
    with notificationEchoBlocking():
        with undoBlockWithoutSideBar():
            for nr in  _stoppableProgressBar(project.nmrResidues, title='Copying missing NmrAtoms...'):
                if nr.relativeOffset == -1:
                    caIm1 = nr.getNmrAtom(CA)
                    cbIm1 = nr.getNmrAtom(CB)

                    if cbIm1:
                        cbIm1Peaks = makeIterableList(caIm1.assignedPeaks)
                        cbIm1Dict = od()
                        for cbIm1Peak in cbIm1Peaks:
                            cbIm1Dict[cbIm1Peak.peakList.spectrum] = cbIm1Peak
                        if cbcaconh:
                            if not cbIm1Dict.get(cbcaconh):
                                while True:
                                    if cbIm1Dict.get(hncacb):  # only choice
                                        cbIm1Dict.get(hncacb).copyTo(cbcaconh.peakLists[-1])
                                        break
                                    break

                    if caIm1:
                        caPeaks = makeIterableList(caIm1.assignedPeaks)
                        caIm1Dict = od()
                        for p in caPeaks:
                            caIm1Dict[p.peakList.spectrum] = p
                        if not caIm1Dict.get(hncacb):
                            if caIm1Dict.get(hncoca): # copy from hncoca 1st choice
                                caIm1Dict.get(hncoca).copyTo(hncacb.peakLists[-1])
                            else:
                                if caIm1Dict.get(hnca):  # copy from hnca 2nd choice
                                    caIm1Dict.get(hnca).copyTo(hncacb.peakLists[-1])
                                    if hncoca: # if  you have on hnca but not on hncoca
                                        caIm1Dict.get(hnca).copyTo(hncoca.peakLists[-1])
                        if cbcaconh:
                            if not caIm1Dict.get(cbcaconh):
                                while True:
                                    if caIm1Dict.get(hncoca):  # copy from hncoca 1st choice
                                        caIm1Dict.get(hncoca).copyTo(cbcaconh.peakLists[-1])
                                        break
                                    if caIm1Dict.get(hnca):    # copy from hnca   2nd choice
                                        caIm1Dict.get(hnca).copyTo(cbcaconh.peakLists[-1])
                                        break
                                    if caIm1Dict.get(hncacb):  # copy from hncacb 3rd choice
                                        caIm1Dict.get(hncacb).copyTo(cbcaconh.peakLists[-1])
                                        break
                                    break
                        if hnca:
                            if not caIm1Dict.get(hnca):
                                while True:
                                    if caIm1Dict.get(hncoca):  # copy from hncoca 1st choice
                                        caIm1Dict.get(hncoca).copyTo(hnca.peakLists[-1])
                                        break
                                    if caIm1Dict.get(hncacb):  # copy from hncacb 3rd choice
                                        caIm1Dict.get(hncacb).copyTo(hnca.peakLists[-1])
                                        break
                                    break


def removeObsoletePeaks():
    tobedelpeaks =[]
    for nr in  _stoppableProgressBar(project.nmrResidues, title='removing  obsolete C NmrAtoms...'):
        if nr.relativeOffset == -1:

            cIm1 = nr.getNmrAtom(C)
            caIm1 = nr.getNmrAtom(CA)
            cbIm1 = nr.getNmrAtom(CB)
            if caIm1 and cbIm1:
                pks = makeIterableList(cIm1.assignedPeaks)
                tobedelpeaks.extend(pks)
            if caIm1 and cIm1 :
                pks = makeIterableList(cIm1.assignedPeaks)
                if len(pks) == 1: # then is maybe CB
                    _assignNmrAtomsToPeaks(pks,[nr.fetchNmrAtom(CB)])
            if cbIm1 and cIm1:
                pks = makeIterableList(cIm1.assignedPeaks)
                if len(pks) == 1:  # then is maybe CA
                    _assignNmrAtomsToPeaks(pks, [nr.fetchNmrAtom(CA)])

    project.deleteObjects(*tobedelpeaks)




def _propagate_HNCACB_to_CBCACONH():
    caPeaks= []
    cbPeaks = []
    cPeaks = []
    for nr in project.nmrResidues:
            if nr.relativeOffset == -1:
                caNa = nr.getNmrAtom(CA)
                cbNa = nr.getNmrAtom(CB)
                cNa = nr.getNmrAtom(C)
                if caNa:
                    caPeaks = makeIterableList(caNa.assignedPeaks)
                if cbNa:
                    cbPeaks = makeIterableList(cbNa.assignedPeaks)
                if cNa:
                    cPeaks = makeIterableList(cNa.assignedPeaks)
            with notificationEchoBlocking():
                with undoBlockWithoutSideBar():
                    for cPeak in cPeaks:
                        for caPeak in caPeaks:
                            if _isPeakWithinTollerances(cPeak, caPeak, tolerances):
                                tbPropagated = makeIterableList(caPeak.assignedNmrAtoms)
                                _assignNmrAtomsToPeaks([cPeak], tbPropagated)
                        for cbPeak in cbPeaks:
                            if _isPeakWithinTollerances(cPeak, cbPeak, tolerances):
                                tbPropagated = makeIterableList(cbPeak.assignedNmrAtoms)
                                _assignNmrAtomsToPeaks([cPeak], tbPropagated)



# run it
pickPeaksHSQC()
addLabelsHSQC()
pickRestrictedPeaksAndAddLabels()
unAssigned = findPeaksAssignedOnlyToHSQC()
_propagate_HNCACB_to_CBCACONH()
checkNmrAtomCount()
removeObsoletePeaks()






