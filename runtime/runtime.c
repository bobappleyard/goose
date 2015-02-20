#include "tso.h"

#include <stdlib.h>
#include <stdbool.h>


#include "threads.c"
#include "memory.c"
#include "io.c"
//#include "stdlib.c"

static void tso_init(TSO_Runtime *e) {
    tso_init_threads(e);
    tso_init_memory(e);
    tso_init_io(e);
}

static bool tso_program_live(TSO_Runtime *e) {
    return e->current_thread || e->io_events;
}

void tso_main(TSO_Thread *main_thread) {
    TSO_Runtime e;
    tso_init(&e);
    e.current_thread = main_thread;
    while (tso_program_live(&e)) {
        tso_run_thread(&e);
        tso_process_io_events(&e);
        tso_schedule(&e);
    }
}


