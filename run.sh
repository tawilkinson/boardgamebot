#!/bin/bash

. project.cfg

docker run --rm -d \
  --name="$name" \
  "$repo":latest \
  $@

# Some "docker run" options for quick reference:
#  --env VARIABLE=value
#  --publish, -p HOST_PORT:CONTAINER_PORT
#  --volume=[HOST_PATH|NAMED_VOLUME]:DEST_PATH[:ro]
#  --mount type=bind,source=HOST_PATH,destination=DEST_PATH[,readonly]
#  --mount type=volume[,source=NAMED_VOLUME],destination=DEST_PATH[,readonly]
#  --mount type=tmpfs,destination=DEST_PATH
#
# NB:
#  - Volume will create DEST_PATH if it doesn't already exist
#  - Mount and Volume require absolute paths, and cannot deal with symlinks
