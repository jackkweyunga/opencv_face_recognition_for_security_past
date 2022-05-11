

def maxk(dict_v):
    max_v = max(dict_v.values())
    for key in dict_v.keys():
        if dict_v.get(key) == max_v:
            return key