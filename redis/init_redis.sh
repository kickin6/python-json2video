#!/bin/sh
sysctl -w vm.overcommit_memory=1
exec "$@"
