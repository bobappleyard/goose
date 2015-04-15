from type_checker import *

class AST(object):
    def __init__(self, *args):
        sls = self.__slots__
        if len(args) != len(sls):
            raise TypeError('wrong number of arguments')
        for n, v in zip(sls, args):
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
        if len(args)+1 < len(self.__slots__):
            raise TypeError('wrong number of arguments')
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
        env = env.bind('this', this)
        for name, arg, expr in self.attrs:
            input = Var()
            method_env = env.bind(arg, input)
            m = Method(env.scope, name, input, None)
            input._scope = m
            m.out_type = expr.analyze(method_env)
            res.methods.append(m)
        res.extends(this, env.seen)
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
        res_type = Var(env.scope)
        req = Type(Method(None, self.name, arg_type, res_type))
        obj_type.extends(req, env.seen)
        return res_type


class GlobalScope(object):
    parent = None
    name = 'globals'
    def contains(self, other):
        return True


class TypeEnvironment(object):
    def __init__(self, bindings=None, scope=GlobalScope()):
        self.bindings = bindings or {}
        self.scope = scope
        self.seen = set()
    
    def bind(self, name, t):
        bindings = copy(self.bindings)
        bindings[name] = t
        return TypeEnvironment(bindings)
    
    def in_scope(self, scope):
        return TypeEnvironment(self.bindings, scope)
    
    def __getitem__(self, name):
        return self.bindings[name]


