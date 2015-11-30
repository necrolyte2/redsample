.. image:: https://travis-ci.org/necrolyte2/redsample.svg
    :target: https://travis-ci.org/necrolyte2/redsample

.. image:: https://coveralls.io/repos/necrolyte2/redsample/badge.svg?branch=master
    :target: https://coveralls.io/r/necrolyte2/redsample?branch=master

.. image:: https://badge.fury.io/py/redsample.svg
    :target: https://badge.fury.io/py/redsample

.. image:: https://readthedocs.org/projects/redsample/badge/?version=latest
    :target: https://readthedocs.org/projects/redsample/?badge=latest
    :alt: Documentation Status

RedSample
=========

Use `Redmine <http://www.redmine.org>`_ to manage sample data

Documentation is hosted on Read The Docs `here <http://redsample.readthedocs.org>`_

Suggested Workflow
==================
Tech creates samplesheet on MiSeq machine

* Tech runs script which takes a samplesheet and produces a corrected samplesheet, and creates the run issue
   * This script creates the run issue, relates samples to run, fetches and merges with existing samples.
* Tech adds watchers to the run issue
* Tech starts run using the produced samplesheet

Run finishes

* MiSeq dumps to temporary directory
Tech updates run 

* assigns to NGSYnc user
A cron job polls for runs assigned to NGSYnc user, and submits a PBS job to copy the run results from temp directory.

