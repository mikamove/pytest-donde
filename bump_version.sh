#!/bin/bash

PART=$1 # major, minor, patch

bump2version --verbose "$1" && echo "bump2version done, see differences:" && git show -1
