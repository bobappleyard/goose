package lc

// Reduce the expression e so as to remove superfluous terms according to the constraints of
// continuation passing style. using beta and eta reductions where applicable. This utilises a
// heuristic, which is that every reduction step must actually make the term smaller. Doing so
// prevents the function from looping infinitely at the cost of missing some useful reductions.
func Reduce(e Expr) Expr {
	return reduce(e, true)
}

// reduce does the actual reduction. The reduction rules change subtly depending on whether we are
// on the right or left hand side of an application, so track that through the recursion.
func reduce(expr Expr, rhs bool) Expr {
start:
	switch e := expr.(type) {
	case Var:
		return e

	case Abs:
		body := reduce(e.Body, false)

		// eta reduction: λx·f x --> f
		if body, ok := body.(App); ok && validEta(e, body, rhs) {
			return body.Fn
		}

		return Abs{Var: e.Var, Body: body}

	case App:
		fn := reduce(e.Fn, false)
		arg := reduce(e.Arg, true)

		// beta reduction: (λx·x) y --> y
		if fn, ok := fn.(Abs); ok {
			expr = substitute(fn.Var, arg, fn.Body)
			if size(expr) >= size(e) {
				return expr
			}
			// simulate tail recursion
			goto start
		}

		return App{Fn: fn, Arg: arg}
	}

	panic("unreachable")
}

// Contains reports the presence of the variable v in the expression e, taking into account possible
// bindings of a variable with the same name.
func Contains(v Var, e Expr) bool {
	switch e := e.(type) {
	case Var:
		return e == v

	case Abs:
		if e.Var == v {
			return false
		}
		return Contains(v, e.Body)

	case App:
		return Contains(v, e.Fn) || Contains(v, e.Arg)
	}

	panic("unreachable")
}

// Valid checks whether a term is valid according to the constraints of CPS. This means that, while
// nested abstractions and applications are permissible, this nesting may only appear on the lhs.
func Valid(e Expr) bool {
	switch e := e.(type) {
	case Var:
		return true

	case Abs:
		return Valid(e.Body)

	case App:
		if _, ok := e.Arg.(App); ok {
			return false
		}
		return Valid(e.Fn) && Valid(e.Arg)
	}

	panic("unreachable")
}

// validEta checks whether we can safely perform an eta reduction. This is a bit fiddly, as we are
// trying to maintain CPS-validity.
func validEta(e Abs, body App, rhs bool) bool {
	if body.Arg != e.Var {
		return false
	}
	if Contains(e.Var, body.Fn) {
		return false
	}
	_, ok := body.Fn.(App)
	return !rhs || !ok
}

// substitue replaces all instances of from with to in e, taking into account scoping rules.
func substitute(from Var, to, e Expr) Expr {
	switch e := e.(type) {
	case Var:
		if e == from {
			return to
		}
		return e

	case Abs:
		if e.Var == from {
			return e
		}
		return Abs{Var: e.Var, Body: substitute(from, to, e.Body)}

	case App:
		fn := substitute(from, to, e.Fn)
		arg := substitute(from, to, e.Arg)

		return App{Fn: fn, Arg: arg}
	}

	panic("unreachable")
}

// size of a lambda term.
func size(e Expr) int {
	switch e := e.(type) {
	case Var:
		return 1

	case Abs:
		return 1 + size(e.Body)

	case App:
		return size(e.Fn) + size(e.Arg)
	}

	panic("unreachable")
}
