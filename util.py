


def en(s):
    if isinstance(s, unicode):
        return s.encode('utf-8', 'ignore')
    else:
        return str(s)
