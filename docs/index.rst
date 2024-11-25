eXperiment Shaperate
====================

The eXperiment Shaperate (xshaper) is a tool for measuring and recording
experiment runs and their resource consumption.  It provides a Python API for
tracking runs with their resource use and saving these records into a logging
directory.

It also provides command-line tools to process these records into long-term,
queryable form for storing with a project's data (e.g. in DVC-tracked files),
and APIs for accessing this storage.

It natively measures basic resource usage (e.g. CPU and memory), and has
extensible support for reporting power from a range of sources using adapters
with a simple ZeroMQ-based protocol.

Documentation Sections
----------------------

.. toctree::
    :maxdepth: 2

    recording
    model
