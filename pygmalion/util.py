import json

def lossy_obj_rep(val):
    if isinstance(val, list):
        return [lossy_obj_rep(i) for i in val]
    elif isinstance(val, set):
        return {lossy_obj_rep(i) for i in val}
    elif isinstance(val, dict):
        return {str(i):lossy_obj_rep(val[i]) for i in val}
    elif hasattr(val, '__dict__'):
        return ('#' + val.__class__.__name__, lossy_obj_rep(val.__dict__))
    else:
        try:
            s = json.dumps(val)
            return val
        except:
            try:
                return '<not serializable #%s %s>' % (val.__class__.__name__, hash(val))
            except:
                return '<not serializable #%s %s>' % (val.__class__.__name__, str(val))


