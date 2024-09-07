#!/bin/bash
pyinstaller --onefile -n rephile rephile/__main__.py && cp dist/rephile ~/sync/bin/
