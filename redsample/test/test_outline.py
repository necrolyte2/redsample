from __future__ import print_function
from . import unittest, mock, json_response, CONFIG_EXAMPLE
from redsample import config
from redsample import outline
import os
from os import path
from functools import partial
import shutil
'''
cut until after [Data] header
parse as CSV using pandas
'''
THISD = os.path.dirname(os.path.abspath(__file__))
here = partial(os.path.join, THISD)
def create():
    for i in [3, 5, 8, 4]: yield mock.MagicMock(id=i)
def all_issue_hits(**kwargs):
    yield Missue('_fo o', {}, 8)
    yield Missue('BLANK', {'PR Name' : 'BAR'}, 2)

class TestSampleSheet(unittest.TestCase):

    def setUp(self):
        self.sheet = open(path.join(THISD, 'SampleSheet.csv'))
        self.ss_string = '''[crud]asdf\n\n[morecrud]asdf\nData\n[Data]\n
Sample_Name,Sample_ID,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description
_name_,_name_,,,,,,,,,
_other_name_,foo,,,,,,,,,
fo-o,foo,,,,,,,,,
bar,baz,,,,,,,,,'''

    def test_ss_to_data_frame(self):
        df = outline.sample_sheet_to_df(self.sheet)
        actual = df.ix[0].tolist()
        expected = [ "011515DV1-WesPac74", "011515DV1-WesPac74", "20150317_Den_YFV_JEV_WNV",
         "A01", "N701", "TAAGGCGA", "S502", "CTCTCTAT", "PhiX\Illumina\RTA\Sequence\WholeGenomeFasta",
         float("nan"), float("nan") ]
        #Note: nan will never equal nan, so slice
        self.assertEquals(expected[:-2], actual[:-2])


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
        self.ss_string = '''[crud]asdf\n\n[morecrud]asdf\nData\n[Data]\n
Sample_Name,Sample_ID,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description
_name_,_name_,,,,,,,,,
_other_name_,foo,,,,,,,,,
fo-o,foo,,,,,,,,,
bar,baz,,,,,,,,,'''
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


#    def test_retrieves_only_samples_from_sampleproj(self):
#            self.response.json = json_response(responses['Sample']['all'])
#            issues = outline.all_samples()
#            self.assertEqual(issues[0].id, 1)
#            self.assertEqual(issues[0].subject, 'sample1')
#            self.assertEqual(issues[1].id, 2)
#            self.assertEqual(issues[1].subject, 'sample2')
#            args, kwargs = self.mock_get.call_args
#            params_sent = kwargs['params']
#            self.assertEqual(params_sent['project_id'], self.config['sampleprojectid'])
#            self.assertEqual(params_sent['tracker_id'], self.config['sampletrackerid'])



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


    @mock.patch('redsample.outline.create_run_issue')
    @mock.patch('redsample.outline.make_run_block')
    @mock.patch('redsample.outline.redmine.issue.all', side_effect=all_issue_hits)
    @mock.patch('redsample.outline.create_sample_issue')
    def test_execute_functional_create_all(self,  mcreate, mall, mblock, rcreate):
        mcreate.side_effect = create()
        self.response.json = json_response( {'issues': [{'subject': 'sample1', 'id': 1, 'custom_fields' : [{}]},{'subject': 'sample2', 'id': 2, 'custom_fields' : [{}]}]})
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.ss_string), create = True) as m:
            actual_df, mapping_str = outline.execute(open('somedir/nonsense'), 'somedir')
            actual_str = set(mapping_str.split('\n'))
        expected = set("Sample Name\tIssue ID\n_name_\t3\n_other_name_\t5\nfo-o\t8\nbar\t4".split('\n'))
        self.assertEquals(expected, actual_str)
        self.assertEquals(mblock.call_count, 4)
        self.assertEquals(mcreate.call_count, 4)
        self.assertEquals(rcreate.call_count, 1)
        samplenames = map(str.upper, ['_name_', '_other_name_', 'fo_o', 'bar'])
        #Need this because dicts are unhashable
        map(self.assertTrue, map(mcreate.call_args_list.__contains__, map(lambda x: mock.call(subject=x), samplenames)))
        #map(self.assertTrue, map(mblock.call_args_list.__contains__, map(mock.call, [3, 5, 8, 4])))
        expected_run_issue_call = mock.call(custom_fields={ 'Samples Synced' : 'No',
                                                   'Run Name' : 'somedir'},
                                    subject='somedir')
        self.assertEquals(expected_run_issue_call, rcreate.call_args_list[0])

    @mock.patch('redsample.outline.sys')
    @mock.patch('redsample.outline.create_run_issue')
    @mock.patch('redsample.outline.make_run_block')
    @mock.patch('redsample.outline.redmine.issue.all', side_effect=all_issue_hits)
    @mock.patch('redsample.outline.create_sample_issue')
    def test_functional_final_sample_sheet(self,  mcreate, mall, mblock, rcreate, msys):
        mcreate.side_effect = create()
        csv_path = here('test_ss.csv')
        with open(csv_path, 'w') as out:
            out.write(self.ss_string)
        msys.argv = ['_', csv_path]
        self.response.json = json_response( {'issues': [{'subject': 'sample1', 'id': 1, 'custom_fields' : [{}]},{'subject': 'sample2', 'id': 2, 'custom_fields' : [{}]}]})
        expected_path = here( 'expected_ss.csv')
        outline.main()
        expected, actual = open(expected_path).readlines(), open(csv_path).readlines()
        nonewlines = partial(filter, lambda s: s != '\n')
        expected, actual = map(nonewlines, [expected, actual])
        result_mapping = set(map(str.strip, open(here('SampleMapping.txt')).readlines()))
        expected_mapping = set("Sample Name\tIssue ID\n_name_\t3\n_other_name_\t5\nfo-o\t8\nbar\t4".split('\n'))
        #shutil.move(here('test_ss.csv.bak'), here('test_ss.csv'))
        self.assertEquals(expected, actual)
        self.assertEquals(expected_mapping, result_mapping)
        pass

    @mock.patch('redsample.outline.create_run_issue')
    @mock.patch('redsample.outline.make_run_block')
    @mock.patch('redsample.outline.redmine.issue.all', side_effect=all_issue_hits)
    @mock.patch('redsample.outline.create_sample_issue')
    def test_execute_functional_create_all_ss_recreated(self,  mcreate, mall, mblock, _):
