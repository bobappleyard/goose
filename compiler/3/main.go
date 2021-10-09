package main

import (
	"os"

	"github.com/bobappleyard/goose/b2c"
	"github.com/bobappleyard/goose/c2l"
	"github.com/bobappleyard/goose/h2c"
	"github.com/bobappleyard/goose/handler"
	"github.com/bobappleyard/goose/l2b"
	"github.com/bobappleyard/goose/lc"
)

func main() {
	h := handler.Handle{
		Eval: handler.Apply{Fn: handler.Var{Name: "effectful"}, Arg: handler.Var{Name: "x"}},
		Handlers: []handler.EffectHandler{
			{
				Effect: "effect",
				Var:    "arg",
				Body: handler.Apply{
					Arg: handler.Resume{With: handler.Var{Name: "arg"}},
					Fn: handler.Lambda{
						Var:  "res",
						Body: handler.Apply{Fn: handler.Var{Name: "f"}, Arg: handler.Var{Name: "res"}},
					},
				},
			},
		},
	}

	// h := handler.Resume{With: handler.Var{Name: "arg"}}

	// h := handler.Apply{Fn: handler.Var{Name: "effectful"}, Arg: handler.Var{Name: "x"}}

	c, err := h2c.ConvertExpr(h, false)
	if err != nil {
		panic(err)
	}

	// c := cont.WithSubCont{
	// 	Prompt: cont.Var{Name: "prompt"},
	// 	Fn: cont.Lambda{
	// 		Var:  "x",
	// 		Body: cont.Var{Name: "y"},
	// 	},
	// }

	l, err := c2l.ConvertExpr(c)
	if err != nil {
		panic(err)
	}

	b2c.ConvertProgram(l2b.ConvertProgram(lc.Reduce(l)), os.Stdout)
}
