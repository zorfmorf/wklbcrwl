#!/bin/bash

for i in {832..833} ; do wget https://community.wanikani.com/posts/1085304/revisions/${i}.json -P raw/; done

