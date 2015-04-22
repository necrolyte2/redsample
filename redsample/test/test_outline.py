from __future__ import print_function
from . import unittest, mock, json_response, CONFIG_EXAMPLE
from redsample import config
from redsample import outline
from collections import namedtuple
import io

'''
cut until after [Data] header
parse as CSV using pandas
'''

def create():
    for i in [-1, 3, 5, 8, 4]: yield mock.MagicMock(id=i)
def all_issue_hits(**kwargs):
    yield Missue('_fo o', {}, 8)
    yield Missue('BLANK', {'PR Name' : 'BAR'}, 2)

class TestSampleSheet(unittest.TestCase):

    def setUp(self):
        self.sheet = open('test/SampleSheet.csv')

#def test_get_csv_from_samplesheet(self):
#    expected = '''Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description'''
#    actual = outline.get_csv_substring(self.sheet)

    def test_ss_to_data_frame(self):
        df = outline.sample_sheet_to_df(self.sheet)
        actual = df.ix[0].tolist()
        expected = [ "011515DV1-WesPac74", "011515DV1-WesPac74", "20150317_Den_YFV_JEV_WNV",
         "A01", "N701", "TAAGGCGA", "S502", "CTCTCTAT", "PhiX\Illumina\RTA\Sequence\WholeGenomeFasta",
         float("nan"), float("nan") ]
        #Note: nan will never equal nan, so slice
        self.assertEquals(expected[:-2], actual[:-2])

    def test_read_sample_sheet(self):
        expected = [("011515DV1-WesPac74", "011515DV1-WesPac74"), ("00132-06","00132-06")]
        samples = outline.read_sample_sheet(self.sheet)
        actual = [(sample.name, sample.sample_id) for sample in samples[:2]]
        self.assertEquals(expected[0], actual[0])
        self.assertEquals(expected[1], actual[1])

#api_key='a192502d2a96958bdd4231b5f2292e5b2ae13e1a'
#redmine = Redmine('https://www.vdbpm.org', key=api_key)
#all = redmine.issue.all(project_id=18, tracker_id=6)
#print all[0]


responses = {
    'Sample': {
        'get': {'issue': {'subject': 'sample1', 'id': 1}},
        'all': {'issues': [{'subject': 'sample1', 'id': 1},{'subject': 'sample2', 'id': 2}]},
        'filter': {'issues': [{'subject': 'sample1', 'id': 1},{'subject': 'sample2', 'id': 2}]},
    }
}
#Missue = namedtuple("Missue", ("subject", "custom_fields.resources", "id"))


def Missue(a, b, c):
    m = mock.MagicMock( id=c)
    m.custom_fields.resources=[{'name' : 'PR Name', 'value' : b.get('PR Name', None)}]
    #TODO: fix this
    m.__getitem__.side_effect = lambda x, b=a: b
    return m

class TestSamplesmanager(unittest.TestCase):
    def setUp(self):
        self.config = config.load_config(CONFIG_EXAMPLE)

