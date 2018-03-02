class ReplList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def __repr__(self):
        return ', '.join(map(repr, self))


class Repl(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)

        def fill(**kwargs):
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = Repl(v)
                elif isinstance(v, list):
                    self[k] = ReplList(v)
                else:
                    self[k] = v
        if args and isinstance(args[0], dict):
            fill(**args[0])
        fill(**kwargs)

    def __resolvekey__(self, key):
        m = self
        while '.' in key:
            index = key.index('.')
            k_parent = key[:index]
            if k_parent not in m:
                m[k_parent] = Repl()
            m = m[k_parent]
            key = key[index + 1:]
        return m, key

    def __setitem__(self, name, value):
        m, name = self.__resolvekey__(name)
        dict.__setitem__(m, name, value)

    def __getattr__(self, name):
        if name in self:
            v = self[name]
            if isinstance(v, dict):
                return v
            elif isinstance(v, list):
                return repr(v)
            else:
                return str(v)
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            self[name] = value
