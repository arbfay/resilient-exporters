

def test_datastore_memory():
    from resilient_exporters.utils import _DataStore

    ds = _DataStore(use_memory=True)
    assert ds.size == 0

    ds.put([1, 2, 3])
    assert ds.size == 1

    assert [1, 2, 3] == ds.get()
    assert ds.size == 0
