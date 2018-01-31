#!/bin/bash
set -e

rm -rf /usr/local/tomcat/webapps/ROOT

exec $@
