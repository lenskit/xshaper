Data Model
==========

.. py:module:: xshaper.model

This page describes the XShaper data model.  These classes are all Pydantic_
models, and are used directly to serialize and deserialize ``xshaper`` data.

.. _Pydantic: https://docs.pydantic.dev

Runs
~~~~

.. autoclass:: RunRecord
.. autoclass:: TimeRecord

Machines
~~~~~~~~

.. autoclass:: MachineRecord

Resources
~~~~~~~~~

.. autoclass:: CPURecord
.. autoclass:: MemoryRecord
.. autoclass:: PowerRecord
