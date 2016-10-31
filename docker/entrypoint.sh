#!/bin/ash

# Create a dummy user with correct uid
adduser -s /bin/bash -u $UID -D nestml

# run the NESTML jar under the dummy user's account
exec sudo -u nestml java -jar /data/nestml/target/nestml.jar "$@"
