"""

A type checker for an object-oriented language. This type checker does not
require type annotations in order to function.

The type checker works by making assertions about types when analysing
expressions. These assertions form a set of constraints about a program. 
Determining whether a program is well-typed requires that the constraints be 
solved.

Types are defined to be sets of methods. A type T extends another type U if T 
has all the methods on U and they are compatible. A method Ti -> To is 
compatible with Ui -> Uo if Ui extends Ti and To extends Uo.

The type checker uses type variables to represent the constraints as they 
accumulate. The precise type represented by a type variable is not significant,
only whether the constraints it represents are consistent with one another.

A type variable maintains two sets of types that it is linked to: the types that
it extends, and the types that extend it. A graph of subtype/supertype
relationships is thus maintained by the type checker. When a concrete type is
introduced into this graph, a consistency check is performed, whereby all of the
reachable concrete subtypes must extend all of the reachable concrete 
supertypes.

Generic types are represented by copying type variables. A type variable has a
scope associated with it (the scope in which the variable was introduced). When
a method is checked for compatibility its input and output types are copied. A
variable is only copied if it is within the scope of that method being checked
for compatibility.

"""

import string
from copy import copy

class RequirementsError(Exception):
    pass


class TypePrinter(object):
    def __init__(self):
        self.seen = {}
        self.cur = 1
        self.defns = {}
        self.recursive = False
    
    def type_string(self, t):
        self.type_var_string(t)
        return self.render_type_string(t)
    
    def type_var_string(self, t):
        t = t
        pt = self.get_primitive_name(t)
        if pt:
            return pt
        try:
            res = self.seen[t]
            if res == 'A':
                self.recursive = True
            return res
        except KeyError:
            res = self.new_type_var()
            self.seen[t] = res
            self.defns[res] = self.build_type_string(t)
            return res
    
    def get_primitive_name(self, t):
        for m in t.methods:
            if m.name.startswith('@'):
                return m.name[1:]
    
    def new_type_var(self):
        cur = self.cur
        res = ""
        while cur != 0:
            res = string.ascii_uppercase[(cur-1) % 26] + res
            cur = cur // 26
        self.cur += 1
        return res
    
    def build_type_string(self, t):
        methods = ", ".join("{0}: {1} -> {2}".format(m.name,
                                                     self.type_var_string(m.in_type),
                                                     self.type_var_string(m.out_type))
                            for m in t.methods)
        return "{{{0}}}".format(methods)
    
    def render_type_string(self, t):
        t = t
        pt = self.get_primitive_name(t)
        if pt:
            return pt
        tv = self.seen[t]
        if self.recursive:
            return 'A\nwhere\n' + '\n'.join(
                "  {0} = {1}".format(n, v)
                for n, v in self.defns.iteritems()
            )
        return "\n".join([self.defns[tv], "where"] + [
            "  {0} = {1}".format(n, v)
            for n, v in self.defns.iteritems()
            if n != tv
        ])


class Method(object):
    def __init__(self, parent, name, in_type, out_type):
        self.name = name
        self.in_type = in_type
        self.out_type = out_type
        self.parent = parent
    
    def assert_requirement_satisfied_by(self, other, seen):
        self.in_type.extends(other.in_type, seen)
        other.out_type.extends(self.out_type, seen)
    
    def contains(self, other):
        while other:
            if other == self:
                return True
            other = other.parent
    
    def clone(self, env, cmap):
        return Method(self.parent,
                      self.name,
                      self.in_type.clone(env, cmap),
                      self.out_type.clone(env, cmap))


