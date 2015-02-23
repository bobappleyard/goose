static void tso_init_threads(TSO_Runtime *e) {
    e->run_queue = NULL;
}

static void tso_run_thread(TSO_Runtime *e) {
    e->current_thread->fp->pc(e);
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
    *queue = item->next;
    item->next = NULL;
    return item;
}

static void tso_schedule(TSO_Runtime *e) {
    if (e->current_thread) {
        tso_thread_enqueue(&e->run_queue, e->current_thread);
    }
    e->current_thread = tso_thread_dequeue(&e->run_queue);
}

void tso_thread_spawn(TSO_Runtime *e, TSO_Thread *t) {
    tso_thread_enqueue(&e->run_queue, t);
}

static void tso_do_send(TSO_Runtime *e, TSO_Channel *ch, TSO_Thread *sender,
                        TSO_Thread *receiver) {
    if (!ch->wait) {
        ch->state = TSO_CHAN_EMPTY;
    }
    sender->communicate(sender, receiver);
    tso_thread_enqueue(&e->run_queue, receiver);
    tso_thread_enqueue(&e->run_queue, sender);
}

void tso_send(TSO_Runtime *e, TSO_Channel *ch) {
    TSO_Thread *sender = e->current_thread;
    e->current_thread = NULL;
    if (ch->state == TSO_CHAN_RECEIVING) {
        TSO_Thread *receiver = tso_thread_dequeue(&ch->wait);
        tso_do_send(e, ch, sender, receiver);
    } else {
        tso_thread_enqueue(&ch->wait, sender);
        ch->state = TSO_CHAN_SENDING;
    }
}

void tso_receive(TSO_Runtime *e, TSO_Channel *ch) {
    TSO_Thread *receiver = e->current_thread;
    e->current_thread = NULL;
    if (ch->state == TSO_CHAN_SENDING) {
        TSO_Thread *sender = tso_thread_dequeue(&ch->wait);
        tso_do_send(e, ch, sender, receiver);
    } else {
        tso_thread_enqueue(&ch->wait, receiver);
        ch->state = TSO_CHAN_RECEIVING;
    }
}


