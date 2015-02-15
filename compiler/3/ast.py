import type_system

class AST(object):
    def __init__(self, *args):
        if len(args) != len(self.__slots__):
            raise TypeError('wrong number of arguments')
        for n, v in zip(self.__slots__, args):
            setattr(self, n, v)
    
    def __repr__(self):
        return '{name}({args})'.format(
            name=type(self).__name__,
            args=', '.join(repr(getattr(self, n))
                           for n in self.__slots__)
        )


class Var(AST):
    __slots__ = ('name',)
    
    def analyze(self, vartypes, method):
        return vartypes[self.name]


class Object(AST):
    __slots__ = ('methods',)
    
    def analyze(self, vartypes, method):
        thistype = type_system.Abstract(method)
        inner = vartypes.bind({'this': thistype})
        restype = type_system.Concrete([m.analyze_method(inner, method) for m in self.methods])
        restype.extends(thistype, {})
        return restype


class Method(AST):
    __slots__ = ('name', 'arg', 'body')
    
    def analyze_method(self, vartypes, method):
        argtype = type_system.Abstract(None)
        resm = type_system.Method(method, self.name, argtype, None)
        argtype.scope = resm
        inner = vartypes.bind({self.arg: argtype})
        restype = self.body.analyze(inner, resm)
        print resm.name, '->', argtype, '[arrowhead=curve]'
        print resm.name, '->', restype, '[arrowhead=crow]'
        resm.out_type = restype
        return resm


class Call(AST):
    __slots__ = ('obj', 'name', 'arg')
    
    def analyze(self, vartypes, method):
        objtype = self.obj.analyze(vartypes, method)
        argtype = self.arg.analyze(vartypes, method)
        restype = type_system.Abstract(type_system.global_scope)
        m = type_system.Method(None, self.name, argtype, restype)
        objtype.has_method(m, {})
        return restype


class Begin(AST):
    __slots__ = ('exprs',)
    
    def analyze(self, vartypes, method):
        for expr in self.exprs:
            res = expr.analyze(vartypes, method)
        return res


