from type_checker import Id, Object, Call, Type, Method, TypeEnvironment, Begin

exprs = [
    Id(0),
    Object(('id', 'x', Id('x'))),
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
]

int_type = Type(Method('@int', Type(), Type()))
void_type = Type(Method('@void', Type(), Type()))

env = TypeEnvironment({0: int_type, 'void': void_type},
                      set([int_type, void_type]))
for expr in exprs:
    t = expr.analyze(env).prune()
    print expr, '::', t
    print
