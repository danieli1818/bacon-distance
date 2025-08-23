#!/bin/bash
set -euo pipefail
trap 'echo "❌ Error in $(basename "$0") on line $LINENO"; exit 1' ERR

PASSWORDS_FILE="/run/secrets/user_passwords.secret"

commands=""

while IFS=':' read -r username password_hash; do
  [[ -z "$username" || "$username" =~ ^# ]] && continue

  echo "Processing user: $username"
  commands+="CREATE USER $username IF NOT EXISTS SET ENCRYPTED PASSWORD '$password_hash' CHANGE NOT REQUIRED;\n"
done < "$PASSWORDS_FILE"

echo -e "$commands" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD"
