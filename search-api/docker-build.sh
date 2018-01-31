#!/bin/bash

echo 'compile && pack'
docker build -t star-search-gradle -f Dockerfile-gradle .
docker run --rm -v ${PWD}:/usr/src/app star-search-gradle

echo 'docker build && push'
datetime_str=`date +%Y%m%d%H%M`
docker build -t registry.cn-hangzhou.aliyuncs.com/kanjian/star-search-api:$datetime_str .
docker push registry.cn-hangzhou.aliyuncs.com/kanjian/star-search-api:$datetime_str
