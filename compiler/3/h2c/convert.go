package h2c

import (
	"errors"
	"fmt"

	"github.com/bobappleyard/goose/cont"
	"github.com/bobappleyard/goose/handler"
)

var errUnsupportedSyntax = errors.New("unsupported syntax")
var errNotInHandler = errors.New("not in a handler")

var (
	handlerVariable = cont.Var{Name: "#handler"}
	promptVariable  = cont.Var{Name: "#prompt"}
	scopeVariable   = cont.Var{Name: "#scope"}
	promptKVariable = cont.Var{Name: "#promptK"}
	scopeKVariable  = cont.Var{Name: "#scopeK"}
)

func ConvertExpr(e handler.Expr, inHandler bool) (cont.Expr, error) {
	switch e := e.(type) {

	case handler.Var:
		return convertVariable(e, inHandler)

	case handler.Apply:
		return convertApply(e, inHandler)

	case handler.Lambda:
		return convertLambda(e, inHandler)

	case handler.Handle:
		return convertHandle(e, inHandler)

	case handler.Signal:
		return convertSignal(e, inHandler)

	case handler.Resume:
		return convertResume(e, inHandler)

	}

	return nil, fmt.Errorf("%w: %s", errUnsupportedSyntax, e)
}

func convertVariable(e handler.Var, inHandler bool) (cont.Expr, error) {
	return cont.Var{Name: e.Name}, nil
}

func convertApply(e handler.Apply, inHandler bool) (cont.Expr, error) {
	arg, err := ConvertExpr(e.Arg, inHandler)
	if err != nil {
		return nil, err
	}

	f, err := ConvertExpr(e.Fn, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.Apply{
		Fn:  cont.Apply{Fn: f, Arg: arg},
		Arg: handlerVariable,
	}, nil
}

func convertLambda(e handler.Lambda, inHandler bool) (cont.Expr, error) {
	body, err := ConvertExpr(e.Body, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.Lambda{
		Var:  cont.Var{Name: e.Var},
		Body: cont.Lambda{Var: handlerVariable, Body: body},
	}, nil
}

func convertHandle(e handler.Handle, inHandler bool) (cont.Expr, error) {
	eval, err := ConvertExpr(e.Eval, inHandler)
	if err != nil {
		return nil, err
	}

	handlerObj, err := convertHandlers(e.Handlers)
	if err != nil {
		return nil, err
	}

	return let(promptVariable, cont.NewPrompt{}, cont.PushPrompt{
		Prompt: promptVariable,
		Scope: cont.Apply{
			Fn: cont.Lambda{
				Var:  handlerVariable,
				Body: eval,
			},
			Arg: handlerObj,
		},
	}), nil
}

func let(n cont.Var, v cont.Expr, in cont.Expr) cont.Expr {
	return cont.Apply{
		Fn: cont.Lambda{
			Var:  n,
			Body: in,
		},
		Arg: v,
	}
}

func apply(f cont.Expr, args ...cont.Expr) cont.Expr {
	var res cont.Expr = f
	for _, a := range args {
		res = cont.Apply{
			Fn:  res,
			Arg: a,
		}
	}
	return res
}

func convertHandlers(handlers []handler.EffectHandler) (cont.Expr, error) {
	var res cont.Expr = cont.Var{Name: "runtime.emptyObject"}
	for _, h := range handlers {
		b, err := ConvertExpr(h.Body, true)
		if err != nil {
			return nil, err
		}

		res = apply(
			cont.Var{Name: "runtime.extendObject"},
			cont.Var{Name: "." + h.Effect},
			res,
			convertHandler(cont.Var{Name: h.Var}, b),
		)
	}

	return res, nil
}

func convertHandler(v cont.Var, b cont.Expr) cont.Expr {
	return cont.Lambda{
		Var: v,
		Body: cont.WithSubCont{
			Prompt: promptVariable,
			Fn: cont.Lambda{
				Var: promptKVariable,
				Body: cont.PushPrompt{
					Prompt: promptVariable,
					Scope: let(scopeVariable, cont.NewPrompt{}, cont.PushPrompt{
						Prompt: scopeVariable,
						Scope:  b,
					}),
				},
			},
		},
	}
}

func convertSignal(e handler.Signal, inHandler bool) (cont.Expr, error) {
	arg, err := ConvertExpr(e.Arg, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.Apply{
		Fn: cont.Apply{
			Fn:  cont.Var{Name: "." + e.Effect},
			Arg: handlerVariable,
		},
		Arg: arg,
	}, nil
}

func convertResume(e handler.Resume, inHandler bool) (cont.Expr, error) {
	if !inHandler {
		return nil, errNotInHandler
	}

	with, err := ConvertExpr(e.With, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.WithSubCont{
		Prompt: scopeVariable,
		Fn: cont.Lambda{
			Var: scopeKVariable,
			Body: cont.PushPrompt{
				Prompt: scopeVariable,
				Scope: cont.PushSubCont{
					Cont: scopeKVariable,
					Scope: cont.PushSubCont{
						Cont:  promptKVariable,
						Scope: with,
					},
				},
			},
		},
	}, nil
}
