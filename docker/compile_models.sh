#!/bin/sh
if [ $# -eq 1 ] 
then
    echo "Runs the release container"
    echo "Please, provide one folder which contains models to process as script argument"
    echo "Only an absolute path is supported at the moment"
    export INPUT=$1
    MOUNTED=/$(basename $INPUT)
    echo "Uses model folder: " $INPUT
    echo "Uses module name: " $MOUNTED
    echo "Docker command: docker run -v "$INPUT":/"$MOUNTED" --entrypoint=java nestml_release -jar /data/nestml.jar "$MOUNTED" --target "$MOUNTED"/build"
    docker run -v $INPUT:$MOUNTED --entrypoint=java nestml_release -jar /data/nestml.jar $MOUNTED --target $MOUNTED/build
else
    echo "Invalid arguments. Please pass only one argument pointing to the model fodler."
fi
