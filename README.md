# Resilient Exporters
![PyPI](https://img.shields.io/pypi/v/resilient-exporters?logo=pypi&logoColor=white&style=for-the-badge)
![GitHub Build Status](https://img.shields.io/github/workflow/status/arbfay/resilient-exporters/Python%20package?logo=github&style=for-the-badge)
![License](https://img.shields.io/github/license/arbfay/resilient-exporters?style=for-the-badge)
![Python Version](https://img.shields.io/badge/3.6+%20-%2314354C.svg?label=PYTHON&style=for-the-badge&logo=python&logoColor=white)

Resilient-exporters abstracts away common tasks when sending or saving data from an application. It has been designed to send data to different targets and manage common issues for applications running on edge devices such as a Raspberry Pi or Nvidia Jetson Nano:
- Internet connection interruptions;
- Highly variable frequency of data transfers;

If a connection is lost, it automatically saves the data and retries later when the connection is recovered and when a new request to send data is made. To avoid consuming too much memory or disk space, it has a specific configurable flush.

If an application wants to send more data than is momentally manageable, it multiplies the transmission jobs (using multithreading, if available) and saves the data (queuing), to avoid back-pressure and reducing the application's speed.

Of course, it can break if:
- the data to transmit is _almost always_ more important than the available bandwidth;
- the interruptions are too long compared to the available memory or disk space;

We have designed it particularly for a Raspberry Pi 3B+ device running a Linux distribution.

## Installation
To use the package:
```
pip install resilient-exporters
```

With all the additional packages needed for the different exporters:
```
pip install resilient-exporters[all]
```

### Dev installation
If you'd like to have a editable, up-to-date version of the files, do:
```
git clone https://github.com/arbfay/resilient-exporters.git && \
pip install -e resilient-exporters/ && \
pip install -r resilient-exporters/dev_requirements.txt
```

## Usage
Currently supported:
- Text file
- MongoDB
- ElasticSearch
- PostgreSQL

Some features for some exporters might be missing. Raise an issue on Github to ask for an implementation and help improve the package.

### Store in a file
```python
from resilient_exporters import FileExporter

exporter = FileExporter(target_file="mydata.txt",
                        max_lines=100)

mydata = "line of text"
exporter.send(mydata)
```

### To MongoDB
```python
from resilient_exporters import MongoDBExporter

exporter = MongoDBExporter(target_ip="127.0.0.1",
                           target_port=27017,
                           username="username",
                           password="password",
                           default_db="my_db",
                           default_collection="my_collection")

mydata = {"field1": "value1"}
exporter.send(mydata)
```

### To ElasticSearch
```python
from resilient_exporters import ElasticSearchExporter

exporter = ElasticSearchExporter(target_ip="127.0.0.1",
                                 default_index="my_index",
                                 use_ssl=True,
                                 ssl_certfile="/path/to/file",
                                 sniff_on_start=True)

mydata = {"field1": "value1"}
exporter.send(mydata)
```

### To PostgreSQL
```python
from resilient_exporters.exporters import PostgreSQLExporter

exporter = PostgreSQLExporter(target_host="myserver.domain.net",
                              username="username",
                              password="my-password",
                              database="profiles",
                              default_table="scientists")

data = {"name": "Richard Feynman",
        "age": 69}
exporter.send(data)
```

### Multiple distant targets - Pools
Edge devices are more and more powerful, and are capable of managing multiple distant targets without much overhead thanks to `resilient-exporters`. If you're taking advantage of this, you might need sometimes to replicate data across different databases of the same type (e.g. NoSQL, document-based databases). However, if you use multiple exporters, all the features will be duplicated and can generate inefficiencies (multiple temporary files, multiple queues, etc.).

Instead, use `resilient_exporters.ExporterPool` which pools exporters _and_ other pools to expose only one `send` method for all the exporters and to ensure a more efficient management of the resources. To use it:
```python
from resilient_exporters import ExporterPool
from resilient_exporters import MongoDBExporter, ElasticSearchExporter

exporters = [
  MongoDBExporter(target_ip="127.0.1.10",
                  target_port=1234,
                  default_db="my_db",
                  default_collection="my_collection"),
  ElasticSearchExporter(cloud_id="cloud id",
                        api_key="api key",
                        default_index="my_index")]

pool = ExporterPool(exporters, use_memory=False)

mydata = {"metric": 2}
pool.send(mydata)
```

## Transform data before sending
To transform data before it gets sent by an exporter or a pool, one can add a function that takes the input data and returns the transformed data:
```python
from resilient_exporters import MongoDBExporter

def transform(data):
  data["metric"] = (data["metric"] / 2) * .5
  return data

exporter = MongoDBExporter(target_ip="127.0.1.10",
                           target_port=1234,
                           default_db="my_db",
                           default_collection="my_collection",
                           transform=transform)

mydata = {"metric": 2}
exporter.send(mydata)
```
>**NOTE**: it can also be passed to a pool with the same key argument `tranform` at initialisation. When doing so, transform functions of individual exporters will be superseded by the pool's transform function.

## Additional information
The `resilient_exporters.Exporter` is at the core of the package. All the other exporters inherits from it.

`Exporter` manages the export of data to a target, however each target need specific logic to send data. All these subclasses, such as `FileExporter` or `MongoDBExporter`, implements the `Exporter.send` method and manages the needed options. Some exporters might need additional packages to be usable:
- `pymongo` for `MongoDBExporter`
- `elasticsearch` for `ElasticSearchExporter`
- `psycopg2` for `PostgreSQLExporter`

## Documentation
More documentation available [here.](https://resilient-exporters.readthedocs.io)

## Suggestions and contribution
Please open a GitHub issue for bugs or feature requests.
Contact the contributors for participating.
