from collections import Mapping, Iterable
from functools import partial

from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore

from ccpn.ui.gui.widgets.Frame import Frame


# def _updateRunArgs(argsDict, arg, value):
#   argsDict[arg] = value
AUTOGEN_TAG = 'Auto-generated input:'

#TODO: document
#TODO: removed hard-coded strings

def generateWidget(params, widget, argsDict=None, columns=1):

  if argsDict is None:
    argsDict = {}

  # widget = Container()
  # # ndac = self._getNonDefaultArgCount(objMethod.run) -1  # -1 so we don't count the self arg

  from ccpn.ui.gui.widgets.Label import Label
  for i, param in enumerate(params):
    assert isinstance(param, Mapping)

    row = int(i / columns)
    column = i % columns

    frame = Frame(widget, setLayout=True)     # ejb
    frame.setObjectName('autoGeneratedFrame')
    # TODO: remove style sheet hard coding
    frameColour = '#BEC4F3' if 'dark' else '#000000'
    frame.setStyleSheet('Frame#autoGeneratedFrame {{margin:5px; border:1px solid {};}}'
                        .format(frameColour))
    try:
      widget.layout().addWidget(frame, row, column)
    except TypeError:  # Compatability between our layout and PyQt's layout()
      widget.layout.addWidget(frame, row, column)
    l = Label(frame, param.get('label', param['variable']), grid=(0, 0))
    l.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    if isinstance(param['value'], str):
      from ccpn.ui.gui.widgets.LineEdit import LineEdit
      le = LineEdit(frame, grid=(0, 1))
      le.setText(param['default'])
      le.setObjectName(AUTOGEN_TAG + param['variable'])
      setattr(widget, param['variable'], le)
      callback = partial(argsDict.__setitem__, param['variable'])
      le.textChanged.connect(callback)
      callback(le.get())

    elif isinstance(param['value'], bool):
      from ccpn.ui.gui.widgets.CheckBox import CheckBox
      cb = CheckBox(frame, checked=param['value'], grid=(0, 1))
      cb.setObjectName(AUTOGEN_TAG + param['variable'])
      setattr(widget, param['variable'], cb)
      cb.stateChanged.connect(partial(argsDict.__setitem__, param['variable']))
      cb.setCheckState(param['default'])
      argsDict[param['variable']] = param['default']


    elif isinstance(param['value'], Iterable):
      if isinstance(param['value'][0], str):
        from ccpn.ui.gui.widgets.PulldownList import PulldownList
        pdl = PulldownList(frame, texts=param['value'], grid=(0, 1))
        pdl.setObjectName(AUTOGEN_TAG + param['variable'])
        pdl.set(param.get('default', param['value'][0]))
        setattr(widget, param['variable'], pdl)
        callback = partial(argsDict.__setitem__, param['variable'])
        pdl.setCallback(callback)
        callback(pdl.get())
      elif isinstance(param['value'][0], tuple):
        if isinstance(param['value'][0][1], bool):
          from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
          t, b = zip(*param['value'])
          rb = RadioButtons(frame, texts=t,  grid=(0, 1))
          rb.setObjectName(AUTOGEN_TAG + param['variable'])
          setattr(widget, param['variable'], rb)
          rb.set(param['default'])
          rb.buttonGroup.buttonClicked[QtWidgets.QAbstractButton].connect(partial(selectedRadioButton, param=param, argsDict=argsDict))
          argsDict[param['variable']] = param['default']


        else:
          assert all([len(v) == 2 for v in param['value']])
          assert all([isinstance(v[0], str) for v in param['value']])
          from ccpn.ui.gui.widgets.PulldownList import PulldownList
          t, o = zip(*param['value'])
          pdl = PulldownList(frame, texts=t, objects=o, grid=(0, 1))
          pdl.setObjectName(AUTOGEN_TAG + param['variable'])
          pdl.set(param.get('default', param['value'][0]))
          setattr(widget, param['variable'], pdl)
          callback = partial(argsDict.__setitem__, param['variable'])
          pdl.setCallback(callback)
          callback(pdl.get())

      elif isinstance(param['value'][0], int):
        assert len(param['value']) == 2
        from ccpn.ui.gui.widgets.Spinbox import Spinbox
        sb = Spinbox(frame, min=param['value'][0], max=param['value'][1], grid=(0, 1))
        sb.setObjectName(AUTOGEN_TAG + param['variable'])
        sb.setSingleStep(param.get('stepsize', 1))
        sb.setValue(param.get('default', param['value'][0]))
        callback = partial(argsDict.__setitem__, param['variable'])
        sb.valueChanged.connect(callback)
        setattr(widget, param['variable'], sb)
        callback(sb.value())

      elif isinstance(param['value'][0], float):
        assert len(param['value']) == 2
        from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
        dsb = DoubleSpinbox(frame, min=param['value'][0], max=param['value'][1], grid=(0, 1))
        dsb.setObjectName(AUTOGEN_TAG + param['variable'])
        defaultStepSize = (param['value'][1] - param['value'][0]) / 100
        dsb.setSingleStep(param.get('stepsize', defaultStepSize))
        dsb.setValue(param.get('default', param['value'][0]))
        callback = partial(argsDict.__setitem__, param['variable'])
        dsb.valueChanged.connect(callback)
        setattr(widget, param['variable'], dsb)
        callback(dsb.value())
      else:
        raise NotImplementedError(param)
    else:
      raise NotImplementedError(param)


  return widget

def selectedRadioButton(self, argsDict, param):
  clicked = [b.text() for b in self.sender().buttons() if b.isChecked()]
  partial(argsDict.__setitem__, param['variable'])

def _getNonDefaultArgCount(self, f:callable) -> int:  # TODO: Move this to util
  import inspect
  count = 0
  sig = inspect.signature(f)
  for _, p in sig.parameters.items():
    if p.default == inspect._empty:
      count += 1
  return count

def _anyArgsVarPositional(self, f:callable) -> int:
  import inspect
  sig = inspect.signature(f)
  for _, p in sig.parameters.items():
    if p.kind == inspect._ParameterKind.VAR_POSITIONAL:
      return True
  return False