"""
The control package of expyriment.

"""

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.10.0'
__revision__ = 'bac5b00'
__date__ = 'Wed Oct 30 23:26:23 2019 +0100'


from . import defaults
from ._miscellaneous import start_audiosystem, stop_audiosystem, \
        get_audiosystem_is_playing, wait_end_audiosystem, \
        set_develop_mode, get_defaults, register_wait_callback_function, \
        unregister_wait_callback_function
from .._internals import CallbackQuitEvent
from ._experiment_control import initialize, start, pause, end
from ._test_suite import run_test_suite
