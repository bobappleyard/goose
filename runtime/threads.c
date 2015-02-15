static void tso_init_threads(TSO_Runtime *e) {
    e->run_queue = NULL;
}

static void tso_thread_enqueue(TSO_Thread **queue, TSO_Thread *thread) {
    TSO_Thread *item = *queue;
    if (!item) {
        *queue = thread;
        return;
    }
    while((item = item->next)) {}
    item->next = thread;
}

static TSO_Thread *tso_thread_dequeue(TSO_Thread **queue) {
    TSO_Thread *item = *queue;
    if (!item) {
        return NULL;
    }
    item->next = NULL;
    *queue = item->next;
    return item;
}

static void tso_schedule(TSO_Runtime *e) {
    if (e->current_thread) {
        tso_thread_enqueue(&e->run_queue, e->current_thread);
    }
    e->current_thread = tso_thread_dequeue(&e->run_queue);
}

void tso_send(TSO_Runtime *e, TSO_Channel *ch) {
    TSO_Thread *sender = e->current_thread;
    e->current_thread = NULL;
    if (ch->state == TSO_CHAN_RECEIVING) {
        TSO_Thread *receiver = tso_thread_dequeue(&ch->wait);
        if (!ch->wait) {
            ch->state = TSO_CHAN_EMPTY;
        }
        sender->communicate(sender, receiver);
        tso_thread_enqueue(&e->run_queue, receiver);
        tso_thread_enqueue(&e->run_queue, sender);
    } else {
        tso_thread_enqueue(&ch->wait, sender);
        ch->state = TSO_CHAN_SENDING;
    }
}

void tso_receive(TSO_Runtime *e, TSO_Channel *ch) {
    TSO_Thread *receiver = e->current_thread;
    e->current_thread = NULL;
    if (ch->state == TSO_CHAN_RECEIVING) {
        TSO_Thread *sender = tso_thread_dequeue(&ch->wait);
        if (!ch->wait) {
            ch->state = TSO_CHAN_EMPTY;
        }
        sender->communicate(sender, receiver);
        tso_thread_enqueue(&e->run_queue, sender);
        tso_thread_enqueue(&e->run_queue, receiver);
    } else {
        tso_thread_enqueue(&ch->wait, receiver);
        ch->state = TSO_CHAN_RECEIVING;
    }
}


