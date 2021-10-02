package h2c

import (
	"reflect"
	"testing"

	"github.com/bobappleyard/goose/cont"
	"github.com/bobappleyard/goose/handler"
)

func TestConvertExpr(t *testing.T) {
	for _, test := range []struct {
		name string
		in   handler.Expr
		out  cont.Expr
	}{
		{
			name: "var",
			in:   handler.Var{Name: "hello"},
			out:  cont.Var{Name: "hello"},
		},
		{
			name: "apply",
			in: handler.Apply{
				Fn:  handler.Var{Name: "function"},
				Arg: handler.Var{Name: "arg"},
			},
			out: cont.Apply{
				Fn: cont.Apply{
					Fn:  cont.Var{Name: "function"},
					Arg: cont.Var{Name: "arg"},
				},
				Arg: cont.Var{Name: "#handler"},
			},
		},
		{
			name: "lambda",
			in: handler.Lambda{
				Var:  "x",
				Body: handler.Var{Name: "x"},
			},
			out: cont.Lambda{
				Var: "x",
				Body: cont.Lambda{
					Var:  "#handler",
					Body: cont.Var{Name: "x"},
				},
			},
		},
		{
			name: "signal",
			in: handler.Signal{
				Effect: "effect",
				Arg:    handler.Var{Name: "arg"},
			},
			out: cont.Apply{
				Fn: cont.Apply{
					Fn:  cont.Var{Name: ".effect"},
					Arg: cont.Var{Name: "#handler"},
				},
				Arg: cont.Var{Name: "arg"},
			},
		},
		{
			name: "abortiveHandler",
			in: handler.Handle{
				Eval: handler.Apply{Fn: handler.Var{Name: "effectful"}, Arg: handler.Var{Name: "x"}},
				Handlers: []handler.EffectHandler{
					{
						Effect: "effect",
						Var:    "arg",
						Body:   handler.Var{Name: "arg"},
					},
				},
			},
			out: cont.WithPrompt{
				Fn: cont.Lambda{
					Var: "#prompt",
					Body: cont.Apply{
						Fn: cont.Lambda{
							Var: "#handler",
							Body: cont.Apply{
								Fn: cont.Apply{
									Fn:  cont.Var{Name: "effectful"},
									Arg: cont.Var{Name: "x"},
								},
								Arg: cont.Var{Name: "#handler"},
							},
						},
						Arg: cont.Apply{
							Fn: cont.Apply{
								Fn: cont.Apply{
									Fn:  cont.Var{Name: "object#extend"},
									Arg: cont.Var{Name: ".effect"},
								},
								Arg: cont.Var{Name: "object#empty"},
							},
							Arg: cont.Lambda{
								Var: "arg",
								Body: cont.WithSubCont{
									Prompt: cont.Var{Name: "#prompt"},
									Fn: cont.Lambda{
										Var: "#promptK",
										Body: cont.WithPrompt{
											Fn: cont.Lambda{
												Var:  "#scope",
												Body: cont.Var{Name: "arg"},
											},
										},
									},
								},
							},
						},
					},
				},
			},
		},
		{
			name: "resumptiveHandler",
			in: handler.Handle{
				Eval: handler.Apply{Fn: handler.Var{Name: "effectful"}, Arg: handler.Var{Name: "x"}},
				Handlers: []handler.EffectHandler{
					{
						Effect: "effect",
						Var:    "arg",
						Body: handler.Resume{
							With: handler.Var{Name: "arg"},
						},
					},
				},
			},
			out: cont.WithPrompt{
				Fn: cont.Lambda{
					Var: "#prompt",
					Body: cont.Apply{
						Fn: cont.Lambda{
							Var: "#handler",
							Body: cont.Apply{
								Fn: cont.Apply{
									Fn:  cont.Var{Name: "effectful"},
									Arg: cont.Var{Name: "x"},
								},
								Arg: cont.Var{Name: "#handler"},
							},
						},
						Arg: cont.Apply{
							Fn: cont.Apply{
								Fn: cont.Apply{
									Fn:  cont.Var{Name: "object#extend"},
									Arg: cont.Var{Name: ".effect"},
								},
								Arg: cont.Var{Name: "object#empty"},
							},
							Arg: cont.Lambda{
								Var: "arg",
								Body: cont.WithSubCont{
									Prompt: cont.Var{Name: "#prompt"},
									Fn: cont.Lambda{
										Var: "#promptK",
										Body: cont.WithPrompt{
											Fn: cont.Lambda{
												Var: "#scope",
												Body: cont.WithSubCont{
													Prompt: cont.Var{Name: "#scope"},
													Fn: cont.Lambda{
														Var: "#scopeK",
														Body: cont.PushSubCont{
															Cont: cont.Var{Name: "#scopeK"},
															Scope: cont.PushSubCont{
																Cont:  cont.Var{Name: "#promptK"},
																Scope: cont.Var{Name: "arg"},
															},
														},
													},
												},
											},
										},
									},
								},
							},
						},
					},
				},
			},
		},
	} {
		t.Run(test.name, func(t *testing.T) {
			out, err := ConvertExpr(test.in, false)
			if err != nil {
				t.Fatal(err)
			}
			if !reflect.DeepEqual(out, test.out) {
				t.Errorf("got %#v, expecting %#v", out, test.out)
			}
		})
	}
}