class TestSamplesResource(unittest.TestCase):
    def setUp(self):
        self.config = config.load_config(CONFIG_EXAMPLE)
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
        self.missues = map(lambda x: Missue(*x), [('ABA', {'PR Name' : 'miss'}, 1),
                           ('AA_-B', {'PR Name' : 'PRFOO'}, 2),
                           ('PRFoo', {'PR Name' : ''}, 3),
                           ('HIT',  {"PR Name" : "pr foO"}, 4)])


    def test_retrieves_only_samples_from_sampleproj(self):
            self.response.json = json_response(responses['Sample']['all'])
            issues = outline.all_samples()
            self.assertEqual(issues[0].id, 1)
            self.assertEqual(issues[0].subject, 'sample1')
            self.assertEqual(issues[1].id, 2)
            self.assertEqual(issues[1].subject, 'sample2')
            args, kwargs = self.mock_get.call_args
            params_sent = kwargs['params']
            self.assertEqual(params_sent['project_id'], self.config['sampleprojectid'])
            self.assertEqual(params_sent['tracker_id'], self.config['sampletrackerid'])



    def test_find_sample_by_subject(self):
        missues = map(lambda x: Missue(*x), [('ABA', {}, 0), ('AA_-B', {}, 0), ('ABAA', {}, 0)])
        sample = outline.Sample('AA//b', 'foo')
        actual = outline.find_sample(sample, missues)
        self.assertEquals(missues[1], actual)

    def test_find_sample_by_pr(self):
        sample = outline.Sample('PR-Foo', 'foo')
        actual = outline.find_sample(sample, self.missues)
        self.assertEquals(self.missues[-1], actual)


    #TODO: How test get-or-create?
    #Note: mock still counts a call even if it got partial'd
    @mock.patch('redsample.outline.redmine.issue.create')
    def test_get_or_create_wont_recreate(self, mcreate):
        #TODO: set response to include the sample I want to create
        pass

    @mock.patch('redsample.outline.redmine.issue.create')
    def test_get_or_create_will_create_new(self, mcreate):
        #TODO: set response to NOT include a sample, insure mcreate got called
        pass


    #TODO: Test this with must-create issues
    #TODO: can't seem to mock issue.all
    @mock.patch('redsample.outline.raw_all_samples')#redmine.issue.all') #, side_effect=all_issue_hits)
    def test_sync_samples(self, mall):
        mall.return_value = all_issue_hits()
        _input = map(lambda x: outline.Sample(*x), [("-fo-o", "fooid"), ("bar", "barid")])
        expected = {"-fo-o" : 8, "bar" : 2}
        actual = outline.sync_samples(_input)
        self.assertEquals(expected, actual)

    def test_sample_id_map_str(self):
        expected = set("Sample Name\tIssue ID\n_name_\t3\n_other_name_\t5".split('\n'))
        _input = {"_name_" : 3, "_other_name_" : 5}
        actual = set(outline.sample_id_map_str(_input).split('\n'))
        self.assertEquals(expected, actual)


    @mock.patch('redsample.outline.make_run_block')
    @mock.patch('redsample.outline.redmine.issue.all', side_effect=all_issue_hits)
    @mock.patch('redsample.outline.create_sample_issue')
    def test_execute_functional_create_all(self,  mcreate, mall, mblock):
        ss_string = '''[crud]asdf\n\n[morecrud]asdf\nData\n[Data]\n
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description
_name_,_name_,,,,,,,,,
_other_name_,foo,,,,,,,,,
fo-o,foo,,,,,,,,,
bar,baz,,,,,,,,,'''
# Should strip?
        mcreate.side_effect = create()
        self.response.json = json_response( {'issues': [{'subject': 'sample1', 'id': 1, 'custom_fields' : [{}]},{'subject': 'sample2', 'id': 2, 'custom_fields' : [{}]}]})
        with mock.patch('__builtin__.open', mock.mock_open(read_data=ss_string), create = True) as m:
            actual = set(outline.execute('somedir/nonsense').split('\n'))
        expected = set("Sample Name\tIssue ID\n_name_\t3\n_other_name_\t5\nfo-o\t8\nbar\t4".split('\n'))
        self.assertEquals(expected, actual)
        self.assertEquals(mblock.call_count, 4)
        self.assertEquals(mcreate.call_count, 5)
        samplenames = ['_name_', '_other_name_', 'fo-o', 'bar']
#        self.assertEquals(set(mcreate.call_args_list), set(map(lambda x: mock.call(subject=x), samplenames)))
#        self.assertEquals(set(mblock.call_args_list), set(map(mock.call, [3, 5, 8, 4])))
        #Need this because dicts are unhashable
        map(self.assertTrue, map(mcreate.call_args_list.__contains__, map(lambda x: mock.call(subject=x), samplenames)))
        map(self.assertTrue, map(mblock.call_args_list.__contains__, map(mock.call, [3, 5, 8, 4])))
        expected_run_issue_call = mock.call(custom_fields={'SampleList': '\n'.join(samplenames),
                                                   'Samples Synced' : 'No',
                                                   'Run Name' : 'somedir'},
                                    subject='somedir')
        self.assertEquals(expected_run_issue_call, mcreate.call_args_list[0])



