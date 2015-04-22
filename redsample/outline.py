from __future__ import print_function
from functools import partial
import config
import re
import io
import os
import sys
from collections import namedtuple
from redmine import Redmine
import pandas as pd
import operator
from redsample import DEFAULT
#TODO: How to test properly?
#TODO: Do we have to get all issue results and filter manually? Might be more trusty
# Just load all issues once and check sample against them
#TODO: How to avoid making this code wedlocked with the APIs?
config = config.load_config(DEFAULT)
redmine = Redmine(config['siteurl'], key=config['apikey'])
#make_run_block = partial(redmine.issue_relation.create, config['runid'], relation_type='blocks')
create_sample_issue = partial(redmine.issue.create, project_id=config['sampleprojectid'], tracker_id=config['sampletrackerid'])
raw_all_samples = partial( redmine.issue.all, project_id=config['sampleprojectid'], tracker_id=config['sampletrackerid'], limit=100)
Sample = namedtuple("Sample", ("name", "sample_id"))
make_run_block = partial(redmine.issue_relation.create, relation_type='blocks')
def sample_sheet_to_df(filehandle):
    '''
    :param file SampleSheet.csv
    :return list of tuples (sample_id, sample_name)
    '''
    s = filehandle.read()
    meta_info_striped = io.BytesIO(s[s.find('[Data]') + len('[Data]'):].strip())
    return pd.read_csv(meta_info_striped)

def read_sample_sheet(filehandle):
    df = sample_sheet_to_df(filehandle)
    return map(Sample, df['Sample_ID'].tolist(), df['Sample_Name'].tolist())


def all_samples(offset=0):
    #
    #Assumes 100 is the max
    samples = list(raw_all_samples(offset=offset))
    if not samples or samples  == [None]:
        return []
    return samples + all_samples(offset=(offset + 100))


def filter_one(func, iterable):
    result = filter(func, iterable)
    return None if not result else result[0]

def get_issue_pr_name(issue):
    try:
        pr_resource =  filter_one(lambda a: a['name'] == 'PR Name', issue.custom_fields.resources)
    except KeyError:
        print("Warning, issue {0} had no PR Name field.".format(issue))
        return ''
    return str(pr_resource['value']) if pr_resource else ''

def subj_match(issue, sample):
    return filter_subject(issue['subject']) == filter_subject(sample.name)

def pr_match(issue, sample):
    return filter_subject(get_issue_pr_name(issue)) == filter_subject(sample.name)

#def match(op, left, l_getter, right, r_getter):
#    return op(l_getter(left), r_getter(right))

def find_sample(sample, issues):
    '''
    Search by sample name (subject field) and PR-code.
    :param Sample sample: sample object which may or may not exist in the redmine project
    :return int issue's id, or None if not found.
    '''
    #subject = re.sub( r'[!"#$%&\'()*+,-\./:;<=>?@\[\\\]^`{|}~]', '_', origsubject)
    subj_eq, pr_eq = partial(subj_match, sample=sample), partial(pr_match, sample=sample)
    return filter_one(subj_eq, issues) or filter_one(pr_eq, issues)
#   subject_matches = [i for i in issues if i.subject == sample.name]
#   if subject_matches:
#       return subject_matches[0]
#   pr_matches = [i for i in issues if i['PR Name'] == sample.name]

def filter_subject(string):
    return re.sub(r'[-/\s]', '_', string).upper()

def get_or_create(sample, issues):
    issue = find_sample(sample, issues) or create_sample_issue(subject=sample.name)
    return issue.id

def match_pr_name(left, right):
    return filter_subject(left) == filter_subject(right)

def sync_samples(samples):
    '''
    :param list samples: list of sample objects with .name and .id
    :return dict: mapping of samplenames -> issue ids
    '''
    issues = all_samples()
    issue_ids = [get_or_create(sample, issues) for sample in samples]
    samplenames = (s.name for s in samples)
    return dict( zip(samplenames, issue_ids) )

def sample_id_map_str(sample_id_map):
    header = "Sample Name\tIssue ID"
    form = "{0}\t{1}".format
    return '\n'.join([header] + map(form, *zip(*sample_id_map.items()) ))

def make_run_issue(run_name, samples):
    #TODO: could include platform
    sample_names = '\n'.join(s.name for s in samples)
    return create_sample_issue(subject=run_name, custom_fields=
                               {"Run Name" : run_name, "SampleList" : sample_names,
                                 "Samples Synced" : "No"})

#TODO: How should the samples be named that have PR Names?
def execute(csv_file_path):
    csv_file, run_name = open(csv_file_path), os.path.split(csv_file_path)[-2]
    samples = read_sample_sheet(csv_file)
    run_issue = make_run_issue(run_name, samples)
    sample_id_map = sync_samples(samples)
    #make_this_run_block = lambda a, runid=run_issue.id: make_this_run_block(issue_id=runid, to_id=a)
    make_this_run_block = lambda a: make_run_block(issue_id=run_issue.id, to_id=a)
    map(make_run_block, sample_id_map.values())
    return sample_id_map_str(sample_id_map)

def main():
    csv_file = sys.argv[1]
    print( execute(csv_file))
    return 0


