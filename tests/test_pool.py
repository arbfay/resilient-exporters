import os
import json
import pytest

def test_exppool_base():
    import resilient_exporters as re

    try:
        os.remove("test_fileexporter.txt")
    except FileNotFoundError:
        pass

    lines = []

    exp = re.exporters.FileExporter("test_fileexporter.txt")
    pool = re.exporters.ExporterPool([exp])

    mydata = {"field1": "value1",
               "field2": "value2"}
    pool.send(mydata)
    lines.append(json.dumps(mydata))

    mydata = {"field1": "value1",
               "field2": "value2",
               "field3": "value3444"}
    pool.send(mydata)
    exp.stop()
    lines.append(json.dumps(mydata))

    with open("test_fileexporter.txt", "r") as file:
        assert lines == file.read().splitlines()

@pytest.mark.skipif(os.getenv('MONGO_IP', None) is None,
                    reason="No configured MongoDB URI.")
def test_exppool_threads():
    import resilient_exporters as re

    try:
        os.remove("test_fileexporter.txt")
    except FileNotFoundError:
        pass

    lines = []

    exp1 = re.exporters.MongoDBExporter(target_ip=os.environ['MONGO_IP'],
                                        username=os.environ['MONGO_USERNAME'],
                                        password=os.environ['MONGO_PWD'],
                                        default_db="test-transmitter",
                                        default_collection="dataset")
    exp2 = re.exporters.FileExporter("test_fileexporter.txt")

    pool = re.exporters.ExporterPool([exp1, exp2], num_threads=2)
    assert len(pool) == 2

    mydata = {"field1": "value1",
              "field2": "value2"}
    assert [True, True] == [res.successful for res in pool.send(mydata)]
    lines.append(json.dumps(mydata))

    mydata = {"field1": "value1",
              "field2": "value2",
              "field3": "value3444"}
    assert [True, True] == [res.successful for res in pool.send(mydata)]
    lines.append(json.dumps(mydata))
    exp2.stop()
    with open("test_fileexporter.txt", "r") as file:
        assert lines == file.read().splitlines()
