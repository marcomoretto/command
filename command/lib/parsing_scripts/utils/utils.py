def get_dict_key_from_value(dictionary, val):
    for k, v in dictionary.items():
        if v == val:
            return k
