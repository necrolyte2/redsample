
from __future__ import print_function
import mock
from . import unittest
from redsample import outline, autosync

def ReadyRun():
    m = mock.MagicMock(done_ratio=20)
    m.custom_fields.resources=[{'name' : 'Run Name', 'value' : 'ARUN'}]
    return [m]

def NotReady():
    return [mock.MagicMock(done_ratio=100)]

class TestAutoSync(unittest.TestCase):
    def setUp(self):
        self.cfg = outline.config
        pass

    @mock.patch('redsample.autosync.get_my_new_runs') #, side_effect=ReadyRun)
    @mock.patch('redsample.autosync.copy_runs_samples')
    def test_sync_is_called_correctly(self, msync,  newrun):
        runs = ReadyRun()
        newrun.return_value = runs
        autosync.start()
        self.assertTrue(msync.called)
        #Mock doesn't work with partial?
        #expected_args = mock.call(ngs_data=self.cfg['destinationpath'], src='/Instruments/MiSeq/ARUN')
        expected_args = mock.call(runs[0])
        #could use assert_called_with
        self.assertEquals(msync.call_args_list[0], expected_args)
        pass

    @mock.patch('redsample.autosync.get_my_new_runs')
    def test_run_issue_precent_updated(self, newrun):
        newrun.return_value = ReadyRun()
        run = autosync.start()[0]
        self.assertEquals(run.save.call_count, 2)
        self.assertEquals(run.done_ratio, 100)

    @mock.patch('redsample.autosync.get_my_new_runs', side_effect=list)
    def test_sync_not_called_on_high_percent(self, _):
        with self.assertRaises(SystemExit):
            autosync.start()

    @mock.patch('redsample.outline.get_my_new_runs', side_effect=list)
    def test_sync_not_called_when_no_runs(self, _):
        with self.assertRaises(SystemExit):
            autosync.start()

