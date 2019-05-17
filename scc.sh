#!/bin/sh
scc . --exclude-dir="build,dist,ts-boilerplate,htmlcov,js,notebooks,.git,.tox,.idea,*.egg-info,.pytest_cache"
