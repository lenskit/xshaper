Run Recording API
=================

.. py:module:: xshaper

The API surface for integrating ``xshaper`` into a program to record
experimental runs is quite small.  A typical use, incorporating all of the
capabilities, would look like:

.. code:: python

    xshaper.configure('run-logs')
    with xshaper.Monitor():
        with xshaper.Run(tags=['my-package', 'my-stage']):
            # do your run

Recording Runs
~~~~~~~~~~~~~~

The primary interface is the :class:`Run` class, which can be used as a context
manager to wrap a body of computation comprising a single “run”:

.. code:: python

    with xshaper.Run():
        # do your computations

.. important::

    ``xshaper`` does not currently support concurrent “runs” in different threads.

.. autoclass:: Run
.. autofunction:: current_run

Configuring xshaper
~~~~~~~~~~~~~~~~~~~

There are two primary configuration points for ``xshaper``: configuring the run
record with :func:`configure`, and activating a resource monitor with
:class:`Monitor`.

.. autofunction:: configure

.. autoclass:: Monitor
