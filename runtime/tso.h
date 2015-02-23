#ifndef TSO_H
#define TSO_H

#include <stdint.h>

// Forward declarations.
typedef struct TSO_Thread TSO_Thread;
typedef struct TSO_Frame TSO_Frame;
typedef struct TSO_Channel TSO_Channel;
typedef struct TSO_Communication TSO_Communication;
typedef struct TSO_Arena TSO_Arena;
typedef struct TSO_Runtime TSO_Runtime;
typedef struct TSO_IO TSO_IO;

/*

Runtime
=======

Represents all the state that is required to run a Tso program. There will in 
all likelihood only ever be a single instance of the runtime for any given 
program, but you never know.

*/

struct TSO_Runtime {
    // The threads that are waiting to execute.
    TSO_Thread *current_thread, *run_queue;
    // Memory shared between threads.
    TSO_Arena *heap;
    // Pending IO requests.
    TSO_IO *io_events;
};

void tso_main(TSO_Thread *main_thread);

/*

Threads
=======

In this version, threads are purely a userspace construct. A thread represents
a sequence of operations that may be executed concurrently with other such 
sequences. Each thread maintains its own working state (a call stack etc) and
is responsible for descheduling itself (co-operative multitasking).

As none of this is directly accessible to the programmer this should remain an 
implementation detail and so can be altered later on for performance (i.e. to
use more CPU cores).

*/

// Represents an interthread communication. Instances of this will also be 
// emitted by the compiler.
typedef void (*TSO_CommunicationFunction)(TSO_Thread *from, TSO_Thread *to);

// 64k should be enough for anyone.
#define TSO_STACK_SIZE (64*1024)

// The necessary state for a thread to execute.
struct TSO_Thread {
    // The next thread in the queue, be it the queue of threads waiting to run
    // or the queue of threads waiting on a channel. The currently running
    // thread is not in any queues.
    TSO_Thread *next;
    // The current position on the stack.
    // Any pending communication.
    TSO_CommunicationFunction communicate;
    // The top of the stack.
    uint8_t *sp;
    // The current frame.
    TSO_Frame *fp;
    // The call stack. This is untyped here -- the generated code should know
    // how to treat this data appropriately.
    char stack[TSO_STACK_SIZE];
};

// Represents some work to be done by the program. The compiler will emit many
// instances of this type as part of its code generation. It won't quite be a
// single instruction, but will probably not be a great deal of work either.
typedef void (*TSO_Instruction)(TSO_Runtime *e);

// Represents a stack map. This marks objects as live when performing garbage
// collection.
typedef void (*TSO_StackMap)(TSO_Runtime *e, TSO_Frame *fp);

// A pointer into the stack.
struct TSO_Frame {
    // The instruction that will be executed next.
    TSO_Instruction pc;
    // The stack map for this frame.
    TSO_StackMap stack_map;
    // Frame size.
    int size;
    // The rest of the stack. It will not actually be this size.
    uint8_t stack[TSO_STACK_SIZE];
};

void tso_thread_spawn(TSO_Runtime *e, TSO_Thread *t);

/*

Channels
========

Channels are the primary means of synchronisation between threads. They are 
typed communication primitives, where a thread may send values and another 
thread receive them.

The actual transmission of values isn't directly handled here. As the values are
typed that part should be in generated code. The code here is to handle the
scheduling of these transmission events.

*/

typedef enum { TSO_CHAN_EMPTY, TSO_CHAN_SENDING, TSO_CHAN_RECEIVING } TSO_Channel_State;

struct TSO_Channel {
    TSO_Channel_State state;
    TSO_Thread *wait;
};

void tso_send(TSO_Runtime *e, TSO_Channel *ch);
void tso_receive(TSO_Runtime *e, TSO_Channel *ch);

/*
 
*/

#define ARENA_BUFFER_SIZE (1024*1024)

struct TSO_Arena {
    uint8_t *pos, *front, *back;
    uint8_t buffer[2*ARENA_BUFFER_SIZE];
};



#endif

