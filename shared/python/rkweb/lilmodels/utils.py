"""
Copyright Futurex LP
Credits Lilith Neathery
"""

def flatten_dict(d, include_nested_keys=False):
    """
    Flatten a nested dictionary into single key:value pairs
    """
    def flat_gen(d):
        if not isinstance(d, dict) and hasattr(d, 'as_dict'):
            d = d.as_dict(False)
        for (k, v) in d.items():
            try:
                v_flat = flat_gen(v)
                for (k_sub, v) in v_flat:
                    k_flat = '%s.%s' % (k, k_sub)
                    if include_nested_keys:
                        yield k, ...
                    yield (k_flat, v)
            except AttributeError:
                yield (k, v)

    return dict(flat_gen(d))
