// Create a tagged representation of a value. Return a NaN floating-point value
// with the tag and value as payloads.
static Gosl gosl_tagged(int tag, uint64_t val) {
    Gosl r;
    r.as_bits.marker = GOSL_NAN_MARK;
    r.as_bits.tag = tag;
    r.as_bits.val = val;
    return r;
}

static bool gosl_is_nan(Gosl x) {
    if (x.as_bits.marker != GOSL_NAN_MARK) {
        return false;
    }
    if (x.as_bits.tag != GOSL_NAN.as_bits.tag) {
        return false;
    }
    return x.as_bits.val == GOSL_NAN.as_bits.val;
}

static bool gosl_eq(Gosl left, Gosl right) {
    if (left.as_float == right.as_float) {
        return true;
    }
    if (gosl_is_nan(left) || gosl_is_nan(right)) {
        return false;
    }
    if (left.as_bits.tag != right.as_bits.tag) {
        return false;
    }
    return left.as_bits.val == right.as_bits.val;
}

// Package an object into a NaN.
static Gosl gosl_ptr(uint8_t tag, void *ptr) {
    uintptr_t pint = (uintptr_t) ptr;
    tag += pint > (1LL << 48);
    return gosl_tagged(tag, pint);
}

// Retrieve the object stored inside the value. If the value is not an object,
// return NULL.
static Gosl *gosl_get_object(Gosl val) {
    if (val.as_bits.marker != GOSL_NAN_MARK) {
        return NULL;
    }
    uintptr_t pint = (uintptr_t) val.as_bits.val;
    if (val.as_bits.tag == GOSL_OBJ_TAG) {
        return (void *) pint;
    }
    if (val.as_bits.tag == GOSL_OBJ_TAG + 1) {
        // In the upper region of canonical space.
        pint |= (0xffffLL << 48);
        return (void *) pint;
    }
    return NULL;
}

//
static bool gosl_has_tag(uint8_t tag, Gosl val) {
    if (val.as_bits.marker != GOSL_NAN_MARK) {
        return false;
    }
    if (val.as_bits.tag != tag) {
        return false;
    }
    return true;
}

//
static bool gosl_is_object(Gosl val) {
    return gosl_has_tag(GOSL_OBJ_TAG, val) || gosl_has_tag(GOSL_OBJ_TAG + 1, val);
}

//
static Gosl gosl_object(Gosl *obj) {
    return gosl_ptr(GOSL_OBJ_TAG, obj);
}

//
static bool gosl_is_class(Gosl val) {
    if (gosl_has_tag(GOSL_VEC_TAG, val)) {
        return true;
    }
    if (gosl_has_tag(GOSL_BUF_TAG, val)) {
        return true;    
    }
    if (gosl_has_tag(GOSL_CLASS_TAG, val)) {
        return true;    
    }
    if (gosl_is_object(val)) {
        return gosl_has_tag(GOSL_CLASS_TAG, gosl_get_object(val)[0]);
    }
    return false;
}

static GoslClass *gosl_get_class(Gosl type) {
    return (GoslClass *) gosl_get_object(type);
}

GoslClass *gosl_object_class(GoslEnv *env, Gosl obj) {
    Gosl c;
    if (!isnan(obj.as_float)) {
        c = env->builtins->classes.Number;
    } else if (gosl_is_nan(obj)) {
        c = env->builtins->classes.Number;
    } else if (gosl_is_class(obj)) {
        c = env->builtins->classes.Class;
    } else if (gosl_eq(obj, GOSL_NULL)) {
        c = env->builtins->classes.Null;
    } else if (gosl_eq(obj, GOSL_TRUE) || gosl_eq(obj, GOSL_FALSE)) {
        c = env->builtins->classes.Boolean;
    } else {
        Gosl *d = gosl_get_object(obj);
        if (gosl_has_tag(GOSL_VEC_TAG, d[0])) {
            c = env->builtins->classes.Vector;
        } else if (gosl_has_tag(GOSL_BUF_TAG, d[0])) {
            c = env->builtins->classes.Buffer;
        } else {
            c = d[0];
        }
    }
    return gosl_get_class(c);
}

//
static int gosl_object_size(Gosl type) {
    if (!gosl_is_class(type)) {
        return -1;
    }
    switch ((int) type.as_bits.tag) {
    case GOSL_CLASS_TAG:
        return GOSL_CLASS_SIZE;
    case GOSL_OBJ_TAG:
    case GOSL_OBJ_TAG + 1:
        return gosl_get_class(type)->field_count;
    case GOSL_VEC_TAG:
        return (int) type.as_bits.val;
    case GOSL_BUF_TAG:
        return (int) (type.as_bits.val + 7) / 8;
    }
    return -1;
}


