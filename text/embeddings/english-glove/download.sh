#!/bin/bash

url=http://nlp.stanford.edu/data/glove.6B.zip

echo "Downloading GloVE from $url"

wget $url && \
  unzip *.zip && \
  rm *.zip

echo "Done!"
