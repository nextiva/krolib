PROJECT_NAME := "Krolib"
BOLD := \033[1m
RESET := \033[0m

.DEFAULT: help

.PHONY: help
help:
	@echo "$(BOLD)$(PROJECT_NAME)$(RESET)"
	@echo ""
	@echo "$(BOLD)make docs$(RESET)"
	@echo "    build documentation"
	@echo ""

.PHONY: docs
docs:
	@echo "$(BOLD)Building Sphinx documentation$(RESET)"
	@cd docs; make html
	@echo "$(BOLD)Done!$(RESET)"