class Type(object):
    def __init__(self, *methods):
        self.methods = list(methods)
    
    def __repr__(self):
        return TypePrinter().type_string(self)
    
    def structurally_equal(self, other, cmap):
        rother = cmap.get(self)
        rself = cmap.get(other)
        if id(rself) == id(self) or id(rother) == id(other):
            return True
        if rself or rother:
            return False
        cmap[self] = other
        for m in self.methods:
            ns = [n for n in other.methods if m.name == n.name]
            if not ns:
                return False
            n = ns[0]
            if not m.in_type.structurally_equal(n.in_type, cmap):
                return False
            if not m.out_type.structurally_equal(n.out_type, cmap):
                return False
        return True
    
    def clone(self, env, cmap):
        try:
            return cmap[self]
        except KeyError:
            res = Type()
            cmap[self] = res
            res.methods = [m.clone(env, cmap) for m in self.methods]
            return res
            
    def get_method(self, name):
        try:
            m = next(m for m in self.methods if m.name == name)
        except StopIteration:
            raise RequirementsError('missing ' + name)
        return m.clone(m, {self:self})
    
    def extends(self, other, seen):
        """ Assert that self is a subtype of other. That is that other has all
            the methods of self and that the input and output types are 
            compatible. """
        #print self
        #print other
        #print self.structurally_equal(other, {})
        #print
        if (self, other) in seen:
            return
        seen.add((self, other))
        if isinstance(other, Var):
            other._sub_types.append(self)
            other.check_extends(seen)
            return
        if self.structurally_equal(other, {}):
            return
        for om in other.methods:
            m = self.get_method(om.name)
            om.assert_requirement_satisfied_by(m, seen)


class Var(object):
    def __init__(self, scope=None):
        self._super_types = []
        self._sub_types = []
        self._methods = None
        self._scope = scope
    
    def __repr__(self):
        return TypePrinter().type_string(self)
    
    def clone(self, scope, cmap):
        if not scope.contains(self._scope):
            return self
        try:
            return cmap[self]
        except:
            res = Var(self._scope)
            cmap[self] = res
            res._sub_types = [t.clone(scope, cmap) for t in self._sub_types]
            res._super_types = [t.clone(scope, cmap) for t in self._super_types]
            return res
    
    def structurally_equal(self, other, cmap):
        if not isinstance(other, Var):
            return False
        return self._check_equality(self.super_types, other.super_types, cmap) \
           and self._check_equality(self.sub_types, other.sub_types, cmap)
    
    def _check_equality(self, self_types, other_types, cmap):
        for st in self_types:
            if not any(st.structurally_equal(ot, cmap)
                       for ot in other_types):
                return False
        return True
    
    @property
    def methods(self):
        # This doesn't work correctly. It needs to deal with potential 
        # circularity in order for it to operate. As it is, I don't think it
        # actually needs to exist, although it's handy for debugging.
        if self._methods is None:
            subs = self.sub_types
            if subs:
                res = dict((m.name, m) for m in subs[0].methods)
                for sub in subs:
                    seen = set()
                    for m in sub.methods:
                        seen.add(m.name)
                    for s in set(res) - seen:
                        del res[s]
                self._methods = res.values()
            else:
                res = []
                for sup in self.super_types:
                    res.extend(sup.methods)
                self._methods = res
        return self._methods
    
    def _walk_graph(self, following, seen=None):
        if seen is None:
            seen = set()
        for t in following(self):
            if t in seen:
                continue
            seen.add(t)
            yield t
            if isinstance(t, Var):
                for t in t._walk_graph(following, seen):
                    yield t
    
    @property
    def super_types(self):
        res = []
        for t in self._walk_graph(lambda self: self._super_types):
            if isinstance(t, Type):
                res.append(t)
        return res
    
    @property
    def sub_types(self):
        res = []
        for t in self._walk_graph(lambda self: self._sub_types):
            if isinstance(t, Type):
                res.append(t)
        return res
    
    def check_extends(self, seen):
        for sup in self.super_types:
            for sub in self.sub_types:
                sub.extends(sup, seen)
    
    def extends(self, other, seen):
        self._methods = None
        if isinstance(other, Var):
            other._sub_types.append(self)
        self._super_types.append(other)
        self.check_extends(seen)


