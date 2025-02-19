#!/bin/bash

echo "Running Flake8..."
flake8 djangotelex/

echo "Running Pylint..."
pylint djangotelex/

echo "Running Radon Complexity Analysis..."
radon cc -s djangotelex/
