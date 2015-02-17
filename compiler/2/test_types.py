from type_checker import *

exprs = [
    Id(0),
    Call(Id(0), 'add', Id(0)),
    Object(('id', 'x', Id('x'))),
    Object(('self', 'x', Id('this'))),
    Call(Id(0), 'add', Object(('add', 'x', Id('x')))),
    Call(Object(('id', 'x', Id('x'))), 'id', Id(0)),
    Object(('gety', 'x', Call(Id('x'), 'y', Id('void')))),
    Object(
        ('gety', 'x', Call(Id('this'), 'y', Id('void'))),
        ('y', 'x', Id(0)),
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
]

num_type = Type()
num_type.methods.append(Method(GlobalScope(), 'add', num_type, num_type))

int_type = Type(Method(GlobalScope(), '@int', Type(), Type()),
                Method(GlobalScope(), 'add', num_type, num_type))
void_type = Type(Method(GlobalScope(), '@void', Type(), Type()))

if_method = Method(GlobalScope(), 'if', None, None)
if_var = Var(if_method)
if_method.in_type = Type(Method(GlobalScope(), 'then', void_type, if_var),
                         Method(GlobalScope(), 'else', void_type, if_var))
if_method.out_type = if_var
if_type = Type(if_method)     

env = TypeEnvironment({0: int_type, 'void': void_type, 'if': if_type})
for expr in exprs:
    print expr,
    try:
        t = expr.analyze(env)
    except Exception as e:
#        raise
        print 'failed:', e
    else:
        print '::', t
    print


