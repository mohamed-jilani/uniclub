================================================================================

    PROJET: UniClub Connect - Gestion de la Vie Associative Universitaire

================================================================================

AUTEUR: Projet de Modélisation de Base de Données
DATE: Mai 2026
SGBD: PostgreSQL 15+

lien video : https://www.youtube.com/watch?v=715aP93wlq4

================================================================================

1. DESCRIPTION DU PROJET

================================================================================

UniClub Connect est une plateforme de gestion de la vie associative 
universitaire permettant:

- Aux étudiants et professeurs de s'inscrire
- De créer des clubs (sport, culture, science, etc.)
- D'organiser des événements (conférences et ateliers)
- Aux membres de participer aux événements

================================================================================

2. PRÉREQUIS SYSTÈME

================================================================================

Logiciels nécessaires:
- PostgreSQL 15 ou supérieur
- psql (client PostgreSQL en ligne de commande)

Vérifier l'installation:
    psql --version

Si PostgreSQL n'est pas installé:
- Ubuntu/Debian: sudo apt install postgresql postgresql-client
- macOS: brew install postgresql
- Windows: Télécharger depuis https://www.postgresql.org/download/

================================================================================

3. STRUCTURE DES FICHIERS

================================================================================

UniClub_Connect/
├── README.txt                          (ce fichier)
├── create_tables.sql                   (création des tables)
├── insert_data.sql                     (insertion des données)
├── Rapport_UniClub_Connect.pdf         (rapport complet du projet)
└── video_demonstration.mp4             (vidéo de démonstration)

================================================================================

4. INSTALLATION ET EXÉCUTION

================================================================================

Étape 1: Créer une base de données
-----------------------------------
sudo -u postgres psql
CREATE DATABASE uniclub_db;
CREATE USER uniclub_user WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE uniclub_db TO uniclub_user;
\q

Étape 2: Se connecter à la base de données
-------------------------------------------
psql -U uniclub_user -d uniclub_db -h localhost

(Si demandé, entrer le mot de passe: password123)

Étape 3: Exécuter le script de création des tables
---------------------------------------------------
\i create_tables.sql

ou depuis le terminal:
psql -U uniclub_user -d uniclub_db -h localhost -f create_tables.sql

Étape 4: Insérer les données d'exemple
---------------------------------------
\i insert_data.sql

ou depuis le terminal:
psql -U uniclub_user -d uniclub_db -h localhost -f insert_data.sql

================================================================================

5. VÉRIFICATION DE L'INSTALLATION

================================================================================

Une fois connecté à la base (psql -U uniclub_user -d uniclub_db):

-- Lister toutes les tables
\dt

-- Afficher le nombre de tuples par table
SELECT 'Membre' AS table_name, COUNT(*) AS nb_tuples FROM Membre
UNION ALL
SELECT 'Club', COUNT(*) FROM Club
UNION ALL
SELECT 'Evenement', COUNT(*) FROM Evenement
UNION ALL
SELECT 'Conference', COUNT(*) FROM Conference
UNION ALL
SELECT 'Atelier', COUNT(*) FROM Atelier
UNION ALL
SELECT 'Adhere', COUNT(*) FROM Adhere
UNION ALL
SELECT 'Participe', COUNT(*) FROM Participe;

-- Vous devriez obtenir au moins 5 tuples par table

================================================================================

6. REQUÊTES D'EXEMPLE

================================================================================

-- Afficher tous les clubs validés
SELECT * FROM Club WHERE statut_validation = 'valide';

-- Afficher les événements avec leur type (conférence ou atelier)
SELECT e.titre, e.date_evenement, e.lieu,
       CASE 
           WHEN c.id_evenement IS NOT NULL THEN 'Conference'
           WHEN a.id_evenement IS NOT NULL THEN 'Atelier'
       END AS type_evenement
FROM Evenement e
LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
LEFT JOIN Atelier a ON e.id_evenement = a.id_evenement;

