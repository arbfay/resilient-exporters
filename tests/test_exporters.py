import os
import json
import pytest

class TestFileExporter:
    def test_fileexp_dictdata(self):
        import resilient_exporters as re

        try:
            os.remove("test_fileexporter.txt")
        except FileNotFoundError:
            pass

        lines = []

        exp = re.exporters.FileExporter(
            "test_fileexporter.txt"
        )

        mydata = {"field1": "value1",
                   "field2": "value2"}
        exp.send(mydata)
        lines.append(json.dumps(mydata))

        mydata = {"field1": "value1",
                   "field2": "value2",
                   "field3": "value3444"}
        exp.send(mydata)
        lines.append(json.dumps(mydata))

        exp.stop()
        with open("test_fileexporter.txt", "r") as file:
            assert lines == file.read().splitlines()

    def test_fileexp_stringdata(self):
        import resilient_exporters as re

        try:
            os.remove("test_fileexporter.txt")
        except FileNotFoundError:
            pass

        lines = []
        exp = re.exporters.FileExporter(
            "test_fileexporter.txt"
        )

        mydata = "This is a line of text"
        exp.send(mydata)
        lines.append(mydata)

        mydata = "Yet another line"
        exp.send(mydata)
        lines.append(mydata)

        exp.stop()
        with open("test_fileexporter.txt", "r") as file:
            assert lines == file.read().splitlines()

    def test_fileexp_maxlines(self):
        import resilient_exporters as re

        try:
            os.remove("test_fileexporter.txt")
        except FileNotFoundError:
            pass

        lines = []
        exp = re.exporters.FileExporter(
            "test_fileexporter.txt",
            max_lines=100
        )

        for i in range(101):
            mydata = "This is a line of text"
            res = exp.send(mydata)
            if res.successful:
                lines.append(mydata)

        exp.stop()
        with open("test_fileexporter.txt", "r") as file:
            assert lines == file.read().splitlines()

@pytest.mark.skipif(os.getenv('MONGO_IP', None) is None,
                    reason="No configured MongoDB URI.")
def test_mongoexp_dictdata():
    import resilient_exporters as re

    exp = re.exporters.MongoDBExporter(target_ip=os.environ['MONGO_IP'],
                                       target_port=27017,
                                       username=os.environ['MONGO_USERNAME'],
                                       password=os.environ['MONGO_PWD'])

    mydata = {"field1": "value11",
               "field2": "value22"}
    assert True == exp.send(mydata, db="test-transmitter", collection="dataset").successful

@pytest.mark.skipif(os.getenv('SQL_SERVER_ADD', None) is None,
                    reason="No configured SQL Server address.")
def test_sqlserverexp_dictdata():
    from resilient_exporters.exporters import SQLServerExporter

    exp = SQLServerExporter(target_host=os.environ['SQL_SERVER_ADD'],
                            target_port=1433,
                            username=os.environ['SQL_SERVER_USERNAME'],
                            password=os.environ['SQL_SERVER_PWD'],
                            database=os.getenv('SQL_SERVER_DB', None),
                            create_table_if_inexistent=True)

    mydata = {"field1": "value11",
              "field2": 0.1}

    assert True == exp.send(mydata, table="test").successful
