#!/bin/bash

# $1 must be the path of the solution / repository
# $2 must be the path to git repo

cd "$1" || exit

git init
git branch -m "main"
git add .
git commit -m "initial commit"

if [ $# -eq 2 ]
  then
    git remote add origin $2
    git push origin main
fi