#!/bin/sh
scc . --exclude-dir="build,ts-boilerplate,htmlcov,dist,js,notebooks,.git,.tox,.idea,*.egg-info,.pytest_cache"
