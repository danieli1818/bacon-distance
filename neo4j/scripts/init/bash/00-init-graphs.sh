#!/bin/bash
set -euo pipefail
trap 'echo "❌ Error in $(basename "$0") on line $LINENO"; exit 1' ERR

# Read password from Docker secret file
AUTH_FILE="/run/secrets/neo4j_auth.secret"
if [ ! -f "$AUTH_FILE" ]; then
  echo "❌ Auth secret file not found at $AUTH_FILE"
  exit 1
fi

NEO4J_USER=$(cut -d'/' -f1 < "$AUTH_FILE")
NEO4J_PASSWORD=$(cut -d'/' -f2 < "$AUTH_FILE")

cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < "$INIT_SCRIPTS_DIR/cypher/init-bacon-distance-graph.cypher"
