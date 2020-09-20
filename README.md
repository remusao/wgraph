# wgraph

See what it can do: https://remusao.github.io/posts/wiktionary-etymology-exploration.html

Etymological graphs based on Wiktionary dumps. Extract Etymological relations
between words from Etymology sections of Wiktionary dumps. Multiple languages
are supported (currently `en` and `fr`) and the extraction process should be
relatively fast (e.g.: extracting all etymological references from the `5.2GB`
English Wiktionary dumps takes ~2 minutes).

Some use-cases:
* Distance between two words in the graph ("w-distance")
* Display etymological neighborhood of a word (potentially combining multiple
  editions of Wiktionary: e.g. `en` + `fr`)
* Find the closest word in `lang1` from `w` in `lang2` (e.g.: What's the closest
  English word from German word `Buch`?)
