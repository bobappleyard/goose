struct GoslBuiltinClasses {
    Gosl Object, Name, Class, Redirect;
    Gosl Null, Boolean, Number, Buffer, Vector;
};

struct GoslBuiltins {
    struct GoslBuiltinClasses classes;
};

static void gosl_init_core_types(GoslEnv *env);

static void gosl_init_builtins(GoslEnv *env) {
    env->builtins = malloc(sizeof(GoslBuiltins));
    gosl_init_core_types(env);
}


static void std_visit(GoslEnv *env, Gosl *obj, Gosl **to) {
    int size = gosl_object_size(obj[0]);
    for (int i = 0; i < size; i++) {
        if (gosl_is_object(obj[i])) {
            obj[i] = gosl_copy_object(env, obj[i], to);
        }
    }
}

static void gosl_init_core_types(GoslEnv *env) {
}

