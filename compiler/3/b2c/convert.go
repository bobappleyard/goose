package b2c

import (
	"fmt"
	"io"

	"github.com/bobappleyard/goose/bc"
)

func ConvertProgram(p bc.Program, w io.Writer) error {
	c := converter{
		program: &p,
		output:  w,
	}
	c.Println(`#include "cz.h"`)
	c.ForEachBlock(blockForwardRef)
	c.Printf(`static cz_block_t cz_gg_blocks[] = {`)
	c.ForEachBlock(blockStaticData)
	c.Println("\n};")
	c.Println(`static cz_value_t cz_gg_globals[] = {};`)
	c.ForEachBlock(blockImplementation)
	return c.err
}

type converter struct {
	program *bc.Program
	output  io.Writer
	err     error
}

func (c *converter) Println(s string) {
	c.Printf(s + "\n")
}

func (c *converter) Printf(pattern string, args ...interface{}) {
	if c.err != nil {
		return
	}
	_, c.err = fmt.Fprintf(c.output, pattern, args...)
}

func (c *converter) ForEachBlock(f func(*converter, int, bc.Block)) {
	for i, b := range c.program.Blocks {
		if c.err != nil {
			return
		}
		f(c, i, b)
	}
}

func blockName(i int) string {
	return fmt.Sprintf("cz_gg_block_%d", i)
}

func blockDecl(i int) string {
	return fmt.Sprintf("static void %s(cz_process_t *p)", blockName(i))
}

func blockForwardRef(c *converter, i int, b bc.Block) {
	c.Printf("%s;\n", blockDecl(i))
}

func blockStaticData(c *converter, i int, b bc.Block) {
	if i > 0 {
		c.Printf(",")
	}
	c.Printf(`
	{
		.type = CZ_BLOCK_TYPE,
		.closure = %d,
		.frame = %d,
		.impl = &%s
	}`, len(b.Free), b.Allocs, blockName(i))
}

func blockImplementation(c *converter, i int, b bc.Block) {
	c.Printf("%s {\n", blockDecl(i))
	for _, op := range b.Steps {
		c.Printf("\t%s;\n", stepCode(c, op))
	}
	c.Println("}")
}

func stepCode(c *converter, s bc.Step) string {
	switch s := s.(type) {
	case bc.PushBound:
		return fmt.Sprintf("CZ_PUSH_BOUND(%d)", s.Var)

	case bc.PushFree:
		return fmt.Sprintf("CZ_PUSH_FREE(%d)", s.Var)

	case bc.PushGlobal:
		return fmt.Sprintf("CZ_PUSH_GLOBAL(%d)", s.Var)

	case bc.PushBlock:
		return fmt.Sprintf("CZ_PUSH_BLOCK(%d)", s.ID)

	case bc.PushFn:
		return fmt.Sprintf("CZ_PUSH_FN(%d)", s.Start)

	case bc.Call:
		return fmt.Sprintf("CZ_CALL(%d, %d)", s.Start, s.Argc)

	}

	panic("unreachable")
}
