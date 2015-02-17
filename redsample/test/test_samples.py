from . import unittest, mock, json_response, CONFIG_EXAMPLE, builtins

from .. import samples, config
Samples = samples.Samples

responses = {
    'Sample': {
        'get': {'issue': {'subject': 'sample1', 'id': 1}},
        'all': {'issues': [{'subject': 'sample1', 'id': 1},{'subject': 'sample2', 'id': 2}]},
        'filter': {'issues': [{'subject': 'sample1', 'id': 1},{'subject': 'sample2', 'id': 2}]},
    }
}

class TestRedSample(unittest.TestCase):
    def setUp(self):
        self.config = config.load_config(CONFIG_EXAMPLE)
        self.redsample = samples.RedSample(self.config)

    def test_initializes_correctly(self):
        self.assertEqual(self.redsample.url, self.config['siteurl'])
        self.assertEqual(self.redsample.key, self.config['apikey'])
        self.assertEqual(self.redsample.custom_resource_paths, ('redsample.samples',))

    def test_gets_samples_manager(self):
        _samples = self.redsample.Samples
        self.assertIsInstance(_samples, samples.SamplesManager)
        self.assertEqual(
            self.config['sampleprojectid'],
            _samples.resource_class.project_id
        )
        self.assertEqual(
            self.config['sampletrackerid'],
            _samples.resource_class.tracker_id
        )

class TestSamplesmanager(unittest.TestCase):
    def setUp(self):
        self.config = config.load_config(CONFIG_EXAMPLE)
        self.redsample = samples.RedSample(self.config)

    def test_sets_redmine_attribute(self):
        self.assertEqual(
            self.redsample.Samples.redmine,
            self.redsample
        )

    def test_sets_correct_resource_class(self):
        self.assertIs(
            self.redsample.Samples.resource_class,
            samples.Samples
        )

class TestSamplesResource(unittest.TestCase):
    def setUp(self):
        self.config = config.load_config(CONFIG_EXAMPLE)
        self.redmine = samples.RedSample(self.config)
        self.response = mock.Mock(status_code=200)
        self.patcher_get = mock.patch('requests.get', return_value=self.response)
        self.patcher_post = mock.patch('requests.post', return_value=self.response)
        self.patcher_put = mock.patch('requests.put', return_value=self.response)
        self.patcher_delete = mock.patch('requests.delete', return_value=self.response)
        self.mock_get = self.patcher_get.start()
        self.patcher_post.start()
        self.patcher_put.start()
        self.patcher_delete.start()
        self.addCleanup(self.patcher_get.stop)
        self.addCleanup(self.patcher_post.stop)
        self.addCleanup(self.patcher_put.stop)
        self.addCleanup(self.patcher_delete.stop)

    def test_is_redmine_resourcemanager(self):
        from redmine.managers import ResourceManager
        self.assertIsInstance(self.redmine.Samples, ResourceManager)

    def test_retrieves_only_samples_from_sampleproj(self):
        self.response.json = json_response(responses['Sample']['all'])
        issues = self.redmine.Samples.all()
        self.assertEqual(issues[0].id, 1)
        self.assertEqual(issues[0].subject, 'sample1')
        self.assertEqual(issues[1].id, 2)
        self.assertEqual(issues[1].subject, 'sample2')
        args, kwargs = self.mock_get.call_args
        params_sent = kwargs['params']
        self.assertEqual(params_sent['project_id'], self.config['sampleprojectid'])
        self.assertEqual(params_sent['tracker_id'], self.config['sampletrackerid'])
