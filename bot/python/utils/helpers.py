
def get_int(value):
    '''
    Returns an int if value can be an int
    '''
    try:
        int_val = int(str(value))
        return int_val
    except (ValueError, TypeError) as e:
        return None
