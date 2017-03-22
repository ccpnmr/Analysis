
from ccpn.framework.lib.Plugin import Plugin

class AutoGeneratedDevPlugin(Plugin):
  PLUGINNAME = 'Development Plugin...Auto-generated UI'
  params = [{'variable': 'param1',
                        'value': ('Fast', 'Slow'),
                        'label': 'Param #1',
                        'default': 'Fast'},  # List

                       {'variable': 'param2',
                        'value': False,
                        'default': 0},  # checkbox 0 unchecked 2 checked

                       {'variable': 'param3',
                        'value': (('White 1', False), ('Red 2', True)),  # RadioButtons
                        'default': 'Red 2'},

                       {'variable': 'param4',
                        'value': ('0', '4'),
                        'default': 4},  # List

                       {'variable': 'param5',  # Spinbox
                        'value': (0, 4),
                        'default': (3)},

                       {'variable': 'param6',  # Spinbox with default
                        'value': (0, 4),
                        'default': 2},

                       {'variable': 'param7',  # Spinbox with stepsize
                        'value': (0, 4),
                        'stepsize': 2,
                        'default': 3},

                       {'variable': 'param8',  # Spinbox with default and stepsize
                        'value': (0, 4),
                        'stepsize': 2,
                        'default': 2},

                       {'variable': 'param9',  # Double Spinbox
                        'value': (0., 1),
                        'default': 0.3},

                       {'variable': 'param10',  # Double Spinbox with default
                        'value': (0., 1.),
                        'default': 0.2},

                       {'variable': 'param11',  # Double Spinbox with stepsize
                        'value': (0., 1.),
                        'stepsize': 0.1,
                        'default': 0.2},

                       {'variable': 'param12',  # Double Spinbox with default and stepsize
                        'value': (0., 1),
                        'stepsize': 0.1,
                        'default': 0.2},

                       {'variable': 'param13',  # LineEdit
                        'value': '',
                        'default': 'param13'},

                       {'variable': 'param14',
                        'value': (('Ford', 'Focus'),  # Mapped list
                                  ('BMW', '320'),
                                  ('Fiat', '500')
                                  ),
                        'default': 'Focus'},
                       ]
  settings = [{'variable': 'param1s',
                          'value': ('Fast', 'Slow'),
                          'label': 'Param #1',
                          'default': 'Fast'},  # List

                         {'variable': 'param2s',
                          'value': False,
                          'default': 0},  # checkbox 0 unchecked 2 checked

                         {'variable': 'param3s',
                          'value': (('White 1', False), ('Red 2', True)),  # RadioButtons
                          'default': 'Red 2'},

                         {'variable': 'param4s',
                          'value': ('0', '4'),
                          'default': 4},  # List

                         {'variable': 'param5s',  # Spinbox
                          'value': (0, 4),
                          'default': (3)},

                         {'variable': 'param6s',  # Spinbox with default
                          'value': (0, 4),
                          'default': 2},

                         {'variable': 'param7s',  # Spinbox with stepsize
                          'value': (0, 4),
                          'stepsize': 2,
                          'default': 3},

                         {'variable': 'param8s',  # Spinbox with default and stepsize
                          'value': (0, 4),
                          'stepsize': 2,
                          'default': 2},

                         {'variable': 'param9s',  # Double Spinbox
                          'value': (0., 1),
                          'default': 0.3},

                         {'variable': 'param10s',  # Double Spinbox with default
                          'value': (0., 1.),
                          'default': 0.2},

                         {'variable': 'param11s',  # Double Spinbox with stepsize
                          'value': (0., 1.),
                          'stepsize': 0.1,
                          'default': 0.2},

                         {'variable': 'param12s',  # Double Spinbox with default and stepsize
                          'value': (0., 1),
                          'stepsize': 0.1,
                          'default': 0.2},

                         {'variable': 'param13s',  # LineEdit
                          'value': '',
                          'default': 'param13'},

                         {'variable': 'param14s',
                          'value': (('Ford', 'Focus'),  # Mapped list
                                    ('BMW', '320'),
                                    ('Fiat', '500')
                                    ),
                          'default': 'Focus'},
                         ]

  def run(self, **kwargs):
    print('Run', kwargs)