#!/bin/sh
export PYTHONPATH="${PYTHONPATH}:${CKTSYNC_DIR}/pysrc"
$CKTSYNC_PYBIN $CKTSYNC_DIR/share/cds/pysrc/cdsclient.py "$@"
