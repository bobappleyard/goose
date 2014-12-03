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
    Let([('ider', Object(('id', 'x', Id('x'))))], Begin(
        Call(Id('ider'), 'id', Id(0)),
        Call(Id('ider'), 'id', Id('void'))
    )),
]

num_type = Type()
num_type.methods.append(Method('add', num_type, num_type))

int_type = Type(Method('@int', Type(), Type()),
                Method('add', num_type, num_type))
void_type = Type(Method('@void', Type(), Type()))

env = TypeEnvironment({0: int_type, 'void': void_type})
for expr in exprs:
    try:
        t = expr.analyze(env).prune()
    except RequirementsError as e:
        print expr, 'failed:', e
    else:
        print expr, '::', t
    print

