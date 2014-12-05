"""

A type checker for an object-oriented language.

Types are structural: an object's type is the set of methods it supports. This
is done by making assertions about types when analysing expressions which form a
set of constraints about a program. Finding the type of an expression requires
that the constraints be solved.

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
    def __init__(self, name, in_type, out_type):
        self.name = name
        self._in_type = in_type
        self._out_type = out_type
    
    @property
    def in_type(self):
        if self.name.startswith('@'):
            return self._in_type
        return self._in_type
    
    @property
    def out_type(self):
        if self.name.startswith('@'):
            return self._out_type
        return self._out_type
    
    def clone(self, env, cmap):
        in_type = self.in_type.clone(env, cmap)
        out_type = self.out_type.clone(env, cmap)
        return Method(self.name, in_type, out_type)
    
    def assert_requirement_satisfied_by(self, other):
        self.in_type.extends(other.in_type)
        other.out_type.extends(self.out_type)


class Type(object):
    def __init__(self, *methods):
        self.methods = list(methods)
    
    def __repr__(self):
        return TypePrinter().type_string(self)
    
    def structurally_equal(self, other, cmap):
        if self == other:
            return True
        rother = cmap.get(self)
        rself = cmap.get(other)
        if rself == self or rother == other:
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
    
    def get_method(self, name):
        try:
            return next(m for m in self.methods if m.name == name)
        except StopIteration:
            raise RequirementsError('missing ' + name)
    
    def extends(self, other):
        """ Assert that self is a subtype of other. That is that other has all
            the methods of self and that the input and output types are 
            compatible. """
        if isinstance(other, Var):
            other._sub_types.append(self)
            other.check_extends()
            return
        if self.structurally_equal(other, {}):
            return
        for om in other.methods:
            m = self.get_method(om.name)
            om.assert_requirement_satisfied_by(m)


class Var(object):
    def __init__(self):
        self._super_types = []
        self._sub_types = []
        self._methods = None
    
    def __repr__(self):
        return TypePrinter().type_string(self)
    
    def structurally_equal(self, other, cmap):
        return self == other
    
    @property
    def methods(self):
        if self._methods is None:
            subs = self.sub_types
            if subs:
                res = dict((m.name, m) for m in subs[0].methods)
                for sub in subs[1:]:
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
    
    @property
    def super_types(self):
        res = []
        cur = self
        for cur in self._super_types:
            if isinstance(cur, Type):
                res.append(cur)
            else:
                res.extend(cur.super_types)
        return res
    
    @property
    def sub_types(self):
        res = []
        cur = self
        for cur in self._sub_types:
            if isinstance(cur, Type):
                res.append(cur)
            else:
                res.extend(cur.sub_types)
        return res
    
    def check_extends(self):
        for sup in self.super_types:
            for sub in self.sub_types:
                sub.extends(sup)
    
    def extends(self, other):
        self._methods = None
        if isinstance(other, Var):
            other._sub_types.append(self)
        self._super_types.append(other)
        self.check_extends()


class AST(object):
    def __init__(self, *args):
        for n, v in zip(self.__slots__, args):
            setattr(self, n, v)
    
    def __repr__(self):
        return "{0}({1})".format(type(self).__name__,
                                 ", ".join(repr(getattr(self, n)) 
                                           for n in self.__slots__))


class Id(AST):
    __slots__ = ('name',)

    def analyze(self, env):
        return env[self.name]


class MultiAST(AST):
    def __init__(self, *args):
        sls = self.__slots__
        for n, v in zip(sls[:-1], args):
            setattr(self, n, v)
        setattr(self, sls[-1], args[len(sls)-1:])


class Object(MultiAST):
    __slots__ = ('attrs',)
    
    def __init__(self, *attrs):
        self.attrs = attrs

    def analyze(self, env):
        res = Type()
        this = Var()
        env = env.add_fixed('this', this)
        for name, arg, expr in self.attrs:
            input = Var()
            method_env = env.add_fixed(arg, input)
            res.methods.append(Method(name, input, expr.analyze(method_env)))
        res.extends(this)
        return res


class Begin(MultiAST):
    __slots__ = ('exprs',)
    
    def analyze(self, env):
        for expr in self.exprs:
            res = expr.analyze(env)
        return res


class Call(AST):
    __slots__ = ('obj', 'name', 'arg')

    def analyze(self, env):
        obj_type = self.obj.analyze(env)
        arg_type = self.arg.analyze(env)
        res_type = Var()
        req = Type(Method(self.name, arg_type, res_type))
        obj_type.extends(req)
        return res_type


class TypeEnvironment(object):
    def __init__(self, bindings=None, fixed=None):
        self.bindings = bindings or {}
        self.fixed = fixed or frozenset()
    
    def add_generic(self, name, t):
        bindings = copy(self.bindings)
        bindings[name] = t
        return TypeEnvironment(bindings, self.fixed)
    
    def add_fixed(self, name, t):
        bindings = copy(self.bindings)
        bindings[name] = t
        return TypeEnvironment(bindings, self.fixed | frozenset((t,)))
    
    def is_fixed(self, t):
        return True
        return t in self.fixed
    
    def __getitem__(self, name):
        return self.bindings[name]

