#!/bin/bash

# Download the models
spacy_models="en_core_web_md fr_core_news_md nl_core_news_sm"
for model in $spacy_models; do
    echo "Starting download of NLP model $model"
    python -m spacy download $model
done

# The syntax operator is    not available by default for the Dutch language -> use english one 
LANG_DIR=/usr/local/lib/python3.6/site-packages/spacy/lang
INIT_FILE=$LANG_DIR/nl/__init__.py
cp $LANG_DIR/en/syntax_iterators.py $LANG_DIR/nl/syntax_iterators.py
perl -i -pe's/(from .lemmatizer .*?\n)/$1from .syntax_iterators import SYNTAX_ITERATORS\n/' $INIT_FILE
perl -i -pe's/(\s+stop_words = STOP_WORDS\n)/$1    syntax_iterators = SYNTAX_ITERATORS\n/' $INIT_FILE
