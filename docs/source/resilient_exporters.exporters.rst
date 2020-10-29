.. role:: hidden
    :class: hidden-section

resilient_exporters.exporters
===================================

.. currentmodule:: resilient_exporters.exporters

These are the exporters and their interfaces.

.. contents:: Exporters
    :depth: 2
    :local:
    :backlinks: top


.. currentmodule:: resilient_exporters.exporters


Implemented exporters
---------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :template: classtemplate.rst

    FileExporter
    ElasticSearchExporter
    MongoDBExporter
    ExporterPool

Implement your own exporter
---------------------------
To implement your own exporter, you just have to implement a class that inherits
``resilient_exporters.exporters.Exporter`` and that implements its function
``send``. More detail about the ``Exporter`` class below:

..
  .. autosummary::
      :toctree: generated
      :nosignatures:
      :template: classtemplate.rst

      Exporter

.. autoclass:: Exporter
    :members:
    :undoc-members:
