from __future__ import print_function
import time
from miseqpipeline import miseq_sync
from functools import partial
import os
import sys
'''
 Get run name from issue
 import and run miseq_sync
 skip resample step
 skip rename step
 update run issue
 '''
def compose(outer, inner):
    def newfunc(*args, **kwargs):
        return outer(inner(*args, **kwargs))
    return newfunc

#update_status = partial(update_custom_field, cf_id=cfg['runprojectstatus'])

def save_value(obj, attr, value):
    setattr(obj, attr, value)
    obj.save()

def get_custom_field(issue, fname):
     return [d['value'] for d in issue.custom_fields if d['name'] == fname][0]

update_percent_done = partial(save_value, attr='done_ratio')
update_cf = partial(save_value, attr='value')

is_new_run = lambda r: r.done_ratio < 100
find_new_run = partial(filter, is_new_run)
get_my_runs = partial(redmine.issue.filter, project_id=cfg['runprojectid'], tracker_id=cfg['runtrackerid'], assigned_to_id='me')
get_my_new_runs = compose(find_new_run, get_my_runs)
get_run_name = partial(get_custom_field, fname='Run Name')

NGS_PATH = '/home/EIDRUdata/NGSData'

MAKE_RUN_PATH = partial(os.path.join, '/Instruments/MiSeq')
_sync = partial(miseq_sync.sync, ngsdata=NGS_PATH)
copy_samples = compose(_sync, MAKE_RUN_PATH)
copy_runs_samples = compose(copy_samples, get_run_name)

#def copy_samples(runname):
#    runpath = MAKE_RUN_PATH(runname)
#    miseq_sync.sync(runpath, NGS_PATH)
#


def update_custom_field(issue, cf_id, new_value):
    cf = issue.custom_fields.get(cf_id) #internal id
    update_cf(cf, new_value)

def poll():
    #TODO: use a custom field techs won't use instead of progress bar.
    new_runs = get_my_new_runs()
    if not new_runs:
        print("runs not found at time: {0}".format(time.ctime()))
        sys.exit(0)
    else:
        print("New runs found at time: {0},  {1}".format(time.ctime(), new_runs))
        return new_runs

def start():
    runs = poll()
    # could assert no duplicate run names
    assert len(runs) == 1, "More than one new run found, something went wrong."
    mark_as_started = partial(update_percent_done, value=50)
    map(mark_as_started, runs)
    #pool.map
    map(copy_runs_samples, runs)
    mark_as_finished = partial(update_percent_done, value=100)
    map(mark_as_finished, runs)

