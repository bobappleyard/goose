package b2c

import (
	"fmt"
	"io"

	"github.com/bobappleyard/goose/bc"
)

func ConvertProgram(p *bc.Program, w io.Writer) error {
	fmt.Fprintln(w, `#include "goose.h"`)

	// renderBlocks(p, w);
	// renderInit(p, w);

	return nil
}
