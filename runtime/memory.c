static void tso_memory_reset_pos(TSO_Arena *heap) {
    heap->pos = heap->front + ARENA_BUFFER_SIZE;
}

static void tso_init_memory(TSO_Runtime *e) {
    TSO_Arena *heap = (TSO_Arena *) malloc(sizeof(TSO_Arena));
    heap->front = heap->buffer;
    heap->back = heap->buffer + ARENA_BUFFER_SIZE;
    tso_memory_reset_pos(heap);
    e->heap = heap;
}

static bool tso_memory_frame_in_bounds(TSO_Thread *t, TSO_Frame *frame) {
    uintptr_t stack_top, stack_bottom, frame;
    stack_top = (uintptr_t) t->stack;
    stack_bottom = (uintptr_t) t->stack + TSO_STACK_SIZE;
    frame = (uintptr_t) frame;
    return stack_top <= frame && frame < stack_bottom;
}

static void tso_memory_mark_thread(TSO_Runtime *e, TSO_Thread *t) {
    if (!t) {
        return;
    }
    TSO_Frame *frame = t->fp;
    while (tso_memory_frame_in_bounds(t, frame)) {
        frame->stack_map(e, frame);
        frame = (TSO_Frame *) ((uint8_t *) frame + frame->size);
    }
}

static void tso_memory_mark_threads(TSO_Runtime *e) {
    tso_memory_mark_thread(e, e->current_thread);
    TSO_Thread *t = e->run_queue;
    while (t) {
        tso_memory_mark_thread(e, t);
        t = t->next;
    }
}

static void tso_memory_collect(TSO_Runtime *e) {
    tso_memory_mark_threads(e);
}


