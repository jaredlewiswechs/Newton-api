CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2 -I./src
SRC = src/lexer.c src/parser.c src/runtime.c src/tinytalk_stdlib.c src/main.c
OBJ = $(SRC:.c=.o)
TARGET = tinytalk

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

test: $(TARGET)
	@echo "Running hello_world.tt..."
	./$(TARGET) run examples/hello_world.tt
	@echo ""
	@echo "Running calculator.tt..."
	./$(TARGET) run examples/calculator.tt

.PHONY: all clean test
