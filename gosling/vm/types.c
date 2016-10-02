
typedef struct GoslShape GoslShape;
typedef struct GoslShapeList GoslShapeList;
typedef struct GoslOffset GoslOffset;
typedef struct GoslOffsets GoslOffsets;
typedef struct GoslName GoslName;
typedef struct GoslClassSpec GoslClassSpec;
typedef struct GoslSlotSpec GoslSlotSpec;
typedef struct GoslSlot GoslSlot;
typedef struct GoslLifecycle GoslLifecycle;
typedef struct GoslClass GoslClass;
typedef struct GoslUnit GoslUnit;
typedef struct GoslProcess GoslProcess;
typedef struct GoslFrame GoslFrame;
typedef struct GoslEnv GoslEnv;
typedef struct GoslBuiltins GoslBuiltins;

typedef void (GoslImpl)(GoslProcess *p, int re_entry);
typedef void (GoslVisit)(GoslEnv *env, Gosl *obj, Gosl **to);

struct GoslShape {
    GoslShapeList *children;
    int slot_count, ancestor_count, ancestors[];
};

struct GoslShapeList {
    int count;
    GoslShape *shapes[];
};

struct GoslOffset {
    int shape, offset;
};

struct GoslOffsets {
    int offset_count;
    GoslOffset offsets[];
};

struct GoslName {
    int id;
    char *name;
    GoslOffsets *mapping;
};

struct GoslSlotSpec {
    GoslName *name;
    GoslImpl *impl;
};

struct GoslClassSpec {
    GoslUnit *unit;
    GoslLifecycle *lifecycle;
    int slot_count;
    GoslSlotSpec slots[];
};

struct GoslSlot {
    GoslSlotSpec *spec;
    GoslClass *class;
    GoslSlot *outer;
    Gosl value;
};

struct GoslClass {
    Gosl cls;
    GoslUnit *unit;
    GoslClass *ancestor;
    GoslShape *interface;
    GoslLifecycle *lifecycle;
    int field_start, field_count;
    int slot_count;
    GoslSlot slots[];
};

struct GoslLifecycle {
    GoslVisit *visit;
};

struct GoslUnit {
    char *file;
    Gosl values[];
};

struct GoslProcess {
    GoslProcess *next;
    GoslFrame *control, *frame;
    Gosl *sp;
    Gosl stack[GOSL_STACK_SIZE];
};

struct GoslFrame {
    GoslSlot *slot;
    int re_entry;
    Gosl *data;
};

struct GoslEnv {
    GoslProcess *running, *waiting;
    GoslBuiltins *builtins;
    Gosl *current, arena[2 * GOSL_ARENA_SIZE];
};

