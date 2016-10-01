#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef uint8_t GoslByte;

typedef union {
    double as_float;
    GoslByte as_bytes[8];
    struct {
        uint64_t val     : 48;
        int8_t   tag     : 3;
        uint16_t marker  : 13;
    } as_bits;
} Gosl;

#define GOSL_NAN_MARK   0x0fff

#define GOSL_OBJ_TAG    0
#define GOSL_CLASS_TAG  2
#define GOSL_BUF_TAG    3
#define GOSL_VEC_TAG    4
#define GOSL_LIT_TAG    5

#define GOSL_NULL   gosl_tagged(0, 0)
#define GOSL_FALSE  gosl_tagged(GOSL_LIT_TAG, 0)
#define GOSL_TRUE   gosl_tagged(GOSL_LIT_TAG, 1)
#define GOSL_NAN    gosl_tagged(GOSL_LIT_TAG, 2)

#define GOSL_ARENA_SIZE (1024*1024)
#define GOSL_CLASS_SIZE 8

#include "types.c"
#include "builtins.c"

void gosl_error_msg(GoslEnv *env, char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}



#include "repr.c"
#include "memory.c"


