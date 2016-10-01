static bool gosl_eq(Gosl left, Gosl right) {
    if (left.as_float == right.as_float) {
        return true;
    }
    if (left.as_bits.tag != right.as_bits.tag) {
        return false;
    }
    return left.as_bits.val == right.as_bits.val;
}

// Create a tagged representation of a value. Return a NaN floating-point value
// with the tag and value as payloads.
static Gosl gosl_tagged(int tag, uint64_t val) {
    Gosl r;
    r.as_bits.marker = GOSL_NAN_MARK;
    r.as_bits.tag = tag;
    r.as_bits.val = val;
    return r;
}

// Package an object into a NaN.
static Gosl gosl_ptr(uint8_t tag, void *ptr) {
    uintptr_t pint = (uintptr_t) ptr;
    tag += pint > (1LL << 48);
    return gosl_tagged(tag, pint);
}

// Retrieve the object stored inside the value. If the value is not an objet,
// return NULL.
static void *gosl_get_ptr(uint8_t tag, Gosl val) {
    if (val.as_bits.marker != GOSL_NAN_MARK) {
        return NULL;
    }
    uintptr_t pint = (uintptr_t) val.as_bits.val;
    if (val.as_bits.tag == tag) {
        return (void *) pint;
    }
    if (val.as_bits.tag == tag + 1) {
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
static Gosl *gosl_get_object(Gosl obj) {
    return gosl_get_ptr(GOSL_OBJ_TAG, obj);
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
    if (!gosl_is_class(type)) {
        return NULL;
    }
    return (GoslClass *) gosl_get_object(type);
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


