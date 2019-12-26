#!/bin/bash

for i in {844..847} ; do wget https://community.wanikani.com/posts/1085304/revisions/${i}.json -P raw/; done
