from __future__ import print_function
import time
from miseqpipeline import miseq_sync
from functools import partial
import os
import sys
from outline import get_run_name, get_my_new_runs, update_percent_done, config, compose
from past.builtins import map

'''
 Get run name from issue
 import and run miseq_sync
 skip resample step
 skip rename step
 update run issue
 '''

MAKE_RUN_PATH = partial(os.path.join, config['runbasepath'])
_sync = partial(miseq_sync.sync, ngsdata=config['destinationpath'])
copy_samples = compose(_sync, MAKE_RUN_PATH)
copy_runs_samples = compose(copy_samples, get_run_name)

def poll():
    ''' Look for new run_issues assigned to "me" as defined in config file.'''
    #TODO: use a custom field techs won't use instead of progress bar.
    new_runs = get_my_new_runs()
    if not new_runs:
        print("run issues not found at time: {0}".format(time.ctime()))
        sys.exit(0)
    else:
        print("New run issues found at time: {0},  {1}".format(time.ctime(), new_runs))
        return new_runs

def start():
    ''' Poll for assigned issues, and miseq_sync them  if found.'''
    run_issues = poll()
    assert len(run_issues) == 1, "More than one new run found, something went wrong."
    mark_as_started = partial(update_percent_done, value=50)
    map(mark_as_started, run_issues)
    #pool.map
    map(copy_runs_samples, run_issues)
    mark_as_finished = partial(update_percent_done, value=100)
    map(mark_as_finished, run_issues)
    return run_issues

def main():
    start()
