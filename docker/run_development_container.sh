export VAR=$1
echo $VAR
docker run -v $VAR:$VAR --entrypoint=java nestml_development -jar /data/nestml/target/nestml.jar $VAR --target $VAR/build