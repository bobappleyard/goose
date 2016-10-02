static bool gosl_needs_gc(GoslEnv *env, int size);
static void gosl_gc(GoslEnv *env);
static Gosl *gosl_alloc_block(GoslEnv *env, int size);

Gosl gosl_alloc(GoslEnv *env, Gosl type) {
    int size = gosl_object_size(type);
    if (size == -1) {
        gosl_error_msg(env, "invalid type");
    }
    if (gosl_needs_gc(env, size)) {
        gosl_gc(env);
    }
    if (gosl_needs_gc(env, size)) {
        gosl_error_msg(env, "out of memory");
    }
    Gosl *obj = gosl_alloc_block(env, size);
    obj[0] = type;
    return gosl_object(obj);
}

Gosl gosl_alloc_vector(GoslEnv *env, int count) {
    return gosl_alloc(env, gosl_tagged(GOSL_VEC_TAG, count));
}

Gosl gosl_alloc_buffer(GoslEnv *env, int count) {
    return gosl_alloc(env, gosl_tagged(GOSL_BUF_TAG, count));
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
    for (GoslProcess *p = env->running; p; p = p->next) {
        Gosl *stack = p->stack;
        for (Gosl *sp = p->sp; sp > stack; sp--) {
            if (gosl_is_object(*sp)) {
                *sp = gosl_copy_object(env, *sp, to);
            }
        }
    }
}

static void gosl_rewrite_object(GoslEnv *env, Gosl **finger, Gosl **to) {
    Gosl *data = *finger;
    GoslClass *class = gosl_object_class(env, gosl_object(data));
    *finger += gosl_object_size(data[0]);
    class->lifecycle->visit(env, data, to);
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

