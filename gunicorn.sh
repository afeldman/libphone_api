#!/bin/sh

gunicorn --chdir app main:app -w 2 --threads 4 -b 0.0.0.0:8003
