CFLAGS := -O2 -Wall -Werror

all: build/gosl.so

clean:
	rm *.o

build/gosl.so: *.c build
	gcc -shared -fPIC -o $@ gosl.c


build:
	mkdir $@



