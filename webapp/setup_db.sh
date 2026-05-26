#!/bin/bash
# Script de configuration de la base de données UniClub Connect
# Exécuter avec : bash setup_db.sh

echo "=== Configuration de la base de données UniClub Connect ==="

echo "Création de l'utilisateur et de la base..."
sudo -u postgres psql <<EOF
-- Créer l'utilisateur s'il n'existe pas
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'uniclub_user') THEN
        CREATE USER uniclub_user WITH PASSWORD 'password123';
    ELSE
        ALTER USER uniclub_user WITH PASSWORD 'password123';
    END IF;
END
\$\$;

-- Créer la base si elle n'existe pas
SELECT 'CREATE DATABASE uniclub_db OWNER uniclub_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'uniclub_db')\gexec

-- Accorder les droits
GRANT ALL PRIVILEGES ON DATABASE uniclub_db TO uniclub_user;
EOF

echo "Création des tables..."
psql -U uniclub_user -d uniclub_db -h localhost -f ../create_tables.sql

echo "Insertion des données..."
psql -U uniclub_user -d uniclub_db -h localhost -f ../insert_data.sql

echo ""
echo "=== Configuration terminée ! ==="
echo "Vous pouvez maintenant lancer l'application avec :"
echo "  cd webapp && source venv/bin/activate && python app.py"