-- Lister les membres d'un club avec leurs rôles
SELECT m.nom, m.prenom, m.email, ad.role_dans_club, c.nom AS nom_club
FROM Membre m
JOIN Adhere ad ON m.id_membre = ad.id_membre
JOIN Club c ON ad.id_club = c.id_club
WHERE c.id_club = 1
ORDER BY ad.role_dans_club;

-- Participants à un événement
SELECT m.nom, m.prenom, p.date_inscription, p.present, e.titre
FROM Membre m
JOIN Participe p ON m.id_membre = p.id_membre
JOIN Evenement e ON p.id_evenement = e.id_evenement
WHERE e.id_evenement = 1;

-- Statistiques: nombre d'événements par club
SELECT c.nom, COUNT(e.id_evenement) AS nb_evenements
FROM Club c
LEFT JOIN Evenement e ON c.id_club = e.id_club_organisateur
GROUP BY c.id_club, c.nom
ORDER BY nb_evenements DESC;

================================================================================

7. CONTRAINTES IMPLÉMENTÉES

================================================================================

Clés primaires:
- Membre(id_membre)
- Club(id_club)
- Evenement(id_evenement)
- Conference(id_evenement)
- Atelier(id_evenement)
- Adhere(id_membre, id_club)
- Participe(id_membre, id_evenement)

Clés étrangères:
- Club.id_fondateur → Membre.id_membre
- Evenement.id_club_organisateur → Club.id_club
- Conference.id_evenement → Evenement.id_evenement
- Atelier.id_evenement → Evenement.id_evenement
- Adhere.id_membre → Membre.id_membre
- Adhere.id_club → Club.id_club
- Participe.id_membre → Membre.id_membre
- Participe.id_evenement → Evenement.id_evenement

Contraintes CHECK:
- Membre.statut IN ('etudiant', 'professeur')
- Club.statut_validation IN ('en_attente', 'valide', 'refuse')
- Conference.capacite_max > 0
- Atelier.nb_postes >= 1
- Atelier.niveau_requis IN ('debutant', 'intermediaire', 'avance')
- Adhere.role_dans_club IN ('membre', 'president', 'tresorier', 'secretaire')

Contraintes UNIQUE:
- Membre.email
- Club.nom

================================================================================

8. SCHEMA RELATIONNEL

================================================================================

Membre(id_membre PK, nom, prenom, email UNIQUE, statut)
Club(id_club PK, nom UNIQUE, thematique, date_creation, statut_validation, 
     id_fondateur FK→Membre)
Evenement(id_evenement PK, titre, date_evenement, duree, lieu, 
          id_club_organisateur FK→Club)
Conference(id_evenement PK FK→Evenement, intervenant, support, capacite_max)
Atelier(id_evenement PK FK→Evenement, nb_postes, materiel, niveau_requis)
Adhere(id_membre FK→Membre, id_club FK→Club, date_adhesion, role_dans_club,
       PK=(id_membre, id_club))
Participe(id_membre FK→Membre, id_evenement FK→Evenement, date_inscription,
          present, PK=(id_membre, id_evenement))

Total: 7 relations (> 5 requis)

================================================================================

9. SUPPORT ET CONTACT

================================================================================

Pour toute question concernant ce projet:
- Consulter le rapport PDF complet
- Visionner la vidéo de démonstration
- Contacter l'auteur du projet

================================================================================

10. NOTES IMPORTANTES

================================================================================

- La spécialisation Evenement → {Conference, Atelier} est TOTALE et DISJOINTE
- Un membre ne peut pas s'inscrire deux fois au même événement (PK de Participe)
- Le schéma est en BCNF (Boyce-Codd Normal Form)
- Toutes les contraintes métier sont respectées
- Les données d'exemple respectent toutes les contraintes d'intégrité

================================================================================

FIN DU README

================================================================================
