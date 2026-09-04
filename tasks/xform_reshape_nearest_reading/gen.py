"""Shared generator for xform_reshape_nearest_reading. Stays in tasks_v2/, never copied to workdir."""

SEED = 20260904


def generate(seed=SEED):
    """Return (readings, targets).

    readings: list of dicts {sensor_id, field, timestamp, value}, in
    scrambled (non-chronological) file order.
    targets: list of dicts {sensor_id, field, target_timestamp}, in the
    order rows must be emitted.

    Deliberately plants:
      - a target whose truly-nearest reading has a timestamp AFTER the
        target_timestamp (defeats a "latest reading at or before target"
        heuristic, a very natural but wrong approach)
      - a target with an exact tie between two equidistant readings,
        broken by choosing the smaller (earlier) timestamp
      - a target_timestamp that exactly matches an existing reading's
        timestamp (distance 0)
      - multiple (sensor_id, field) pairs so a naive scan can pick a
        reading from the wrong field or wrong sensor by mistake
    """
    readings = [
        # sensor s1, field temp: readings scattered out of order
        {"sensor_id": "s1", "field": "temp", "timestamp": 1000, "value": 21.0},
        {"sensor_id": "s1", "field": "temp", "timestamp": 1300, "value": 23.5},
        {"sensor_id": "s1", "field": "temp", "timestamp": 1100, "value": 21.8},
        {"sensor_id": "s1", "field": "temp", "timestamp": 900, "value": 20.1},
        # target for s1/temp = 1150 -> nearest is 1100 (dist 50) vs 1300 (dist 150)
        # but also test "after target" case separately below

        # sensor s1, field humidity
        {"sensor_id": "s1", "field": "humidity", "timestamp": 500, "value": 40.0},
        {"sensor_id": "s1", "field": "humidity", "timestamp": 800, "value": 44.0},
        # target for s1/humidity = 550 -> nearest reading is AFTER target
        # (800, dist 250) is farther than (500, dist 50); real nearest is 500.
        # We'll instead plant target so the nearest-after case is unambiguous below.

        # sensor s2, field temp: exact tie case
        {"sensor_id": "s2", "field": "temp", "timestamp": 2000, "value": 18.0},
        {"sensor_id": "s2", "field": "temp", "timestamp": 2100, "value": 19.0},
        {"sensor_id": "s2", "field": "temp", "timestamp": 2200, "value": 20.0},
        # target 2100 exact match on the middle reading (distance 0 case) is
        # handled by s2/temp target = 2100 below; tie case handled by s2/pressure

        # sensor s2, field pressure: two readings equidistant from target
        {"sensor_id": "s2", "field": "pressure", "timestamp": 3000, "value": 101.0},
        {"sensor_id": "s2", "field": "pressure", "timestamp": 3200, "value": 103.0},
        # target 3100 -> both are distance 100; tie broken by smaller timestamp (3000)

        # sensor s3, field temp: nearest reading is strictly AFTER the target
        {"sensor_id": "s3", "field": "temp", "timestamp": 5000, "value": 30.0},
        {"sensor_id": "s3", "field": "temp", "timestamp": 5500, "value": 31.0},
        # target 4950 -> nearest is 5000 (dist 50), which is AFTER target;
        # a "last reading at or before target" heuristic finds nothing at
        # all before 4950 for this sensor and must not fall back wrongly

        # sensor s3, field temp, more spread, out of order in file
        {"sensor_id": "s3", "field": "temp", "timestamp": 4000, "value": 28.0},
    ]

    targets = [
        {"sensor_id": "s1", "field": "temp", "target_timestamp": 1150},
        {"sensor_id": "s1", "field": "humidity", "target_timestamp": 550},
        {"sensor_id": "s2", "field": "temp", "target_timestamp": 2100},
        {"sensor_id": "s2", "field": "pressure", "target_timestamp": 3100},
        {"sensor_id": "s3", "field": "temp", "target_timestamp": 4950},
    ]

    return readings, targets


def process(readings, targets):
    """Return a list of (sensor_id, field, timestamp, value) in target order."""
    out = []
    for t in targets:
        sid, field, tgt = t["sensor_id"], t["field"], t["target_timestamp"]
        candidates = [
            r for r in readings if r["sensor_id"] == sid and r["field"] == field
        ]
        if not candidates:
            raise ValueError(f"no readings for {sid}/{field}")
        best = min(candidates, key=lambda r: (abs(r["timestamp"] - tgt), r["timestamp"]))
        out.append((sid, field, best["timestamp"], best["value"]))
    return out
