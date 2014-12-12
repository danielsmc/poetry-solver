# Poetry-Solver

Given a text corpus and a poem schema (meter & rhyme), generates poems that fit the schema and ape the corpus. Inspired by [Ross Goodwin's Poetizer](https://github.com/rossgoodwin/poetizer).

## Usage
Poetry-solver is built for Python 2.7, and has no dependencies outside stdlib. You'll need a copy of the [CMU Pronouncing Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) or a similar dictionary in a compatable format.

    usage: poetry_solver.py [-h] [-v] [--corpus CORPUS] [--pdict PDICT]
                            [--schema SCHEMA] [--lookback LOOKBACK] [-n N]

    optional arguments:
      -h, --help           show this help message and exit
      -v                   verbose
      --corpus CORPUS      input corpus path
      --pdict PDICT        pronunciation dictionary path
      --schema SCHEMA      poem schema path
      --lookback LOOKBACK  number of words to look back
      -n N                 number of poems to generate

## TODO:
* A better language model
* More scrutable data structures
* Can be very slow to back out of blind alleys
