NAME := vigiboard
all: build

include buildenv/Makefile.common
PKGNAME := $(NAME)
MODULE := $(NAME)
CODEPATH := $(NAME)
EPYDOC_PARSE := vigiboard\.(widgets|controllers)

install: install_files install_permissions

install_files:
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	mkdir -p $(DESTDIR)/var/log/vigilo/$(NAME)
	# Déplacement du app_cfg.py
	mv $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES` $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/
	ln -s $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES`
	echo $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py >> INSTALLED_FILES
	mkdir -p $(DESTDIR)/var/cache/vigilo/sessions

install_permissions:
	chmod 750 $(DESTDIR)/var/cache/vigilo/sessions
	chown apache: $(DESTDIR)/var/cache/vigilo/sessions


lint: lint_pylint
tests: tests_nose
clean: clean_python
