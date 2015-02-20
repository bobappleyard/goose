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

static void tso_alloc(TSO_Runtime *e, ) {
    
}