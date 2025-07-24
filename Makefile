.PHONY: all clean input output

all: clean input output set-permissions set-timestamps

include tools/charfreq-tools/common.mk

INPUT := input/Keystrokes.zip
ORDERS := 1
OUTPUT_NGRAMS_NC := $(foreach N,$(ORDERS),output/$(N)-grams.tsv)
OUTPUT_NGRAMS_UC := $(foreach N,$(ORDERS),output/$(N)-grams-uc.tsv)
OUTPUT_NGRAMS := $(OUTPUT_NGRAMS_NC) $(OUTPUT_NGRAMS_UC)
OUTPUT_NGRAMS_WITH_C_AND_P := $(OUTPUT_NGRAMS:%.tsv=%-with-c-and-p.tsv)
OUTPUT := output/dfko.tsv $(OUTPUT_NGRAMS) $(OUTPUT_NGRAMS_WITH_C_AND_P)
PATTERNS := _keystrokes.txt$$

clean: clean-output clean-venv

input: $(INPUT)

$(INPUT): | input-dir
	curl -L -o $@ https://userinterfaces.aalto.fi/136Mkeystrokes/data/Keystrokes.zip

output: $(OUTPUT)

output/dfko.tsv $(OUTPUT_NGRAMS): $(INPUT) | output-dir
	uv run tools/dfko.py \
		$(INPUT) \
		output/ \
		$(foreach pattern,$(PATTERNS),'$(pattern)')

output/%-with-c-and-p.tsv: output/%.tsv
	tools/charfreq-tools/append-c-and-p 2 < $< > $@
