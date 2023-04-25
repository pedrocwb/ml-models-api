#!/bin/bash

find . -name "*.yaml" -exec kubectl apply -f {} \;

