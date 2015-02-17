============
Installation
============

Installation is quite simple at this point

Setup Redmine Configuration
===========================

#. Copy redsample.config.example to ~/.redsample.config
    You will edit this as we go filling in the variables with values from your
    redmine installation.
#. Create a new project in Redmine that will host your sample issues
    Remember the Identifier you choose for later
    For this tutorial, we will assume the Identifier you pick is samples
#. Create a new tracker in Redmine to assign to all of your samples
    Make sure to assign it to the project you created above
#. You will then need to get the tracker's id you created manually by
    selecting it from the Trackers menu and looking at the url
    The id is the number in the url that should look like the following::

        https://yourredmine.com/trackers/1/edit
    
    Here the number 1 is the tracker id you will need for later
#. Head over to the My account link inside of Redmine and get your API access key
#. Edit your ~/.redsample.config and replace the variables with your information

Install Project
===============

.. code-block:: bash

    git clone https://github.com/necrolyte2/redsample
    cd redsample
    python setup.py install
