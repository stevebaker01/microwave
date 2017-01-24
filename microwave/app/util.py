def dictate(this_list, field=None):

    # standardized identifier to object dict constructor for cleanliness
    # this is gross and I don't like it anymore
    if not this_list:
        return {}
    if isinstance(this_list[0], dict):
        return {x[field if field else 'id']: x for x in this_list}
    return {getattr(x, field if field else 'id'): x for x in this_list}
