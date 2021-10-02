package handler

type Expr interface {
	expr()
}

type Var struct {
	Name string
}

type Apply struct {
	Fn  Expr
	Arg Expr
}

type Lambda struct {
	Var  string
	Body Expr
}

type Handle struct {
	Eval     Expr
	Handlers []EffectHandler
}

type EffectHandler struct {
	Effect string
	Var    string
	Body   Expr
}

type Signal struct {
	Effect string
	Arg    Expr
}

type Resume struct {
	With Expr
}

func (Var) expr()    {}
func (Apply) expr()  {}
func (Lambda) expr() {}
func (Handle) expr() {}
func (Signal) expr() {}
func (Resume) expr() {}
