from __future__ import print_function

from functools import partial
from redsample import config

#TODO: How to test properly?
#TODO: Convert issues to samples
#TODO: Do we have to get all issue results and filter manually? Might be more trusty
# Just load all issues once and check sample against them
#TODO: How to avoid making this code wedlocked with the APIs?


redmine = Redmine(config.SITE_URL, key=API_KEY)
make_run_block = partial(config.RUN_ID, relation_type='blocks', remind.issue_relation.create)
create_sample_issue = partial(config.PROJECT_ID, tracker_id=config.TRACKER_ID, redmine.issue.create)
raw_all_samples = partial(project_id=config.PROJECT_ID, tracker_id=config.TRACKER_ID, limit=100, redmine.issue.all)

def issue_to_sample(issue):
    '''
    :param redmine.Issue issue:
    :return Sample:
    '''

def all_samples(offset=0):
    #Assumes 100 is the max
    return raw_all_samples(offset) + all_samples(offset + 100)

def validate_sample_name(name):
    if not re.match(samplename_regex, name):
        raise ValueError("Sample named {0} was not correct, please fix and re-try.".format(name))

def find_sample(sample):
    '''
    Search by sample name (subject field) and PR-code.
    :param Sample sample: sample object which may or may not exist in the redmine project
    :return int issue's id, or None if not found.
    '''
    pass

#def filter_search(string):
#    result = redmine.issue.filter
#    assert len(result) == 1
#    return result[0]

def get_or_create(sample):
    _id = find_sample(sample) or create_sample(sample)
    return _id

def sync_samples(samples):
    '''
    :param list samples: list of sample objects with .name and .id
    :return dict: mapping of samplenames -> issue ids
    '''
    _ids = map(get_or_create, samples)
    samplenames = (s.name for s in samples)
    return dict( zip(samplenames, _ids) )

def sample_id_map_str(sample_id_map):
    header = "Sample Name\tIssue ID"
    form = "{0}\t{1}".format
    return '\n'.join([header] + map(form, sample_id_map.items()) )

def main():
    samples = load_samples(csv_file)
    map(validate_sample_name, samples)
    #TODO: get all issues for searching through here?
    issues = all_samples()
    sample_id_map = sync_samples(samples)
    map(make_run_block, sample_id_map.values())
    print(sample_id_map_str(sample_id_map))
