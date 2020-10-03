#!/bin/bash

. project.cfg

docker build \
  --tag="$repo:latest" \
  --tag="$repo:$tag" \
  .
