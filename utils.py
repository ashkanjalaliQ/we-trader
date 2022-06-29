def sum_two_dicts(d1, d2):
    d1 = d1.copy()
    d2 = d2.copy()
    for key in d2:
        d1[key] = d2[key]
    return d1