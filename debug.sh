#!/bin/bash

. project.cfg

if [ -f python/.env ]; then
  set -o allexport; source python/.env; set +o allexport
fi

debug_name="debug-$name"
docker stop "$debug_name" > /dev/null 2>&1
docker rm -f "$debug_name" > /dev/null 2>&1

docker run -it \
  --name="$debug_name" \
  --entrypoint='' \
  --env DISCORD_TOKEN \
  "$repo":latest \
  bash

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
