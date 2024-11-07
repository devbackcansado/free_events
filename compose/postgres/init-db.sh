#!/bin/bash

# Variáveis de configuração
DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="free_events"

# Criar o banco de dados
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE IF NOT EXISTS $DB_NAME;
    CREATE USER IF NOT EXISTS $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL

echo "Banco de dados $DB_NAME e usuário $DB_USER criados com sucesso."
