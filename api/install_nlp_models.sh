#!/bin/bash

spacy_models="en_core_web_md fr_core_news_md nl_core_news_sm"
for model in $spacy_models; do
    echo "Starting download of NLP model $model"
    python -m spacy download $model
done
