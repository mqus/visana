#!/usr/bin/env bash

pushd src 
python3 UI.py
popd >/dev/null
pushd ../src >/dev/null
python3 UI.py
popd >/dev/null

