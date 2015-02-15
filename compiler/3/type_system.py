import sys

class TypeSystemError(Exception):
    pass

class NotASubtype(TypeSystemError):
    pass

class MissingMethod(TypeSystemError):
    def __str__(self):
        return 'undefined method: {0}'.format(self.args[1].name)


class Method(object):
    """ A method has a name and types for the input (parameters) and output
        (result). A type is defined as a set of methods. """
    
    def __init__(self, scope, name, in_type, out_type):
        self.name = name
        if not name.startswith('@'):
            print self.name, '[shape=plaintext]'
        self.in_type = in_type
        self.out_type = out_type
        self.scope = scope
    
    def clone(self, cache):
        cin = self.in_type.clone(self, cache)
        cout = self.out_type.clone(self, cache)
        return Method(self.scope, self.name, cin, cout)
    
    def contains(self, scope):
        while scope:
            if scope == self.scope:
                return True
            scope = scope.scope
        return False


class Type(object):
    """ Every expression has a type. That type is represented by an instance of
        Type. """
    
    _current_id = 0
    
    @staticmethod
    def next_id():
        Type._current_id += 1
        return Type._current_id
    
    def __repr__(self):
        return '{}'.format(self.id)
    
    @property
    def method_names(self):
        return frozenset(m.name for m in self.methods)
    
    def extends(self, other, cache):
        """ The extends relation (A extends B) states that an instance of A may
            be used wherever an instance of B is expected. That is, that A is a
            subtype of B. This is true iff every method on B has a counterpart
            on A. """
        print other, "->", self
        if self.structurally_equal(other, {}):
            return True
        try:
            if not cache[self, other]:
                raise NotASubtype(self, other)
        except KeyError:
            cache[self, other] = False
            other.extended_by(self)
            for m in other.methods:
                self.has_method(m, cache)
            cache[self, other] = True
    
    def structurally_equal(self, other, cmap):
        return False


class Concrete(Type):
    """ The type of literal object expressions. """
    
    def __init__(self, methods):
        self.id = self.next_id()
        print self, '[shape=box]'
        self.methods = methods
        for m in self.methods:
            if m.name.startswith('@'):
                continue
            print self, "->", m.name, '[arrowhead=inv]'
    
    def extended_by(self, other):
        pass
    
    def has_method(self, method, cache):
        name, in_type, out_type = method.name, method.in_type, method.out_type
        for m in self.methods:
            if m.name == name:
                c = {}
                n = m.clone(c)
                in_type.extends(n.in_type, cache)
                n.out_type.extends(out_type, cache)
                return
        raise MissingMethod(self, method)
    
    def clone(self, scope, cache):
        return self
        try:
            return cache[self]
        except KeyError:
            res = Concrete([])
            cache[self] = res
            res.methods = [m.clone(cache) for m in self.methods]
            return res
    
    def structurally_equal(self, other, cmap):
        if not isinstance(other, Concrete):
            return False
        rother = cmap.get(self)
        rself = cmap.get(other)
        if rself == self or rother == other:
            return True
        if rself or rother:
            return False
        cmap[self] = other
        if self.method_names != other.method_names:
            return False
        for m in self.methods:
            ns = [n for n in other.methods if m.name == n.name]
            if not ns:
                return False
            if m.name.startswith('@'):
                return True
            n = ns[0]
            if not m.in_type.structurally_equal(n.in_type, cmap):
                return False
            if not m.out_type.structurally_equal(n.out_type, cmap):
                return False
        return True


class Abstract(Type):
    """ The type of unknown types. """
    
    def __init__(self, scope):
        self.id = self.next_id()
        print self
        self.scope = scope
        self.methods = []
        self.subtypes = []
    
    def extended_by(self, other):
        self.subtypes.append(other)
    
    def has_method(self, method, cache):
        print self, '->', method.name, '[arrowhead=inv]'
        self.methods.append(method)
        for t in self.subtypes:
            t.has_method(method, cache)
    
    def clone(self, scope, cache):
        #return self
        if not scope.contains(self.scope):
            return self
        try:
            return cache[self]
        except KeyError:
            res = Abstract(self.scope)
            cache[self] = res
            res.methods = self.methods
            print >> sys.stderr, self, self.subtypes, self.methods
            res.subtypes = [st.clone(scope, cache) for st in self.subtypes]
            for st in res.subtypes:
                print res, '->', st
            print self, '->', res, '[arrowhead=dot]'
            return res


class GlobalScope(object):
    scope = None
    name = "globals"
    
    def contains(self, scope):
        return True

global_scope = GlobalScope()


class TypeEnvironment(object):
    def __init__(self, defs, parent=None):
        self._defs = defs
        self.parent = parent
    
    def __getitem__(self, name):
        try: 
            return self._defs[name]
        except KeyError:
            if self.parent is None:
                raise
            return self.parent[name]
    
    def bind(self, defs):
        return TypeEnvironment(defs, self)

