from type_checker import *
from ast import *

exprs = [
    Id(0),
    Call(Id(0), 'add', Id(0)),
    Call(Id(0), 'add', Id(0.5)),
    Object(('id', 'x', Id('x'))),
    Object(('self', 'x', Id('this'))),
    Call(Id(0), 'add', Object(('add_to_int', 'x', Id('x')))),
    Call(Object(('id', 'x', Id('x'))), 'id', Id(0)),
    Object(('gety', 'x', Call(Id('x'), 'y', Id('void')))),
    Object(
        ('gety', 'x', Call(Id('this'), 'y', Id('void'))),
        ('y', 'x', Id(0)),
    ),
    Call(
        Object(
            ('gety', 'x', Call(Id('this'), 'y', Id('void'))),
            ('y', 'x', Id(0)),
        ),
        'gety',
        Id('void')
    ),
    Call(Object(('gety', 'x', Call(Id('x'), 'y', Id('void')))),
         'gety',
         Object(('y', 'x', Id(0)))),
    Object(('f', 'x', Begin(
            Call(Id('x'), 'f', Id(0)),
            Call(Id('x'), 'g', Id(0))
    ))),
    Object(('f', 'x', Call(Id('x'), 'g', Call(Id('x'), 'h', Id('void'))))),
    Object(('f', 'x', Call(Id('x'), 'g', Id('x')))),
    Object(('f', 'x', Call(Id('this'), 'g', Id('x')))),
    Call(Id('if'), 'if', Object(('then', 'x', Id(0)), 
                                ('else', 'x', Call(Id(0), 'add', Id(0))))),
    Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                ('else', 'x', Id(0)))),
    Call(Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                     ('else', 'x', Id(0)))),
        'add',
        Id(0)),
    Call(Call(Id('if'), 'if', Object(('then', 'x', Id(0)),
                                     ('else', 'x', Call(Id(0), 'add', Id(0))))),
        'add',
        Id(0)),
    Call(Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                     ('else', 'x', Id(0)))),
        'f',
        Id(0)),
    Begin(
        Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                    ('else', 'x', Id(0)))),
        Call(Id('if'), 'if', Object(('then', 'x', Id('void')), 
                                    ('else', 'x', Id('void')))),
    ),
    Call(Begin(
        Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                    ('else', 'x', Id(0)))),
        Call(Id('if'), 'if', Object(('then', 'x', Id('void')), 
                                    ('else', 'x', Id('void')))),
    ), 'add', Id(0)),
    Call(Begin(
        Call(Id('if'), 'if', Object(('then', 'x', Id('void')), 
                                    ('else', 'x', Id('void')))),
        Call(Id('if'), 'if', Object(('then', 'x', Id(0)), 
                                    ('else', 'x', Id(0)))),
    ), 'add', Id(0)),
    Begin(
        Call(Id('if'), 'if', Object(('then', 'x', Id('void')), 
                                    ('else', 'x', Id('void')))),
        Call(Id('if'), 'if', Object(('then', 'x', Call(Id(0), 'add', Id(0))), 
                                    ('else', 'x', Id(0)))),
    ),
    Call(Object(('eg', 'id', Call(Id('id'), 'id', Id(0)))),
         'eg',
         Object(('id', 'x', Id('x')))),
    Call(Object(('eg', 'id', Begin(Call(Id('id'), 'id', Id('void')),
                                   Call(Id('id'), 'id', Id(0))))),
         'eg',
         Object(('id', 'x', Id('x')))),
    Call(Object(('eg', 'id', Begin(Call(Id('id'), 'id', Id(0)),
                                   Call(Id('id'), 'id', Id('void'))))),
         'eg',
         Object(('id', 'x', Id('x')))),
    Call(Call(Object(('eg', 'id', Begin(Call(Id('id'), 'id', Id('void')),
                                        Call(Id('id'), 'id', Id(0))))),
              'eg',
              Object(('id', 'x', Id('x')))),
         'add',
         Id(0)),
    Call(Call(Object(('eg', 'id', Begin(Call(Id('id'), 'id', Id('void')),
                                        Call(Id('id'), 'id', Id(0))))),
              'eg',
              Object(('id', 'x', Id('x')))),
         'bdd',
         Id(0)),
    Object(('rec', 'x', Call(Id('this'), 'rec', Id('x')))),
    Call(Object(('rec2', 'x',
                 Call(Object(('inner', 'that',
                              Call(Id('if'), 'if', 
                                   Object(('then', '_', Call(Id('that'), 'rec2', Id('x'))),
                                          ('else', '_', Id(0)))))),
                      'inner',
                      Id('this')))),
         'rec2',
         Id(0)),
    Call(Object(('rec', 'x', Call(Id('this'), 'rec', Id('x')))), 'rawr', Id('void')),
    Call(Object(('rec2', 'x',
                 Call(Object(('inner', 'that',
                              Call(Id('if'), 'if', 
                                   Object(('then', '_', Call(Id('x'), 'rec2', Id('that'))),
                                          ('else', '_', Id(0)))))),
                      'inner',
                      Id('this')))),
         'rec2',
         Object(('rec2', 'x',
                 Call(Object(('inner', 'that',
                              Call(Id('if'), 'if', 
                                   Object(('then', '_', Call(Id('x'), 'rec2', Id('that'))),
                                          ('else', '_', Id(0)))))),
                      'inner',
                      Id('this'))))),
]


global_scope = GlobalScope()

num_type = Type()
num_type.methods.append(Method(global_scope, 'add', num_type, num_type))

int_add_method = Method(global_scope, 'add', None, None)
int_type = Type()
int_type.methods = [
    Method(global_scope, '@int', Type(), Type()),
    int_add_method,
    Method(global_scope, 'add_to_int', int_type, int_type)
]
int2int_add_method = Method(global_scope, 'add_to_int', int_type, None)
int_ret_type = Var(int_add_method)
int2int_add_method.out_type = int_ret_type
int_add_method.in_type = Type(int2int_add_method)
int_add_method.out_type = int_ret_type

void_type = Type(Method(global_scope, '@void', Type(), Type()))

if_method = Method(global_scope, 'if', None, None)
if_var = Var(if_method)
if_method.in_type = Type(Method(global_scope, 'then', void_type, if_var),
                         Method(global_scope, 'else', void_type, if_var))
if_method.out_type = if_var
if_type = Type(if_method)     

float_type = Type()
float_type.methods = [
    Method(global_scope, '@float', Type(), Type()),
    Method(global_scope, 'add_to_int', int_type, float_type)
]

env = TypeEnvironment({0: int_type, 0.5: float_type, 'void': void_type, 'if': if_type})

int_type.extends(int_type, env.seen)

for expr in exprs:
    print expr,
    try:
        t = expr.analyze(env)
    except Exception as e:
        #raise
        print 'failed:', e
    else:
        print '::', t
    print
    



