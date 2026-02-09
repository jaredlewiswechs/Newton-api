# ═══════════════════════════════════════════════════════════════
# TINYTALK OBJECTIVE-C - MAKEFILE
# Build system for the tinyTalk interpreter
# ═══════════════════════════════════════════════════════════════

CC = clang
CFLAGS = -Wall -Wextra -fobjc-arc -framework Foundation -O2

# Source files
SOURCES = main.m \
          TTToken.m \
          TTLexer.m \
          TTAST.m \
          TTParser.m \
          TTValue.m \
          TTRuntime.m

# Header files
HEADERS = TTToken.h \
          TTLexer.h \
          TTAST.h \
          TTParser.h \
          TTValue.h \
          TTRuntime.h

# Output binary
TARGET = tinytalk
TEST_TARGET = test_runner

# Test sources (all except main.m)
TEST_SOURCES = test_runner.m \
               TTToken.m \
               TTLexer.m \
               TTAST.m \
               TTParser.m \
               TTValue.m \
               TTRuntime.m

# Default target
all: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES)

# Build test runner
$(TEST_TARGET): $(TEST_SOURCES) $(HEADERS)
	$(CC) $(CFLAGS) -o $(TEST_TARGET) $(TEST_SOURCES)

# Debug build
debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TEST_TARGET)
	rm -rf $(TARGET).dSYM $(TEST_TARGET).dSYM

# Run comprehensive tests
test: $(TEST_TARGET)
	./$(TEST_TARGET)

# Run syntax check tests
check: $(TARGET)
	@echo "Checking example files..."
	./$(TARGET) check examples/player.tt
	./$(TARGET) check examples/risk_governor.tt
	./$(TARGET) check examples/intersection.tt
	./$(TARGET) check examples/stress_test.tt
	./$(TARGET) check examples/turing_test.tt
	./$(TARGET) check examples/acid_test.tt
	@echo "All syntax checks passed!"

# Install to /usr/local/bin (macOS/Linux)
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# Uninstall
uninstall:
	rm -f /usr/local/bin/$(TARGET)

# Show help
help:
	@echo "tinyTalk Objective-C Build System"
	@echo "═══════════════════════════════════════════"
	@echo ""
	@echo "Targets:"
	@echo "  make          Build the interpreter"
	@echo "  make test     Run comprehensive test suite"
	@echo "  make check    Run syntax checks on examples"
	@echo "  make debug    Build with debug symbols"
	@echo "  make clean    Remove build artifacts"
	@echo "  make install  Install to /usr/local/bin"
	@echo "  make help     Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - macOS with Xcode Command Line Tools"
	@echo "  - OR GNUstep on Linux"

.PHONY: all debug clean test check install uninstall help
