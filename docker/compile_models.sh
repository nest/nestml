#!/bin/sh

if [ $# -ne 1 ]; then
    echo "Error: wrong number of arguments."
    echo "Usage: $0 <dir>"
    exit 1
fi

if [ ! -d $1 ]; then
    echo "Error: '$1' is not a directory."
    echo "Usage: $0 <dir>"
    exit 1
fi

echo "Executing the NESTML release container"

hostpath=`cd $1; pwd`
mountpath=`basename $hostpath`

uid=`id -u`
volume="$hostpath:/$mountpath"
docker_img="nestml_release"

echo "Running docker image $docker_img"
echo "  Volume : $volume"
echo "  User ID: $uid"

cmd="docker run -v $volume -e UID=$uid $docker_img /$mountpath --target /$mountpath/build"

echo $cmd
