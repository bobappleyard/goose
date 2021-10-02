package lc

import (
	"reflect"
	"testing"
)

func TestReduce(t *testing.T) {
	for _, test := range []struct {
		name    string
		in, out Expr
	}{
		{
			name: "beta",
			in: App{
				Fn: Abs{
					Var:  Var{Name: "x"},
					Body: Var{Name: "x"},
				},
				Arg: Var{Name: "y"},
			},
			out: Var{Name: "y"},
		},
		{
			name: "eta",
			in: Abs{
				Var: Var{Name: "x"},
				Body: App{
					Fn:  Var{Name: "f"},
					Arg: Var{Name: "x"},
				},
			},
			out: Var{Name: "f"},
		},
		{
			name: "omega",
			in: App{
				Fn: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn:  Var{Name: "x"},
						Arg: Var{Name: "x"},
					},
				},
				Arg: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn:  Var{Name: "x"},
						Arg: Var{Name: "x"},
					},
				},
			},
			out: App{
				Fn: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn:  Var{Name: "x"},
						Arg: Var{Name: "x"},
					},
				},
				Arg: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn:  Var{Name: "x"},
						Arg: Var{Name: "x"},
					},
				},
			},
		},
		{
			name: "cps",
			in: Abs{
				Var: Var{Name: "#k19"},
				Body: App{
					Fn: Abs{
						Var: Var{Name: "#k20"},
						Body: App{
							Fn:  Var{Name: "#k20"},
							Arg: Var{Name: "effectful"},
						},
					},
					Arg: Abs{
						Var: Var{Name: "#f17"},
						Body: App{
							Fn: Abs{
								Var: Var{Name: "#k21"},
								Body: App{
									Fn:  Var{Name: "#k21"},
									Arg: Var{Name: "x"},
								},
							},
							Arg: Abs{
								Var: Var{Name: "#x18"},
								Body: App{
									Fn: App{
										Fn:  Var{Name: "#f17"},
										Arg: Var{Name: "#x18"},
									},
									Arg: Var{Name: "#k19"},
								},
							},
						},
					},
				},
			},
			out: Abs{
				Var: Var{Name: "#k19"},
				Body: App{
					Fn: App{
						Fn:  Var{Name: "effectful"},
						Arg: Var{Name: "x"},
					},
					Arg: Var{Name: "#k19"},
				},
			},
		},
		{
			name: "eta-invalid",
			in: App{
				Fn: Var{Name: "f"},
				Arg: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn: App{
							Fn:  Var{Name: "g"},
							Arg: Var{Name: "h"},
						},
						Arg: Var{Name: "x"},
					},
				},
			},
			out: App{
				Fn: Var{Name: "f"},
				Arg: Abs{
					Var: Var{Name: "x"},
					Body: App{
						Fn: App{
							Fn:  Var{Name: "g"},
							Arg: Var{Name: "h"},
						},
						Arg: Var{Name: "x"},
					},
				},
			},
		},
	} {
		t.Run(test.name, func(t *testing.T) {
			out := Reduce(test.in)
			if !reflect.DeepEqual(test.out, out) {
				t.Errorf("got %#v, expecting %#v", out, test.out)
			}
		})
	}
}
