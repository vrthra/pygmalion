import json
import string
import hashlib
import pudb
brk = pudb.set_trace

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

def elts_to_str(lstrule):
    return ''.join(str(i) for i in lstrule.rvalues())

def djs_to_string(djs):
    vals = [elts_to_str(i).replace('\n', '\n|\t') for i in djs]
    return "\n\t| ".join(vals)

def fixline(key, rules):
    fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
    return fmt % (key, djs_to_string(rules))

def show_grammar(g):
    return "\n".join([fixline(key, g[key]) for key in g])

def to_str(k):
    v = ''
    if not k:
        return ':empty:'
    for i in k:
        if str(i) not in string.punctuation + string.digits + string.ascii_letters:
            v+= repr(i)[1:-1]
        else:
            v += i
    r = ''.join(sorted(v))
    r = r.replace('+-.', '-+.')
    return r

Hash = {}

def h1(w):
    global Hash
    v = hashlib.sha256(w.encode('utf-8')).hexdigest()[0:8]
    if v in Hash:
        s = Hash[v]
        assert w == s
    else:
        Hash[v] = w
    return v
