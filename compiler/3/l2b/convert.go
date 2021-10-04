package l2b

import (
	"fmt"

	"github.com/bobappleyard/goose/bc"
	"github.com/bobappleyard/goose/lc"
)

func ConvertProgram(p lc.Expr) bc.Program {
	prog := bc.Program{}
	c := converter{
		prog: &prog,
	}
	c.convertBody(p.(lc.Abs))
	return prog
}

type converter struct {
	prog        *bc.Program
	block       int
	free, bound []lc.Var
	pos         int
}

func (c *converter) convertExpr(e lc.Expr) {
	switch e := e.(type) {
	case lc.Var:
		c.addStep(c.convertVar(e))
		c.pos++

	case lc.Abs:
		c.addStep(c.convertLambda(e))
		c.pos++

	case lc.App:
		c.addStep(c.convertCall(e))
	}
}

func (c *converter) convertVar(e lc.Var) bc.Step {
	id := indexOf(e, c.bound)
	if id != -1 {
		return bc.PushBound{Var: id}
	}
	id = indexOf(e, c.free)
	if id != -1 {
		return bc.PushFree{Var: id}
	}
	id = indexOf(e, c.prog.Globals)
	if id == -1 {
		id = len(c.prog.Globals)
		c.prog.Globals = append(c.prog.Globals, e)
	}
	return bc.PushGlobal{Var: id}
}

func (c *converter) convertLambda(e lc.Abs) bc.PushFn {
	block, free := c.convertBody(e)
	start := c.pos

	c.addStep(bc.PushBlock{
		ID: block,
	})
	c.pos++

	for _, v := range free {
		c.convertExpr(v)
	}

	return bc.PushFn{
		Start: start,
	}
}

func (c *converter) convertCall(e lc.App) bc.Call {
	args := flattenArgs(e)
	toPush := make([]bc.Step, len(args))

	for i, a := range args {
		switch a := a.(type) {
		case lc.Var:
			toPush[i] = c.convertVar(a)
		case lc.Abs:
			toPush[i] = c.convertLambda(a)
		}
	}

	start := c.pos
	for _, a := range toPush {
		c.addStep(a)
		c.pos++
	}

	return bc.Call{
		Start: start,
		Argc:  len(args),
	}
}

func (c *converter) convertBody(e lc.Abs) (int, []lc.Var) {
	bound, body := flattenVars(e)
	block := len(c.prog.Blocks)

	inner := converter{
		prog:  c.prog,
		block: block,
		bound: bound,
		free:  usedVars(mergeVars(c.bound, c.free), e),
	}
	c.prog.Blocks = append(c.prog.Blocks, bc.Block{
		Bound: inner.bound,
		Free:  inner.free,
	})
	inner.convertExpr(body)

	return block, inner.free
}

func (c *converter) addStep(s bc.Step) {
	block := &c.prog.Blocks[c.block]
	block.Steps = append(block.Steps, s)
}

func usedVars(scope []lc.Var, e lc.Expr) []lc.Var {
	switch e := e.(type) {
	case lc.Var:
		if appearsIn(e, scope) {
			return []lc.Var{e}
		}
		return nil
	case lc.Abs:
		return usedVars(removeVar(e.Var, scope), e.Body)

	case lc.App:
		usedFn := usedVars(scope, e.Fn)
		usedArgs := usedVars(scope, e.Arg)

		return mergeVars(usedFn, usedArgs)
	}

	panic("unreachable")
}

func flattenVars(a lc.Abs) ([]lc.Var, lc.Expr) {
	var vars []lc.Var
	for {
		vars = append(vars, a.Var)
		if next, ok := a.Body.(lc.Abs); ok {
			a = next
			continue
		}
		return vars, a.Body
	}
}

func flattenArgs(a lc.App) []lc.Expr {
	if _, ok := a.Arg.(lc.App); ok {
		panic(fmt.Sprintf("unexpected application: %#v", a.Arg))
	}
	var args []lc.Expr
	if fn, ok := a.Fn.(lc.App); ok {
		args = flattenArgs(fn)
	} else {
		args = []lc.Expr{a.Fn}
	}
	return append(args, a.Arg)
}

func indexOf(x lc.Var, xs []lc.Var) int {
	for i, c := range xs {
		if x == c {
			return i
		}
	}
	return -1
}

func appearsIn(x lc.Var, xs []lc.Var) bool {
	return indexOf(x, xs) != -1
}

func removeVar(x lc.Var, xs []lc.Var) []lc.Var {
	idx := indexOf(x, xs)
	if idx == -1 {
		return xs
	}
	copy(xs[idx:], xs[idx+1:])
	return xs[:len(xs)-1]
}

func mergeVars(a, b []lc.Var) []lc.Var {
	for _, b := range b {
		if !appearsIn(b, a) {
			a = append(a, b)
		}
	}
	return a
}
