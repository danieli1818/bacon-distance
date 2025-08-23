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
INIT_SCRIPTS_DIR="/init/scripts/bash"
LOCK_FILE="/data/.init_done"

# Start the original Neo4j entrypoint (background)
/startup/docker-entrypoint.sh neo4j &
NEO4J_PID=$!

# Function to check if the Neo4j process is still alive
is_neo4j_alive() {
  kill -0 "$NEO4J_PID" 2>/dev/null
}

# Wait for Neo4j to be ready, but also exit if Neo4j crashes
echo "Waiting for Neo4j to accept connections..."
while ! cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1;" >/dev/null 2>&1; do
  if ! is_neo4j_alive; then
    echo "❌ Neo4j process exited unexpectedly during startup."
    exit 1
  fi
  sleep 1
done

echo "✅ Neo4j is up. Running Cypher init scripts..."

# Prevent re-running init by checking a lock file
if [ -f "$LOCK_FILE" ]; then
  echo "Initialization already completed. Skipping init scripts."
else
  echo "Running initialization scripts..."

  for script in "$INIT_SCRIPTS_DIR"/*.sh; do
    [ -e "$script" ] || continue

    logfile="/tmp/$(basename "$script").log"
    echo "Running $script, logging to $logfile..."

    if ! bash "$script" >"$logfile" 2>&1; then
      echo "❌ Script $script failed. See log below:"
      cat "$logfile"
      exit 1
    fi

  done

  # Mark init done
  touch "$LOCK_FILE"
  echo "Initialization complete."
fi

# Wait for Neo4j process to exit (foreground it)
wait "$NEO4J_PID"
