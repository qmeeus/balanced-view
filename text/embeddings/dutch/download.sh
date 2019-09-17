#!/bin/bash

url=http://www.clips.uantwerpen.be/dutchembeddings/roularta-320.tar.gz

echo "Downloading dutch embeddings from $url"
wget $url && \
  tar --gzip -xvf *.tar.gz && \
  mv 320/* ./ && \
  rm *.tar.gz && \
  rm -r 320

echo "Done!"
