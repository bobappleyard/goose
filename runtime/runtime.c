#include <stdlib.h>
#include "tso.h"

#include "threads.c"
#include "memory.c"
#include "io.c"

static void tso_init(TSO_Runtime *e) {
    tso_init_threads(e);
    tso_init_memory(e);
    tso_init_io(e);
}

void tso_main(TSO_Thread *main_thread) {
    TSO_Runtime e;
    tso_init(&e);
    e.current_thread = main_thread;
    while (e.current_thread) {
        e.current_thread->pc(&e);
        tso_process_io_events(&e);
        tso_schedule(&e);
    }
}


