from load_firms_to_db import build_rows, insert_detections

CLEANED = {
    "latitude": "45.83", "longitude": "-78.37", "timestamp": "2023-06-04T17:45:00Z",
    "confidence": "82", "confidence_class": "high", "instrument": "MODIS",
    "satellite": "Terra", "frp": "", "daynight": "D", "type": "0",
}


def test_build_rows_converts_types_and_keeps_missing_as_none():
    (row,) = build_rows([CLEANED])
    assert row[:5] == (45.83, -78.37, "2023-06-04T17:45:00Z", 82.0, "high")
    assert row[7] is None   # frp missing -> NULL, not 0
    assert row[9] == 0      # fire_type


class FakeCursor:
    def __init__(self):
        self.batches = []
        self.rowcount = 0

    def executemany(self, sql, batch):
        self.batches.append(batch)
        self.rowcount = len(batch)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self):
        self.cur = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.cur

    def commit(self):
        self.committed = True


def test_insert_detections_batches_and_commits():
    conn = FakeConnection()
    rows = build_rows([CLEANED] * 5)
    inserted = insert_detections(conn, rows, batch_size=2)
    assert [len(b) for b in conn.cur.batches] == [2, 2, 1]
    assert inserted == 5
    assert conn.committed
