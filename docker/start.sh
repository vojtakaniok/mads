#!/bin/bash

# Start the first process
jupyter lab --ip 0.0.0.0 &

# Start the second process
xpra start :10 --start-child=./ns-allinone-3.39/netanim-3.109/NetAnim --bind-tcp=0.0.0.0:10000 --exit-with-children 

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?