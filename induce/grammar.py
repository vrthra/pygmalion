class Grammar:
    def __init__(self, d={}): self._dict = d
    def __setitem__(self, key, item): self._dict[key] = item
    def __getitem__(self, key): return self.get(key)
    def get(self, key): return self._dict[key] if key in self._dict else set()
    def __bool__(self): return self._dict != {}
    def keys(self): return list(self._dict.keys())
    def values(self): return self._dict.values()
    def items(self): return self._dict.items()
    def __delitem__(self, key): del self._dict[key]
    def __missing__(self, key): return set()
    def get_dict(self):
        return {str(k):v for k,v in self._dict.items()}

    def __str__(self):
        def djs_to_string(djs):
            return "\n\t| ".join([i.value().replace('\n', '\n|\t')
                for i in sorted(djs)])
        def fixline(key, rules):
            fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
            return fmt % (key, djs_to_string(rules))
        return "\n".join([fixline(key, self[key]) for key in self.keys()])
