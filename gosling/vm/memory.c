static bool gosl_needs_gc(GoslEnv *env, int size);
static void gosl_gc(GoslEnv *env);
static Gosl *gosl_alloc_block(GoslEnv *env, int size);

Gosl gosl_alloc(GoslEnv *env, Gosl type) {
    if (!gosl_is_class(type)) {
        gosl_error_msg(env, "invalid type");
    }
    int size = gosl_object_size(type);
    if (gosl_needs_gc(env, size)) {
        gosl_gc(env);
    }
    if (gosl_needs_gc(env, size)) {
        gosl_error_msg(env, "out of memory");
    }
    Gosl *obj = gosl_alloc_block(env, size);
    *obj = type;
    return gosl_object(obj);
}

static bool gosl_needs_gc(GoslEnv *env, int size) {
    int offset = (env->current - env->arena) % GOSL_ARENA_SIZE;
    return offset + size > GOSL_ARENA_SIZE;
}

static Gosl gosl_copy_object(GoslEnv *env, Gosl obj, Gosl **to) {
    Gosl Redirect = env->builtins->classes.Redirect;
    Gosl *data = gosl_get_object(obj);
    Gosl type = data[0];
    if (gosl_eq(type, Redirect)) {
        return data[1];
    }
    int size = gosl_object_size(type);
    Gosl *r = *to;
    for (int i = 0; i < size; i++) {
        **to++ = data[i];
    }
    Gosl p = gosl_object(r);
    data[0] = Redirect;
    data[1] = p;
    return p;
}

static void gosl_copy_roots(GoslEnv *env, Gosl **to) {
    Gosl *stack = env->stack;
    for (Gosl *sp = env->sp; sp > stack; sp--) {
        if (gosl_is_object(*sp)) {
            *sp = gosl_copy_object(env, *sp, to);
        }
    }
}

static void gosl_rewrite_object(GoslEnv *env, Gosl **finger, Gosl **to) {
    Gosl *data = *finger;
    Gosl type = data[0];
    int size = gosl_object_size(type);
    *finger += size;
    if (gosl_has_tag(GOSL_BUF_TAG, type)) {
        return;
    }
    for (int i = 0; i < size; i++) {
        if (gosl_is_object(data[i])) {
            data[i] = gosl_copy_object(env, data[i], to);
        }
    }
}

static void gosl_gc(GoslEnv *env) {
    Gosl *from, *to, *finger;
    int offset = env->current - env->arena;
    if (offset / GOSL_ARENA_SIZE) {
        from = env->arena + GOSL_ARENA_SIZE;
        to = env->arena;
    } else {
        from = env->arena;
        to = env->arena + GOSL_ARENA_SIZE;
    }
    finger = to;
    gosl_copy_roots(env, &to);
    while (finger < to) {
        gosl_rewrite_object(env, &finger, &to);
    }
    env->current = to;
}

static Gosl *gosl_alloc_block(GoslEnv *env, int size) {
    Gosl *res = env->current;
    env->current += size;
    return res;
}

