// The untyped lambda calculus.
package lc

import "fmt"

type Expr interface {
	expr()
}

type Var struct {
	Name string
}

type App struct {
	Fn  Expr
	Arg Expr
}

type Abs struct {
	Var  Var
	Body Expr
}

func (Var) expr() {}
func (App) expr() {}
func (Abs) expr() {}

func (v Var) String() string {
	return v.Name
}

func (a App) String() string {
	fn := fmt.Sprint(a.Fn)
	arg := fmt.Sprint(a.Arg)
	if _, ok := a.Arg.(App); ok {
		arg = fmt.Sprintf("(%s)", arg)
	}
	if containsLambda(a.Fn) {
		fn = fmt.Sprintf("(%s)", fn)
	}
	return fmt.Sprintf("%s %s", fn, arg)
}

func (l Abs) String() string {
	return fmt.Sprintf("λ%s · %s", l.Var, l.Body)
}

func containsLambda(x Expr) bool {
	switch x := x.(type) {
	case Var:
		return false
	case Abs:
		return true
	case App:
		return containsLambda(x.Arg) || containsLambda(x.Fn)
	}
	panic("unreachable")
}
