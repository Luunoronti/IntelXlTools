TARGETS = xl710_unlock

CC ?= gcc
CFLAGS ?= -Wall -O2

INST_DIR ?= /usr/sbin


all: $(TARGETS)

clean:
	rm -f $(TARGETS)

%:	%.c
	$(CC) $(CFLAGS) $(LDFLAGS) $< -o $@

install:
	mkdir -p $(DESTDIR)/$(INST_DIR)
	install -m 750 $(TARGETS) $(DESTDIR)/$(INST_DIR)
