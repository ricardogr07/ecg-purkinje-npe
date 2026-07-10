# Makefile for the technical manuscript.
# Markdown is the source of truth; the PDF is a rendering.
#
# Requires: pandoc (>= 3) and a PDF engine. This project renders with typst
# (a single self-contained binary, no LaTeX distribution needed):
#   pandoc + typst both install from conda-forge.
# To use a LaTeX engine instead, set PDF_ENGINE=xelatex (requires a TeX install).

PANDOC     ?= pandoc
PDF_ENGINE ?= typst
CSL        ?= vancouver.csl
BIB        ?= refs.bib
SRC        ?= manuscript.md
OUT        ?= technical-writeup.pdf

.PHONY: all pdf clean

all: pdf

pdf: $(OUT)

$(OUT): $(SRC) $(BIB) $(CSL)
	$(PANDOC) $(SRC) \
	  --citeproc --bibliography=$(BIB) \
	  --csl=$(CSL) \
	  --number-sections \
	  --pdf-engine=$(PDF_ENGINE) \
	  -o $(OUT)

clean:
	rm -f $(OUT)
