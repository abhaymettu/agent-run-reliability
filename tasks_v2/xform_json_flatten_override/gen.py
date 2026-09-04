"""Shared generator for xform_json_flatten_override. Stays in tasks_v2/, never copied to workdir."""
import copy
import json

SEED = 20260904


def base_config():
    return {
        "service": {
            "name": "billing",
            "retries": 3,
            "hosts": ["a1.example", "a2.example", "a3.example"],
            "timeout": {"connect": 5, "read": 30},
        },
        "features": {
            "dark_mode": False,
            "beta": ["alpha_search", "alpha_export"],
        },
        "region": "us-east",
        "limits": {"max_conn": 100, "max_qps": 50},
    }


def override_01():
    # replaces a list wholesale with a SHORTER list -> naive index-merge
    # would leave a3.example dangling from the base list
    return {
        "service": {
            "hosts": ["b1.example"],
            "timeout": {"read": 45},
        }
    }


def override_02():
    # type-mismatch: base has a dict at "limits", override replaces it
    # with a plain scalar -> must fully replace, not merge into the dict
    return {
        "limits": "unlimited",
        "features": {"dark_mode": True},
    }


def override_03():
    # adds new nested keys, replaces another list wholesale (longer this
    # time), and adds a brand-new top-level key
    return {
        "service": {"retries": 5, "region_hint": "east"},
        "features": {"beta": ["alpha_search", "alpha_export", "alpha_billing"]},
        "audit": {"enabled": True, "sinks": ["stdout", "file"]},
    }


def generate(seed=SEED):
    """Return (base_dict, [override_dict, ...]) applied in list order."""
    return base_config(), [override_01(), override_02(), override_03()]


def deep_merge(base, override):
    """override wins. dict+dict merges recursively by key; anything else
    (list, scalar, or a type mismatch) is a full replacement of that path."""
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for k, v in override.items():
            if k in result:
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = copy.deepcopy(v)
        return result
    return copy.deepcopy(override)


def merge_all(base, overrides):
    result = copy.deepcopy(base)
    for ov in overrides:
        result = deep_merge(result, ov)
    return result


def flatten(obj, prefix=""):
    """Yield (path, value) for every leaf (non-dict, non-list value).

    dict keys extend the path with ".key"; list elements extend the path
    with "[i]". A leaf's rendered value is json.dumps(value, sort_keys=True)
    with no extra whitespace.
    """
    out = {}
    if isinstance(obj, dict):
        for k in sorted(obj):
            child_prefix = f"{prefix}.{k}" if prefix else k
            out.update(flatten(obj[k], child_prefix))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            child_prefix = f"{prefix}[{i}]"
            out.update(flatten(v, child_prefix))
    else:
        out[prefix] = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return out


def process(base, overrides):
    merged = merge_all(base, overrides)
    flat = flatten(merged)
    return sorted(flat.items())
