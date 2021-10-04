package cont

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
	Var  Var
	Body Expr
}

type NewPrompt struct {
}

type PushPrompt struct {
	Prompt Expr
	Scope  Expr
}

type WithSubCont struct {
	Prompt Expr
	Fn     Expr
}

type PushSubCont struct {
	Cont  Expr
	Scope Expr
}

func (Var) expr()         {}
func (Apply) expr()       {}
func (Lambda) expr()      {}
func (NewPrompt) expr()   {}
func (PushPrompt) expr()  {}
func (WithSubCont) expr() {}
func (PushSubCont) expr() {}
