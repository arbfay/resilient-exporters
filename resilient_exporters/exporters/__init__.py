from collections import namedtuple

ExportResult = namedtuple("ExportResult", ["returned", "successful"])

from .exporter import Exporter
from .exporter_pool import ExporterPool
from .exporter_file import FileExporter
from .exporter_mongodb import MongoDBExporter
from .exporter_elasticsearch import ElasticSearchExporter
from .exporter_postgresql import PostgreSQLExporter

__all__ = ["ExportResult", "Exporter", "ExporterPool", "FileExporter",
           "MongoDBExporter", "ElasticSearchExporter", "PostgreSQLExporter"]
