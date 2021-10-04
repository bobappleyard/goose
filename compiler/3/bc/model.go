package bc

import (
	"fmt"
	"strings"

	"github.com/bobappleyard/goose/lc"
)

type Step interface {
	s()
}

type Program struct {
	Globals     []lc.Var
	Definitions []Definition
	Blocks      []Block
}

type Definition struct {
	Name  lc.Var
	Block int
}

type Block struct {
	Free  []lc.Var
	Bound []lc.Var
	Steps []Step
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

type PushBlock struct {
	ID int
}

type PushFn struct {
	Start int
}

type Drop struct {
	Var int
}

type Call struct {
	Start int
	Argc  int
}

func (PushBound) s()  {}
func (PushFree) s()   {}
func (PushGlobal) s() {}
func (PushBlock) s()  {}
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

func (s PushBlock) String() string {
	return fmt.Sprintf("BLOCK\t%d", s.ID)
}

func (s PushFn) String() string {
	return fmt.Sprintf("FN\t%d", s.Start)
}

func (s Drop) String() string {
	return fmt.Sprintf("DROP\t%d", s.Var)
}

func (s Call) String() string {
	return fmt.Sprintf("CALL\t%d\t%d", s.Start, s.Argc)
}
