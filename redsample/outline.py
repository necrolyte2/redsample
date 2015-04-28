from __future__ import print_function
from functools import partial
from . import config
import re
import io
import os
import sys
from collections import namedtuple
from redmine import Redmine
import pandas as pd
from redmine import exceptions
import shutil

#TODO: Currently we just load all issues once and check sample against them, should provide another option?
config = config.load_default()
if not config['apikey'] or config['apikey'] in ['fromyouraccount', 'default']:
    redmine = Redmine(config['siteurl'], username=config['username'], password=config['password'])
else:
    redmine = Redmine(config['siteurl'], key=config['apikey'])

#make_run_block = partial(redmine.issue_relation.create, config['runid'], relation_type='blocks')
create_sample_issue = partial(redmine.issue.create, project_id=config['sampleprojectid'], tracker_id=config['sampletrackerid'])
create_run_issue = partial(redmine.issue.create, project_id=config['runprojectid'], tracker_id=config['runtrackerid'])
raw_all_samples = partial( redmine.issue.all, project_id=config['sampleprojectid'], tracker_id=config['sampletrackerid'], limit=100)
make_run_block = partial(redmine.issue_relation.create, relation_type='blocks')
Sample = namedtuple("Sample", ("name", "ignore"))
raw_all_samples = partial( redmine.issue.all, project_id=18, tracker_id=6, limit=100)

def sample_sheet_to_df(filehandle):
    '''
    :param file SampleSheet.csv
    :return list of tuples (sample_id, sample_name)
    '''
    s = filehandle.read()
    meta_info_striped = io.BytesIO(s[s.find('[Data]') + len('[Data]'):].strip())
    filehandle.close()
    return pd.read_csv(meta_info_striped)

#TODO: add searching or log these
def all_samples(offset=0):
    '''
    Return a list of all issues within the defined 'sampleproject'
    '''
    samples = list(raw_all_samples(offset=offset))
    print("Fetched {0} more samples".format(len(samples)))
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
    except exceptions.ResourceAttrError:
        print("Warning, issue {0} had no Custom fields.".format(issue))
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
    ''' replace hyphen, slash, and space with underscores.'''
    return re.sub(r'[-/\s]', '_', string).upper()

def get_or_create(sample, issues):
    ''' Look via find_sample, if not found,
    creates the sample issue with the filtered subject name (see filter_subject) '''
    issue = find_sample(sample, issues) or create_sample_issue(subject=filter_subject(sample.name))
    return issue.id

def sync_samples(samples):
    '''
    Finds/creates issues for all samples as appropriate.
    :param list samples: list of sample objects with .name and .id
    :return dict: mapping of samplenames -> issue ids
    '''
    print("Fetching samples, this may take up to five minutes.")
    issues = all_samples()
    issue_ids = [get_or_create(sample, issues) for sample in samples]
    samplenames = (s.name for s in samples)
    return dict( zip(samplenames, issue_ids) )

def sample_id_map_str(sample_id_map):
    '''
    Return a tab-separated string of the sample names associated with their issue ids.
    '''
    header = "Sample Name\tIssue ID"
    form = "{0}\t{1}".format
    return '\n'.join([header] + map(form, *zip(*sample_id_map.items()) ))

def make_run_issue(run_name):
    '''
    :Param str run_name: the folder the run outputs into.
    Make an issue with the run name filled in and all other fields set to default.
    '''
    #TODO: Test this
    return create_run_issue(subject=run_name, custom_fields=
                            [dict(id=config['runnameid'], value=run_name)])
                            #, "Samples Synced" : "No"})

#TODO: How should the samples be named that have PR Names?
def execute(csv_file, run_name):
    '''
    Load the sample sheet, create the run issue, and "sync" the samples
    by find/creating issues for them. Then, makes the new run issue "block"
    each sample. Finaly, alters the loaded samplesheet.
    :param file csv_file  the samplesheet ouptut by miseq prep
    :param run_name The ouptut folder miseq will output to
    '''
    df = sample_sheet_to_df(csv_file)
    samples = map(Sample, df.Sample_Name, df.Sample_ID)
    run_issue = make_run_issue(run_name)
    sample_id_map = sync_samples(samples)
    make_this_run_block = lambda a: make_run_block(issue_id=run_issue.id, to_id=a)
    map(make_this_run_block, sample_id_map.values())
    df.Sample_Name = df.Sample_Name.apply(sample_id_map.__getitem__)
    return df, sample_id_map_str(sample_id_map)

def main():
    '''
    load csv file, create a new run, sync the samples.
    Backs up the csv_file to csv_name.csv.bak; then replaces the old
    csv file with a new one--with issue ids in place of the sample names.
    finally, writes the samplename-issueid mapping
    into the same directory under 'SampleMapping.txt'
    '''
    csv_file_path = sys.argv[1]
    csv_file, run_name = open(csv_file_path), os.path.split(csv_file_path)[-2]
    #Save a backup of the samplesheet
    shutil.copyfile(csv_file_path, '.'.join([csv_file_path, 'bak'] ))
    df, mapping_str =  execute(csv_file, run_name)
    print(mapping_str)
    #Have to set index in order for output to look right
    csv =  df.set_index('Sample_Name').to_csv()
    s = open(csv_file_path).read()
    metadata = s[:s.find('[Data]')+len('[Data]')]
    new_sample_sheet = '\n'.join([metadata, csv])
    sample_mapping_path = os.path.join(run_name, 'SampleMapping.txt')
    with open(csv_file_path, 'w') as ss:
        ss.write(new_sample_sheet)
    with  open(sample_mapping_path, 'w') as smp:
        smp.write(mapping_str)
