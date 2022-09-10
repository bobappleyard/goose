package schemebackend

import (
	"fmt"

	"applegrove.family/spam/compiler/ast"
	"applegrove.family/spam/compiler/sexpr"
)

type Module struct {
	ns        Namespace
	lastClass int
	code      []sexpr.Node
}

type Context struct {
	module  *Module
	closure []string
}

func (c *Context) DefineRuntimeTypes() {
	resumer := c.module.ns.DefineClass([]Mapping{{
		Method: c.method("call"),
		Impl:   "resumer:call",
	}})
	arith := c.module.ns.DefineClass([]Mapping{{
		Method: c.method("add"),
		Impl:   "arith:add",
	}})
	c.module.code = append(c.module.code,
		sexpr.Call("set!", sexpr.Var("%resume-type-offset"), sexpr.Int(resumer)),
		sexpr.DefineVar("arith", sexpr.Call("vector", sexpr.Int(arith))),
	)
}

func (c *Context) CompileModule(p ast.Module) {
	exports := c.CompileExpr(ast.Create{
		Methods: p.Funcs,
	})
	c.module.code = append(
		c.module.code,
		sexpr.DefineVar(p.Name, exports),
	)
}

func (c *Context) Render() []sexpr.Node {
	table := sexpr.DefineVar("%methods", c.module.ns.Render())
	return append(c.module.code, table)
}

func (c *Context) CompileExpr(x ast.Expr) sexpr.Node {
	switch x := x.(type) {
	case ast.Int:
		return sexpr.Int(x.Value)

	case ast.Ref:
		return c.compileVar(x)

	case ast.Create:
		return c.compileCreate(x)

	case ast.Invoke:
		return c.compileInvoke(x)

	case ast.Handle:
		return c.compileHandle(x)

	case ast.Trigger:
		return c.compileTrigger(x)

	}

	panic("unsupported syntax")
}

func (c *Context) compileVar(x ast.Ref) sexpr.Node {
	for i, v := range c.closure {
		if x.Name != v {
			continue
		}
		return sexpr.Call("vector-ref", sexpr.Var("this"), sexpr.Int(i+1))
	}
	return sexpr.Var(x.Name)
}

func (c *Context) compileCreate(x ast.Create) sexpr.Node {
	id := c.module.lastClass
	c.module.lastClass++

	vs := map[string]bool{}
	freeVariablesExpr(vs, x)
	var closure []string
	for v := range vs {
		if vs[v] {
			closure = append(closure, v)
		}
	}

	d := &Context{
		module:  c.module,
		closure: closure,
	}

	offset := c.module.ns.DefineClass(mapSlice(x.Methods, func(m ast.Method) Mapping {
		name := fmt.Sprintf("%d:%s", id, m.Name)
		c.module.code = append(c.module.code, d.compileMethod(name, m))
		return Mapping{
			Method: c.module.ns.Method(m.Name),
			Impl:   name,
		}
	}))

	args := make([]sexpr.Node, len(closure)+1)
	args[0] = sexpr.Int(offset)
	copy(args[1:], mapSlice(closure, func(v string) sexpr.Node {
		return c.compileVar(ast.Ref{Name: v})
	}))

	return sexpr.Call("vector", args...)
}

func (c *Context) compileInvoke(x ast.Invoke) sexpr.Node {
	return sexpr.Call("method-invoke", append([]sexpr.Node{
		c.CompileExpr(x.Object),
		sexpr.Int(c.method(x.Name)),
	}, mapSlice(x.Args, c.CompileExpr)...)...)
}

func (c *Context) compileMethod(name string, method ast.Method) sexpr.Node {
	body := c.CompileExpr(method.Body)
	return sexpr.DefineFunc(name, append([]string{"this"}, method.Args...), body)
}

func (c *Context) compileHandle(x ast.Handle) sexpr.Node {
	handler := c.compileCreate(ast.Create{Methods: x.With})
	prog := sexpr.Call("lambda", sexpr.List(), c.CompileExpr(x.In))
	return sexpr.Call("install-handlers", handler, prog)
}

func (c *Context) compileTrigger(x ast.Trigger) sexpr.Node {
	return sexpr.Call("trigger-effect", append([]sexpr.Node{
		sexpr.Int(c.method(x.Name)),
	}, mapSlice(x.Args, c.CompileExpr)...)...)
}

func (c *Context) method(name string) int {
	return c.module.ns.Method(name)
}

func mapSlice[T, U any](xs []T, f func(T) U) []U {
	res := make([]U, len(xs))
	for i, x := range xs {
		res[i] = f(x)
	}
	return res
}
