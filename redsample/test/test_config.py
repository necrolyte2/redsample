try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

from os.path import *
import tempfile

import mock

from .. import config

# Example config
CONFIG_EXAMPLE = join(dirname(dirname(dirname(__file__))), 'redsample.config.example')

class TestGetConfig(unittest.TestCase):
    def test_loads_config(self):
        r = config.load_config(CONFIG_EXAMPLE)
        keys = (
            'siteurl', 'apikey', 'sampleprojectid', 'sampletrackerid'
        )
        for key in keys:
            self.assertIn(key, r)

class TestLoadUserConfig(unittest.TestCase):
    def test_loads_from_homedir_path(self):
        with mock.patch.object(config, 'yaml') as mock_yaml:
            with mock.patch.object(builtins, 'open') as mock_open:
                c = config.load_user_config()
                homeconf = expanduser('~/.redsample.config')
                self.assertEqual(
                    homeconf,
                    mock_open.call_args_list[0][0][0]
                )
