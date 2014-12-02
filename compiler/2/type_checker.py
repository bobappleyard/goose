"""

A type checker for an object-oriented language.

Types are structural: an object's type is the set of methods it supports. Upon
this basis nominal typing can be built. Likewise, fields can be constructed as
pairs of methods.

This checker is able to infer types when they are not specified. This is done
using type variables that build up constraints.

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
    
    def type_string(self, t):
        self.type_var_string(t)
        return self.render_type_string(t)
    
    def type_var_string(self, t):
        t = t.prune()
        pt = self.get_primitive_name(t)
        if pt:
            return pt
        try:
            return self.seen[t]
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
        kind = type(t).__name__
        methods = ", ".join("{0}: {1} -> {2}".format(m.name,
                                                     self.type_var_string(m.in_type),
                                                     self.type_var_string(m.out_type))
                            for m in t.methods)
        return "{0} {{{1}}}".format(kind, methods)
    
    def render_type_string(self, t):
        t = t.prune()
        pt = self.get_primitive_name(t)
        if pt:
            return pt
        tv = self.seen[t]
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
        return self._in_type.prune()
    
    @property
    def out_type(self):
        return self._out_type.prune()
    
    def clone(self, env, cmap):
        in_type = self.in_type.clone(env, cmap)
        out_type = self.out_type.clone(env, cmap)
        return Method(self.name, in_type, out_type)
    
    def assert_requirement_satisfied_by(self, other):
        self.in_type.assert_subtype_of(other.in_type)
        other.out_type.assert_subtype_of(self.out_type)


class Type(object):
    def __init__(self, *methods):
        self.methods = list(methods)
    
    def __repr__(self):
        return TypePrinter().type_string(self)
    
    def clone(self, env, cmap):
        if env.is_fixed(self):
            return self
        return type(self)(*[m.clone(env, cmap) for m in self.methods])
    
    def prune(self):
        return self
    
    def get_method(self, name):
        try:
            return next(m for m in self.methods if m.name == name)
        except StopIteration:
            raise RequirementsError('missing ' + name)
    
    def assert_subtype_of(self, other):
        """ Assert that self is a subtype of other. That is that other has all
            the methods of self and that the input and output types are 
            compatible. """
        other = other.prune()
        if self == other:
            return
        for om in other.methods:
            m = self.get_method(om.name)
            om.assert_requirement_satisfied_by(m)
        if isinstance(other, Var):
            other.bound = self


class Var(Type):
    def __init__(self, *methods):
        super(Var, self).__init__(*methods)
        self.bound = None
    
    def clone(self, env, cmap):
        if env.is_fixed(self):
            return self
        if self.bound is not None:
            return self.bound.clone(env, cmap)
        try:
            return cmap[self]
        except KeyError:
            res = super(Var, self).clone(env, cmap)
            cmap[self] = res
            return res
    
    def get_method(self, name):
        try:
            return next(m for m in self.methods if m.name == name)
        except StopIteration:
            res = Method(name, Var(), Var())
            self.methods.append(res)
            return res
    
    def prune(self):
        if self.bound is None:
            return self
        self.bound = self.bound.prune()
        return self.bound
    
    def assert_subtype_of(self, other):
        super(Var, self).assert_subtype_of(other)
        if not isinstance(other, Var):
            self.bound = other


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
        return env[self.name].clone(env, {}).prune()


class Object(AST):
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
            res.methods.append(Method(name, input.prune(), expr.analyze(method_env)))
        res.assert_subtype_of(this)
        return res


class Begin(AST):
    __slots__ = ('exprs',)
    
    def __init__(self, *exprs):
        self.exprs = exprs
    
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
        req = Var(Method(self.name, arg_type, res_type))
        obj_type.assert_subtype_of(req)
        return res_type.prune()


class Let(AST):
    __slots__ = ('bindings', 'expr')

    def analyze_decl(self, env):
        inner_env = env
        for name, val in self.bindings:
            inner_env = inner_env.add_generic(name, val.analyze(env))
        return inner_env
    
    def analyze(self, env):
        return self.expr.analyze(self.analyze_decl(env))


class LetRec(Let):
    def analyze_decl(self, env):
        inner_env = env
        for name, _ in self.bindings:
            env = env.add_fixed(name, Var())
        for name, val in self.bindings:
            inner_env = inner_env.add_generic(name, val.analyze(env))
        return inner_env


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
        return t in self.fixed
    
    def __getitem__(self, name):
        return self.bindings[name]

