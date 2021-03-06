.. ganetimgr documentation master file, created by
   sphinx-quickstart on Thu Oct 31 10:48:21 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*************************************
Welcome to ganetimgr's documentation!
*************************************

What is ganetimgr?
##################

ganetimgr is a Django project that serves as an administration frontend for (multiple) Ganeti clusters. It is developed as
the frontend of a VPS service. There's an introduction page for the project at https://grnet.github.io/ganetimgr/

.. image:: _static/images/ganetimgr_create_instance.png
	:scale: 50 %

A simplified architecture of ganetimgr is depicted here::

	+------------------------+           +---------------+
	|                        |           |               |
	|                        |     +-----+ ganeti cluster|
	|         Django         |     |     |               |
	|                        |     |     +---------------+
	|                        |     |            ...
	+------------------------+     |            ...
	|     gevent watcher     |     |            ...
	|                        |     |     +---------------+
	+------------------------+     |     |               |
	|  Caching  |ganeti REST +-----+     + ganeti cluster|
	|           |API client  +-----------+               |
	+-----------+------------+           +---------------+

Installation
############
You can go through the installation at the :doc:`Install ganetimgr <install>` section.

Upgrading
#########
If running an older version, look through the :doc:`Upgrade Notes <upgrade>` before upgrading to a new one.

Compatibility
#############
ganetimgr has been tested with ganeti versions 2.4-2.15. Due to the nature of the Ganeti RAPI, ganetimgr should be able to communicate with any Ganeti v.2.X cluster.

While most of the functionality is available with vanilla Ganeti setups, there are some features that require changes to Ganeti in order to work properly, see :doc:`patched software <patches>`

Development
###########
If you're interested in development/testing ganetimgr you might find useful information in the :doc:`Development documentation <devel>`.

Table of Contents
#################

.. toctree::
   :maxdepth: 2

   install
   vnc
   admin
   patches
   upgrade
   interface
   devel
