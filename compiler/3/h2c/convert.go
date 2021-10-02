package h2c

import (
	"errors"
	"fmt"

	"github.com/bobappleyard/goose/cont"
	"github.com/bobappleyard/goose/handler"
)

var errUnsupportedSyntax = errors.New("unsupported syntax")
var errNotInHandler = errors.New("not in a handler")

const handlerVariable = "#handler"
const promptVariable = "#prompt"
const scopeVariable = "#scope"
const promptKVariable = "#promptK"
const scopeKVariable = "#scopeK"

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
		Arg: cont.Var{Name: handlerVariable},
	}, nil
}

func convertLambda(e handler.Lambda, inHandler bool) (cont.Expr, error) {
	body, err := ConvertExpr(e.Body, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.Lambda{
		Var:  e.Var,
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

	return cont.WithPrompt{
		Fn: cont.Lambda{
			Var: promptVariable,
			Body: cont.Apply{
				Fn: cont.Lambda{
					Var:  handlerVariable,
					Body: eval,
				},
				Arg: handlerObj,
			},
		},
	}, nil
}

func convertHandlers(handlers []handler.EffectHandler) (cont.Expr, error) {
	var res cont.Expr = cont.Var{Name: "object#empty"}
	for _, h := range handlers {
		b, err := ConvertExpr(h.Body, true)
		if err != nil {
			return nil, err
		}

		res = cont.Apply{
			Fn: cont.Apply{
				Fn: cont.Apply{
					Fn:  cont.Var{Name: "object#extend"},
					Arg: cont.Var{Name: "." + h.Effect},
				},
				Arg: res,
			},
			Arg: cont.Lambda{
				Var: h.Var,
				Body: cont.WithSubCont{
					Prompt: cont.Var{Name: promptVariable},
					Fn: cont.Lambda{
						Var: promptKVariable,
						Body: cont.WithPrompt{
							Fn: cont.Lambda{
								Var:  scopeVariable,
								Body: b,
							},
						},
					},
				},
			},
		}
	}

	return res, nil
}

func convertSignal(e handler.Signal, inHandler bool) (cont.Expr, error) {
	arg, err := ConvertExpr(e.Arg, inHandler)
	if err != nil {
		return nil, err
	}

	return cont.Apply{
		Fn: cont.Apply{
			Fn:  cont.Var{Name: "." + e.Effect},
			Arg: cont.Var{Name: handlerVariable},
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
		Prompt: cont.Var{Name: scopeVariable},
		Fn: cont.Lambda{
			Var: scopeKVariable,
			Body: cont.PushSubCont{
				Cont: cont.Var{Name: scopeKVariable},
				Scope: cont.PushSubCont{
					Cont:  cont.Var{Name: promptKVariable},
					Scope: with,
				},
			},
		},
	}, nil
}
