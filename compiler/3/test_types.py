import type_system
from ast import *
print 'digraph{'

exprs = [
    #Var(0),
    #Object([Method('a', 'x', Var('x'))]),
    #Call(Object([Method('a', 'x', Var('x'))]), 'a', Var(0)),
    #Call(Object([Method('a', 'x', Var('this'))]), 'a', Var(0)),
    #Object([Method('eg', 'x', Call(Var('x'), 'a', Var(0)))]),
    Call(Object([Method('eg', 'x', Call(Var('x'), 'a', Var(0)))]), 'eg', Object([Method('a', 'x', Var('x'))])),
]
rest = [    Call(Call(Object([Method('eg', 'x', Call(Var('x'), 'a', Var(0)))]), 'eg', Object([Method('a', 'x', Var('x'))])), 'add', Var(0)),
    Call(Call(Object([Method('eg', 'x', Call(Var('x'), 'a', Var(0)))]), 'eg', Object([Method('a', 'x', Var('x'))])), 'bdd', Var(0)),
    Call(Call(Object([Method('eg', 'x', Begin([
        Call(Var('x'), 'a', Var('true')),
        Call(Var('x'), 'a', Var(0)),
    ]))]), 'eg', Object([Method('a', 'x', Var('x'))])), 'add', Var(0)),
    Call(Call(Object([Method('eg', 'x', Begin([
        Call(Var('x'), 'a', Var('true')),
        Call(Var('x'), 'a', Var(0)),
    ]))]), 'eg', Object([Method('a', 'x', Var('x'))])), 'bdd', Var(0)),
]

class GlobalScope(object):
    scope = None
    name = "globals"
    
    def contains(self, scope):
        return True

global_scope = GlobalScope()

empty_type = type_system.Concrete([])
num_type = type_system.Concrete([])
num_type.methods = [type_system.Method(global_scope,
                                       'add',
                                       num_type,
                                       num_type)]
int_type = type_system.Concrete([type_system.Method(global_scope,
                                                    '@int',
                                                    empty_type,
                                                    empty_type),
                                 type_system.Method(global_scope,
                                                    'add',
                                                    num_type,
                                                    num_type),
                                 ])

bool_type = type_system.Concrete([type_system.Method(global_scope,
                                                     '@bool',
                                                     empty_type,
                                                     empty_type)])
                                                     
def concrete_subtypes(t):
    res = []
    for u in getattr(t, 'subtypes', []):
        if isinstance(u, type_system.Concrete):
            res.append(u)
        else:
            res.extend(concrete_subtypes(u))
    return res

env = type_system.TypeEnvironment({0: int_type, 'true': bool_type})

for expr in exprs:
    #print expr
    #print
    try:
        res = expr.analyze(env, global_scope)
        print res, '[style=filled, fillcolor=blue]'
    #    print res, res.method_names, getattr(res, 'subtypes', None), [t.method_names for t in concrete_subtypes(res)]
    except Exception as e:
        print e

print '}'
