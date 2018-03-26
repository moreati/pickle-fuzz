CC = afl-clang-fast
CXX = afl-clang-fast++

CFLAGS = $(shell ./bin/python3.7-config --cflags)
LDFLAGS = $(shell ./bin/python3.7-config --ldflags)

default: uncpickle_stdin

uncpickle_stdin.o: uncpickle_stdin.c
	$(CC) $(CFLAGS) -c uncpickle_stdin.c -o $@

uncpickle_stdin: uncpickle_stdin.o
	$(CC) uncpickle_stdin.o $(LDFLAGS) -o $@