# Should strip?
        mcreate.side_effect = create()
        self.response.json = json_response( {'issues': [{'subject': 'sample1', 'id': 1, 'custom_fields' : [{}]},{'subject': 'sample2', 'id': 2, 'custom_fields' : [{}]}]})
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.ss_string), create = True) as m:
            actual_df, mapping_str = outline.execute(open('somedir/nonsense'), 'somedir')
            #actual_df, mapping_str = outline.execute('somedir/nonsense')
        issue_ids =  [3, 5, 8, 4]
        sampleids = ['_name_', 'foo', 'foo', 'baz']
        actual_ids, actual_names = actual_df.Sample_ID.tolist(), actual_df.Sample_Name.tolist()
        self.assertEquals(sampleids, actual_ids)
        self.assertEquals(issue_ids, actual_names)

#TODO: Maybe integration tests? Don't have a test site and don't have admin on demo.redmine
#class TestOutlineIntegration(unittest.TestCase):
#    #TODO: mock load config
#    def setUp(self):
#        self.ss_string = '''[crud]asdf\n\n[morecrud]asdf\nData\n[Data]\n
#Sample_Name,Sample_ID,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description
#_name_,_name_,,,,,,,,,
#_other_name_,foo,,,,,,,,,
#fo-o,foo,,,,,,,,,
#bar,baz,,,,,,,,,'''
#        #self.config_path = os.path.join(THISD, config.test)
#
#    def test_sample_issues_are_added(self):
#        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.ss_string), create = True) as m:
#            outline.execute(open('somedir/nonsense'), 'somedir')
#        sample_issues = outline.raw_all_samples()
#        actual_subjects = set([s.id for s in sample_issues])
#        expected_subjects = set(['_NAME_', '_OTHER_NAME_', 'FO_O', 'BAR'])
#        self.assertEquals(expected_subjects, actual_subjects)
#        e_fields = ['Pathogen', 'Study', 'PR Name']
#        for issue in sample_issues:
#           fields = [f['name'] for f in issue.custom_fields]
#           in_fields = map(fields.__contains__, e_fields)
#           map(self.assertTrue, in_fields)
#
##    def test_run_issue_was_added(self):
##        pass
#
#
#
#
#
