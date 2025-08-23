#!/bin/bash
set -euo pipefail
trap 'echo "❌ Error in $(basename "$0") on line $LINENO"; exit 1' ERR

if [[ ! "$NEO4J_EDITION" =~ [Ee]nterprise ]]; then
  echo "⚠️ Warning: Neo4j edition is '$NEO4J_EDITION'. Role management is only supported on Enterprise Edition. Skipping role assignment."
  exit 0
fi

# Read password from Docker secret file
AUTH_FILE="/run/secrets/neo4j_auth.secret"
if [ ! -f "$AUTH_FILE" ]; then
  echo "❌ Auth secret file not found at $AUTH_FILE"
  exit 1
fi

NEO4J_USER=$(cut -d'/' -f1 < "$AUTH_FILE")
NEO4J_PASSWORD=$(cut -d'/' -f2 < "$AUTH_FILE")

ROLES_FILE="/run/secrets/neo4j_user_roles.secret"

commands=""

while IFS=':' read -r username roles; do
  [[ -z "$username" || "$username" =~ ^# ]] && continue

  echo "Processing roles for user: $username"

  IFS=',' read -ra role_array <<< "$roles"
  for role in "${role_array[@]}"; do
    commands+="GRANT ROLE $role TO $username;\n"
  done
done < "$ROLES_FILE"

echo -e "$commands" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD"
