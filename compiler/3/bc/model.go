package bc

import (
	"fmt"
	"strings"

	"github.com/bobappleyard/goose/lc"
)

type Step interface {
	s()
}

type Block struct {
	Free  []lc.Var
	Bound []lc.Var
	Steps []Step
}

type Program struct {
	Globals []lc.Var
	Blocks  []Block
}

type PushBound struct {
	Var int
}

type PushFree struct {
	Var int
}

type PushGlobal struct {
	Var int
}

type PushFn struct {
	Block    int
	FirstVar int
}

type Drop struct {
	Var int
}

type Call struct {
	Start int
}

func (PushBound) s()  {}
func (PushFree) s()   {}
func (PushGlobal) s() {}
func (PushFn) s()     {}
func (Drop) s()       {}
func (Call) s()       {}

func (b Block) String() string {
	var steps strings.Builder
	steps.WriteString(fmt.Sprintf("BLOCK(%v %v)", b.Free, b.Bound))
	for _, s := range b.Steps {
		steps.WriteString("\n\t")
		steps.WriteString(fmt.Sprint(s))
	}
	return steps.String()
}

func (p Program) String() string {
	var prog strings.Builder
	prog.WriteString("GLOBALS")
	for _, g := range p.Globals {
		prog.WriteString(fmt.Sprintf("\n\t%s", g.Name))
	}
	for i, s := range p.Blocks {
		prog.WriteString("\n")
		prog.WriteString(fmt.Sprintf("%d: %s", i, s))
	}
	return prog.String()
}

func (s PushBound) String() string {
	return fmt.Sprintf("BOUND\t%d", s.Var)
}

func (s PushFree) String() string {
	return fmt.Sprintf("FREE\t%d", s.Var)
}

func (s PushGlobal) String() string {
	return fmt.Sprintf("GLOB\t%d", s.Var)
}

func (s PushFn) String() string {
	return fmt.Sprintf("FN\t%d\t%d", s.Block, s.FirstVar)
}

func (s Drop) String() string {
	return fmt.Sprintf("DROP\t%d", s.Var)
}

func (s Call) String() string {
	return fmt.Sprintf("CALL\t%d", s.Start)
}
