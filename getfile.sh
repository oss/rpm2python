#!/bin/bash

rm -r getfile/*
wget -P getfile $1
(cd getfile && rpm2cpio *.rpm | cpio -idmv)
