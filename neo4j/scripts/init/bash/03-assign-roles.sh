#!/bin/bash
set -euo pipefail
trap 'echo "❌ Error in $(basename "$0") on line $LINENO"; exit 1' ERR

ROLES_FILE="/run/secrets/neo4j_user_roles.secret"

# Get Neo4j edition string
edition=$(cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" --format plain --delimiter "" \
  "CALL dbms.components() YIELD name, edition RETURN edition LIMIT 1;")

if [[ ! "$edition" =~ [Ee]nterprise ]]; then
  echo "⚠️ Warning: Neo4j edition is '$edition'. Role management is only supported on Enterprise Edition. Skipping role assignment."
  exit 0
fi

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
