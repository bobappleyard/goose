#pragma once

typedef struct { double inner; } Gosl;
typedef unsigned char GoslByte;
typedef void GoslEnv;
typedef void GoslProcess;

typedef void (GoslImpl)(GoslProcess *p);

// Create a new virtual machine.
GoslEnv *gosl_new();

// Load a unit of compiled code at the path specified and execute it using the
// provided virtual machine.
void gosl_load(GoslEnv *env, const char *path);

#define GOSL_VECTOR_TYPE(n) 

//
Gosl gosl_name(GoslEnv *env, const char *name);

//
Gosl gosl_string(GoslEnv *env, const char *str);

//
Gosl gosl_alloc(GoslEnv *env, Gosl type);


