"""General graph handling code

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
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import collections
from typing import Tuple

def minimumStepPath(graph:dict, startNode, endNode=None) -> Tuple[dict,dict]:
  """ Minimum-step-path by breadth-first traversal, inspired by Dijkstras algorithm
  Each edge has the same weight; among paths of the same length
  the function selects the first encountered. Breadth-first search guarantees that
  the paths with fewest steps are encountered first.

  Input:
  graph is given in form {node:{node:edgeInfo}}
  nodes can be any object that can be used as a dictionary key

  Output:
  (costDict, predecessorDict) tuple, where
  costDict is {node:Tuple[edgeInfo, ...]}, with the edgeInfo along the path from start to node
  predecessorDict is {node:predecessor} the predecessor of node in the shortest path from start
  """
  costDict = {startNode:tuple()}
  predecessorDict = {}
  traversal = [startNode]

  for node in traversal:
    cost = costDict[node]
    if node == endNode:
      break
    for node2, edgeInfo in graph[node].items():
      if node2 not in traversal:
        costDict[node2] = cost + (edgeInfo,)
        predecessorDict[node2] = node
        traversal.append((node2))
  #
  return costDict, predecessorDict
