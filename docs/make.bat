@REM Minimal batch file for Sphinx documentation
#

@REM You can set these variables from the command line, and also
@REM from the environment for the first two.
set SPHINXOPTS    ?=
set SPHINXBUILD   ?= sphinx-build
set SOURCEDIR     = .
set BUILDDIR      = _build/html

@REM Put it first so that "make" without argument is like "make help".
help:
    %SPHINXBUILD% -M help "$(SOURCEDIR)" "$(BUILDDIR)" %SPHINXOPTS% %O%

html:
    %SPHINXBUILD% -b html $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"

clean:
    rmdir /s /q "$(BUILDDIR)"\*

.PHONY: help html clean
