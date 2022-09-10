package regex

import (
	"testing"

	"applegrove.family/spam/compiler/parselib"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestRegexCompilation(t *testing.T) {

	var p parselib.LexerProgram

	err := AddTo(&p, 1, "(abc*)+")
	require.Nil(t, err)
	err = AddTo(&p, 2, "(d|e|)f")
	require.Nil(t, err)

	l := p.Lexer([]byte("ababccdfefab"))

	toks := []parselib.Token{
		{ID: 1, Start: 0, End: 6},
		{ID: 2, Start: 6, End: 8},
		{ID: 2, Start: 8, End: 10},
		{ID: 1, Start: 10, End: 12},
	}

	for _, tok := range toks {
		assert.True(t, l.Next())
		assert.Equal(t, tok, l.This())
	}

	assert.False(t, l.Next())
	assert.Nil(t, l.Err())
}
