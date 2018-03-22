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

def djs_to_string(djs):
    vals = [str(i).replace('\n', '\n|\t') for i in djs]
    return "\n\t| ".join(vals)

def fixline(key, rules):
    fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
    return fmt % (key, djs_to_string(rules))

def show_grammar(g):
    return "\n".join([fixline(key, g[key]) for key in g])
