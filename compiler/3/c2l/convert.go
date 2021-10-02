package c2l

import (
	"errors"
	"fmt"

	"github.com/bobappleyard/goose/cont"
	"github.com/bobappleyard/goose/lc"
)

var errUnsupportedSyntax = errors.New("unsupported syntax")

func ConvertExpr(e cont.Expr) (lc.Expr, error) {
	c := new(converter)
	res := c.convertExpr(e)
	if c.err != nil {
		return nil, c.err
	}
	return res, nil
}

type converter struct {
	lastSym int
	err     error
}

func (c *converter) convertExpr(e cont.Expr) lc.Expr {
	if c.err != nil {
		return nil
	}

	switch e := e.(type) {

	case cont.Var:
		return c.convertVar(e)

	case cont.Apply:
		return c.convertApply(e)

	case cont.Lambda:
		return c.convertLambda(e)

	case cont.WithPrompt:
		return c.convertWithPrompt(e)

	case cont.WithSubCont:
		return c.convertWithSubCont(e)

	case cont.PushSubCont:
		return c.convertPushSubCont(e)

	}

	c.err = errUnsupportedSyntax
	return nil
}

func (c *converter) gensym(base string) lc.Var {
	c.lastSym++
	return lc.Var{Name: fmt.Sprintf("#%s%d", base, c.lastSym)}
}

func apply(f, arg0 lc.Expr, args ...lc.Expr) lc.Expr {
	var res lc.Expr = lc.App{
		Fn:  f,
		Arg: arg0,
	}
	for _, a := range args {
		res = lc.App{
			Fn:  res,
			Arg: a,
		}
	}
	return res
}

func lambda(arg lc.Var, body lc.Expr) lc.Expr {
	return lc.Abs{Var: arg, Body: body}
}

func (c *converter) convertVar(e cont.Var) lc.Expr {
	k := c.gensym("k")

	v := lc.Var{Name: e.Name}

	return lambda(k, apply(k, v))
}

func (c *converter) convertApply(e cont.Apply) lc.Expr {
	f := c.gensym("f")
	x := c.gensym("x")
	k := c.gensym("k")

	pf := c.convertExpr(e.Fn)
	px := c.convertExpr(e.Arg)

	return lambda(k, apply(pf, lambda(f, apply(px, lambda(x, apply(f, x, k))))))
}

func (c *converter) convertLambda(e cont.Lambda) lc.Expr {
	k := c.gensym("k")
	kk := c.gensym("k")
	v := lc.Var{Name: e.Var}
	body := c.convertExpr(e.Body)

	return lambda(k, apply(k, lambda(v, lambda(kk, apply(body, kk)))))
}

func (c *converter) convertWithPrompt(e cont.WithPrompt) lc.Expr {
	k := c.gensym("k")
	f := c.gensym("f")
	fn := c.convertExpr(e.Fn)

	withPrompt := lc.Var{Name: "runtime.withPrompt"}

	return lambda(k, apply(fn, lambda(f, apply(withPrompt, f, k))))
}

func (c *converter) convertWithSubCont(e cont.WithSubCont) lc.Expr {
	k := c.gensym("k")
	p := c.gensym("p")
	f := c.gensym("f")

	pr := c.convertExpr(e.Prompt)
	fn := c.convertExpr(e.Fn)
	withSubCont := lc.Var{Name: "runtime.withSubCont"}

	return lambda(k, apply(pr, lambda(p, apply(fn, lambda(f, apply(withSubCont, p, f, k))))))
}

func (c *converter) convertPushSubCont(e cont.PushSubCont) lc.Expr {
	k := c.gensym("k")
	m := c.gensym("meta")

	km := c.convertExpr(e.Cont)
	sc := c.convertExpr(e.Scope)

	psc := lc.Var{Name: "runtime.pushSubCont"}

	return lambda(k, apply(km, lambda(m, apply(psc, m, sc, k))))
}
