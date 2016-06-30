"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================

import functools
import itertools
import operator
import typing
from collections import OrderedDict

from ccpn.core.lib import CcpnSorting
from ccpn.core.lib import Util as coreUtil
from ccpn.util import Common as commonUtil
from ccpn.util import Pid
from ccpnmodel.ccpncore.api.memops import Implementation as ApiImplementation


@functools.total_ordering
class AbstractWrapperObject():
  """Abstract class containing common functionality for subclasses.

  ADVANCED. Core programmers only.


  **Rules for subclasses:**
  
  All collection attributes are tuples. For objects these are sorted by pid;
  for simple values they are ordered. 
  
  Non-child collection attributes must have addElement() and removeElement 
  functions as appropriate.
  
  For each child class there will be a newChild factory function, to crate
  the child object. There will be a collection attribute for each child,
  grandchild, and generally descendant.
  
  The object pid is given as NM:key1.key2.key3 ... where NM is the shortClassName,
  and the combination of key1, key2, etc. forms the id, which is the keys of the parent
  classes starting at the top.
  The pid is the object id relative to the project; keys relative to objects lower
  in the hierarchy will omit successively more keys.


  **Code organisation:**
  
  All code related to a given class lives in the file for the class. 
  On importing it, it will insert relevant functions in the parent class.
  All import must be through the ccpn module, where it is guaranteed that
  all modules are imported in the right order. 
  
  All actual data live
  in the data layer underneath these (wrapper) classes and are derived where needed.
  All data storage is done
  at the lower level, not at the wrapper level, and there is no mechanism for
  storing attributes that have been added at the wrapper level. Key and uniqueness
  checking, type checking etc.  is also done at teh lower level.
  
  Initialising happens by passing in a (lower-level) NmrProject instance to the Project
   __init__;
  all wrapper instances are created automatically starting from there. Unless we change this,
  this means we assume that all data can be found by navigating from an
  NmrProject.
  
  New classes can be added, provided they match the requirements. All classes 
  must form a parent-child tree with the root at Project. All classes must
  must have teh standard class-level attributes, such as  shortClassName, _childClasses,
  and _pluralLinkName.
  Each class must implement the properties id and _parent, and the methods 
  _getAllWrappedData,  and rename. Note that the
  properties and the _getAllWrappedData function
  must work from the underlying data, as they will be called before the pid
  and object dictionary data are set up.
  """

  #: Short class name, for PID. Must be overridden for each subclass
  shortClassName = None

  # Class name - necessary since the actual objects may be of a subclass.
  className = 'AbstractWrapperObject'

  _parentClass = None

  #: Name of plural link to instances of class
  _pluralLinkName = 'abstractWrapperClasses'

  #: List of child classes. Must be overridden for each subclass.
  _childClasses = []


  # Wrapper-level notifiers that are set up on code import and
  # registered afresh for every new project
  _coreNotifiers = []

  # Should notifiers be registered separately for this class?
  # Set to False if multiple wrapper classes wrap the same API class (e.g. PeakList, IntegralList;
  # Peak, Integral) so that API level notifiers are only registered once.
  _registerClassNotifiers = True

  # Function to generate custom subclass instances -= overridden in some subclasses
  _factoryFunction = None

  # Default values for paraeters to 'new' function. Overridden in subclasses
  _defaultInitValues = None
  
  # Implementation methods
  
  def __init__(self, project:'Project', wrappedData:ApiImplementation.DataObject):
   
    # NB project parameter type is Project. Set in Project.py
    
    # NB wrappedData must be globally unique. CCPN objects all are, 
    # but for non-CCPN objects this must be ensured.
    
    # Check if object is already wrapped
    data2Obj = project._data2Obj
    if wrappedData in data2Obj:
      raise ValueError("Cannot create new object for underlying %s: One  already exists"
                       % wrappedData)

    # initialise
    self._project = project
    self._wrappedData = wrappedData
    data2Obj[wrappedData] = self
      
    # set _id
    parent = self._parent
    if parent is project:
      _id = str(self._key)
    else:
      _id = '%s%s%s'% (parent._id, Pid.IDSEP, self._key)
    self._id = _id
    
    # update pid:object mapping dictionary
    dd = project._pid2Obj.get(self.className)
    if dd is None:
      dd = {}
      project._pid2Obj[self.className] = dd
      project._pid2Obj[self.shortClassName] = dd
    dd[_id] = self


  def __bool__(self):
    """Truth value: true - wrapper classes are never empty"""
    return True
  
  def __lt__(self, other):
    """Ordering implementation function, necessary for making lists sortable.
    """
    if self._project is other._project:
      className1 = self.className
      className2 = other.className
      if className1 == className2:
        return (CcpnSorting.stringSortKey(self._id) < CcpnSorting.stringSortKey(other._id))
      else:
        return (className1 < className2)
    else:
      return (id(self._project) < id(other._project))


  def __repr__(self):
    """String representation"""
    return "<ccpn.%s>" % self.longPid

  def __eq__(self, other):
    """Python 2 behaviour - objects equal only to themselves."""
    return self is other

  def __ne__(self, other):
    """Python 2 behaviour - objects equal only to themselves."""
    return self is not other

  def __hash__(self):
    """Python 2 behaviour - objects equal only to themselves."""
    return hash(id(self))
  
  # CCPN properties 
  @property
  def project(self) -> 'Project':
    """The Project (root)containing the object."""
    return self._project
  
  @property
  def pid(self) -> Pid.Pid:
    """Identifier for the object, unique within the project.
    Set automatically from the short class name and object.id
    E.g. 'NA:A.102.ALA.CA' """
    return Pid.Pid(Pid.PREFIXSEP.join((self.shortClassName, self._id)))
  
  @property
  def longPid(self) -> Pid.Pid:
    """Identifier for the object, unique within the project.
    Set automatically from the full class name and object.id
    E.g. 'NmrAtom:A.102.ALA.CA' """
    return Pid.Pid(Pid.PREFIXSEP.join((self.className, self._id)))

  @property
  def isDeleted(self) -> bool:
    """Is object deleted?"""
    return (not hasattr(self, '_wrappedData') or self._wrappedData is None)
  
  # CCPN abstract properties
  
  @property
  def _key(self) -> str:
    """Object local identifier, unique for a given type with a given parent.

    Set automatically from other (immutable) object attributes."""
    raise NotImplementedError("Code error: function not implemented")
  
  @property
  def _parent(self):
    """Parent (containing) object."""
    raise NotImplementedError("Code error: function not implemented")

  @property
  def id(self)->str:
    """Identifier for the object, used to generate the pid and longPid.

    Generated by combining the id of the containing object,
    with the value of one or more key attributes that uniquely identify the object in context.::

      E.g. the id for an Atom, 'A.55.VAL.HA' is generated from:

      - 'A' *Chain.shortName*

      - '55' *Residue.sequenceCode*

      - 'VAL' *Residue.residueType*

      - 'HA' *Atom.name*"""

    return self._id
  
  # Abstract methods
  @classmethod
  def _getAllWrappedData(cls, parent)-> list:
    """get list of wrapped data objects for each class that is a child of parent
    """
    if cls not in parent._childClasses:
      raise Exception
    raise NotImplementedError("Code error: function not implemented")

  def rename(self, value:str):
    """Change the object name or other key attribute(s), changing the object id, pid,
       and all internal references to maintain consistency.
       Some Objects (Chain, Residue, Atom) cannot be renamed"""
    raise ValueError("%s objects cannot be renamed" % self.__class__.__name__)
  
  # In addition each class (except for Project) must define a  newClass method
  # The function (e.g. Project.newMolecule), ... must create a new child object
  # AND ALL UNDERLYING DATA, taking in all parameters necessary to do so. 
  # This can be done by defining a function (not a method)
  # def newMolecule( self, *args, **kw):
  # and then doing Project.newMolecule = newMolecule

  # CCPN functions


  def delete(self):
    """Delete object, with all contained objects and underlying data."""
    
    # NBNB clean-up of wrapper structure is done via notifiers.
    # NBNB some child classes must override this function
    self._wrappedData.delete()

  def getByPid(self, pidstring:str) :
    """Get an arbitrary ccpn.Object from either its pid (e.g. 'SP:HSQC2') or its longPid
    (e.g. 'Spectrum:HSQC2'

    Returns None for invalid or unrecognised input strings."""

    tt = pidstring.split(Pid.PREFIXSEP,1)
    if len(tt) == 2:
      dd = self._project._pid2Obj.get(tt[0])
      if dd:
        return dd.get(tt[1])
    #
    return None

  def _getWrapperObject(self, apiObject:ApiImplementation.DataObject):
    """get wrapper object wrapping apiObject or None"""
    return self._project._data2Obj.get(apiObject)
    
  # CCPN Implementation methods

  @classmethod
  def _linkWrapperClasses(cls, ancestors:list=None, Project:'Project'=None):
    """Recursively set up links and functions involving children for wrapper classes

    NB classes that have already been linked are ignored, but their children are still processed"""

    if Project:
      assert ancestors, "Code errors, _linkWrapperClasses called with Project but no ancestors"
      newAncestors = ancestors + [cls]
      if cls not in Project._allLinkedWrapperClasses:
        Project._allLinkedWrapperClasses.append(cls)
        # add getCls in all ancestors
        funcName = 'get' + cls.className
        #  NB Ancestors is never None at this point
        for ancestor in ancestors:
          # Add getDescendant function
          def func(self,  relativeId: str) -> cls:
            return cls._getDescendant(self, relativeId)
          func.__doc__= "Get contained %s object by relative ID" % cls
          setattr(ancestor, funcName, func)

        # Add descendant links
        linkName = cls._pluralLinkName
        for ii in range(len(newAncestors)-1):
          ancestor = newAncestors[ii]
          func = functools.partial(AbstractWrapperObject._allDescendants,
                                            descendantClasses=newAncestors[ii+1:])
          # func.__annotations__['return'] = typing.Tuple[cls, ...]
          prop = property(func,
                            None, None,
                            ("\- *(%s,)*  - contained %s objects sorted by id" %
                              (cls, cls.className)
                            )
                          )
          setattr(ancestor, linkName, prop)


        # Add standard Notifiers:
        if cls._registerClassNotifiers:
          className = cls._apiClassQualifiedName
          Project._apiNotifiers[:0] = [
            ('_newApiObject', {'cls':cls}, className, '__init__'),
            ('_startDeleteCommandBlock', {}, className, 'startDeleteBlock'),
            ('_finaliseApiDelete', {}, className, 'delete'),
            ('_endCommandBlock', {}, className, 'endDeleteBlock'),
            ('_finaliseApiUnDelete', {}, className, 'undelete'),
            ('_modifiedApiObject', {}, className, ''),
        ]
    else:
      # Project class. Start generation here
      Project = cls
      ll = Project._allLinkedWrapperClasses
      if ll:
        print("DEBUG initialisation attempted more than once")
        return
      newAncestors = [cls]
      ll.append(Project)

    # Fill in Project._className2Class map
    dd = Project._className2Class
    dd[cls.className] = dd[cls.shortClassName] = cls

    # recursively call next level down the tree
    for cc in cls._childClasses:
      cc._linkWrapperClasses(newAncestors, Project=Project)

  @classmethod
  def _getDescendant(cls, self,  relativeId: str):
    """Get descendant of class cls with relative key relativeId
     Implementation function, used to generate getCls functions"""

    dd = self._project._pid2Obj.get(cls.className)
    if dd:
        if self is self._project:
            key = relativeId
        else:
            key = '%s%s%s' % (self._id,Pid.IDSEP, relativeId)
        return dd.get(key)
    else:
      return None

  def _allDescendants(self, descendantClasses):
    """get all descendants of a given class , following descendantClasses down the data tree
    Implementation function, used to generate child and descendant links
    descendantClasses is a list of classes going down from the class of self down the data tree.
    E.g. if called on a chain with descendantClass == [Residue,Atom] the function returns
    a sorted list of all Atoms in a Chain"""
    project = self._project
    data2Obj = project._data2Obj
    objects = [self]

    for cls in descendantClasses:

      # function gets wrapped data for all children starting from parent
      func = cls._getAllWrappedData
      # data is iterator of wrapped data for children starting from all parents
      ll = itertools.chain(*(func(x) for x in objects))
      # objects is all wrapper objects for next child level down
      objects = [data2Obj[x] for x in ll]
      if cls.className in ('ChemicalShift', 'Residue'):
        # These cannot be correctly sorted at the API level
        objects.sort()
    #
    return objects

  def _initializeAll(self):
    """Initialize children, using existing objects in data model"""

    project = self._project
    data2Obj = project._data2Obj

    for childClass in self._childClasses:
      # recursively create children
      for apiObj in childClass._getAllWrappedData(self):
        obj = data2Obj.get(apiObj)
        if obj is None:
          factoryFunction = childClass._factoryFunction
          if factoryFunction is None:
            obj = childClass(project, apiObj)
          else:
            obj = factoryFunction(project, apiObj)
        obj._initializeAll()


  def _unwrapAll(self):
    """remove wrapper from object and child objects
    For special case where wrapper objects are removed without deleting wrappedData"""
    project = self._project
    data2Obj = project._data2Obj

    for childClass in self._childClasses:

      # recursively unwrap children
      for apiObj in childClass._getAllWrappedData(self):
        obj = data2Obj.get(apiObj)
        if obj is not None:
          obj._unwrapAll()
          del self._pid2Obj[obj.shortClassName][obj._id]
        del data2Obj[apiObj]

  def _setUniqueStringKey(self, apiObj:'ccpn.api.memops.Implementation.DataObject',
                          defaultValue:str, keyTag:str='name') -> str:
    """(re)set obj.keyAttr to make it a unique key, using defaultValue if not set
    NB - if called BEFORE data2obj etc. dictionaries are set"""

    wrappedData = self._wrappedData
    if not hasattr (wrappedData,keyTag):
      raise ValueError("Cannot set unique %s for %s: %s object has no attribute %s"
                       % (keyTag, self, wrappedData.__class__, keyTag))

    undo = self._project._undo
    if undo is not None:
      undo.increaseBlocking()
    try:
      if wrappedData not in self._project._data2Obj:
        # Necessary because otherwise we likely will have notifiers - that would then break
        wrappedData.root.override = True
      # Set default value if present value is None
      value = getattr(wrappedData, keyTag)
      if value is None:
        value = defaultValue
        setattr(wrappedData, keyTag, value)

      # Set to new, unique value if present value is a duplicate
      apiObjects = self._getAllWrappedData(self._parent)
      for apiSibling in apiObjects:
        if apiSibling is wrappedData:
          # We have reached the object itself in the list. Enough
          break
        elif getattr(apiSibling, keyTag) == value:
          # Object name is duplicate of earlier object name - make unique name

          # First try appending serial, if possible
          if hasattr(apiObj, 'serial'):
            value = '%s-%s' % (value, apiObj.serial)
          else:
            value = commonUtil.incrementName(value)
          while any(x for x in apiSibling if getattr(x, keyTag) == value):
            value = commonUtil.incrementName(value)
          setattr(self, keyTag, value)
          break
    finally:
      if wrappedData not in self._project._data2Obj:
        wrappedData.root.override = False
      if undo is not None:
        undo.decreaseBlocking()

  def _getDirectChildren(self):
    """Get list of objects that have self as a parent"""

    getDataObj = self._project._data2Obj.get
    return list(getDataObj(y) for x in self._childClasses for y in x._getAllWrappedData(self))

  # NOtifiers and related functions:

  @classmethod
  def _setupCoreNotifier(cls, target:str, func:typing.Callable,
                       parameterDict:dict={}, onceOnly:bool=False):
    """Set up notifiers for class cls that do not depend on individual objects -
    These will be registered whenever a new project is initialised.
    Parameters are eventually passed to the project.registerNotifier() function
    (with cls converted to cls.className). Please see the Project.registerNotifier
    documentation for a precise parameter description

    Note that these notifiers are NOT cleared once set up.
    """

    # CCPNINTERNAL - used in top level class definitions, Current (ONLY)


    # NB _coreNotifiers is a class attribute of AbstractWrapperObject
    # So all tuples are appended to the same list, living in AbstractWrapperObject
    cls._coreNotifiers.append((cls.className, target, func, parameterDict, onceOnly))


  def _finaliseRename(self):
    """Reset internal attributes and call notifiers after values determining PID have changed
    """

    # reset id
    project = self._project
    oldId = self._id
    parent = self._parent
    if parent is None:
      _id = ''
    elif parent is project:
      _id = str(self._key)
    else:
      _id = '%s%s%s'% (parent._id, Pid.IDSEP, self._key)
    self._id = _id

    # update pid:object mapping dictionary
    dd = project._pid2Obj[self.className]
    del dd[oldId]
    dd[_id] = self

  def _finaliseRelatedObjectFromRename(self, oldPid, pathToObject:str, action:str):
    """Finalise related objects after rename
    Alternative to _finaliseRelatedObject for calling from rename notifier.
    """
    target = operator.attrgetter(pathToObject)(self)
    if not target:
      pass
    elif isinstance(target, AbstractWrapperObject):
      target._finaliseAction(action)
    else:
      # This must be an iterable
      for obj in target:
        obj._finaliseAction(action)

  def _finaliseRelatedObject(self, pathToObject:str, action:str):
    """ Finalise 'action' type notifiers for getattribute(pathToObject)(self)
    pathToObject is a navigation path (may contain dots) and must yield an object
    or an iterable of objects. Can NOT be called from a rename notifier"""

    target = operator.attrgetter(pathToObject)(self)
    if not target:
      pass
    elif isinstance(target, AbstractWrapperObject):
      target._finaliseAction(action)
    else:
      # This must be an iterable
      for obj in target:
        obj._finaliseAction(action)

  def _finaliseAction(self, action:str):
    """Do wrapper level finalisation, and execute all notifiers

    action is one of: 'create', 'delete', 'change', 'rename'"""

    project = self.project
    if project._notificationBlanking:
      return

    className = self.className
    iterator = (project._context2Notifiers.setdefault((name, action), OrderedDict())
               for name in (className, 'AbstractWrapperObject'))
    ll = project._pendingNotifications

    if action == 'rename':
      # Special case

      oldPid = self.pid

      # Wrapper-level processing
      self._finaliseRename()

      # Call notifiers with special signature
      if project._notificationSuspension:
        for dd in iterator:
          for notifier, onceOnly in dd.items():
            ll.append((notifier, onceOnly, self, oldPid))
      else:
        for dd in iterator:
          for notifier in dd:
            notifier(self, oldPid)

      for obj in self._getDirectChildren():
        obj._finaliseAction('rename')

    else:
      # Normal case - just call notifiers
      if project._notificationSuspension:
        for dd in iterator:
          for notifier, onceOnly in dd.items():
            ll.append((notifier, onceOnly, self))
      else:
        for dd in iterator:
          for notifier in dd:
            self._project._logger.debug('finaliseAction notifier: %s; %s; %s'
                                        % (action, self, notifier))
            notifier(self)

  def _startFunctionCommandBlock(self, funcName, *params, values=None, defaults=None, parName=None):
    """Execute StartCommandBlock for an object creation function,
    """

    #CCPNINTERNAL

    project = self._project

    parameterString = coreUtil.commandParameterString(*params, values=values, defaults=defaults)

    if self is project:
      command = "project.%s(%s)" % (funcName, parameterString)
    else:
      command = "project.getByPid(%s).%s(%s)" % (self.pid, funcName, parameterString)

    if parName:
      command = ''.join((parName, ' = ', command))

    project._appBase._startCommandBlock(command)


AbstractWrapperObject.getByPid.__annotations__['return'] = AbstractWrapperObject
