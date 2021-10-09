typedef void *cz_value_t;

typedef struct {
    cz_value_t *frame;
    cz_value_t *closure;
} cz_process_t;

typedef struct {
    int type;
    int frame;
    int closure;
    void (*impl)(cz_process_t *p);
} cz_block_t;

void cz_process_push(cz_process_t *p, cz_value_t x);
void cz_process_call(cz_process_t *p, cz_value_t *base, int argc);

/* Opcodes */

#define CZ_PUSH_BLOCK(id)   cz_process_push(p, cz_gg_blocks + id)
#define CZ_PUSH_BOUND(id)   cz_process_push(p, p->frame[id])
#define CZ_PUSH_FREE(id)    cz_process_push(p, p->closure[id])
#define CZ_PUSH_GLOBAL(id)  cz_process_push(p, cz_gg_globals[id])
#define CZ_PUSH_FN(base)    cz_process_push(p, p->frame + base)
#define CZ_CALL(base, argc) cz_process_call(p, p->frame + base, argc)

#define CZ_BLOCK_TYPE 1