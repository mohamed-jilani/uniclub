-- ============================================================================
-- Projet: UniClub Connect - Gestion de la vie associative universitaire
-- Script d'insertion des données d'exemple
-- SGBD: PostgreSQL 15+
-- ============================================================================

-- ============================================================================
-- INSERTION: Membre
-- Au moins 5 membres (étudiants et professeurs)
-- ============================================================================
INSERT INTO Membre (nom, prenom, email, statut) VALUES
('Dupont', 'Alice', 'alice.dupont@univ.fr', 'etudiant'),
('Martin', 'Bob', 'bob.martin@univ.fr', 'etudiant'),
('Durand', 'Clara', 'clara.durand@univ.fr', 'professeur'),
('Lefevre', 'David', 'david.lefevre@univ.fr', 'etudiant'),
('Roux', 'Emma', 'emma.roux@univ.fr', 'etudiant'),
('Bernard', 'François', 'francois.bernard@univ.fr', 'professeur'),
('Petit', 'Gabrielle', 'gabrielle.petit@univ.fr', 'etudiant'),
('Moreau', 'Hugo', 'hugo.moreau@univ.fr', 'etudiant');

-- ============================================================================
-- INSERTION: Club
-- Au moins 5 clubs avec différentes thématiques et statuts
-- ============================================================================
INSERT INTO Club (nom, thematique, date_creation, statut_validation, id_fondateur) VALUES
('Club Robotique', 'Technologie', '2024-09-01', 'valide', 1),
('Théâtre Universitaire', 'Culture', '2024-09-10', 'valide', 2),
('Eco Campus', 'Environnement', '2024-09-15', 'en_attente', 4),
('Débats & Philosophie', 'Sciences Humaines', '2024-10-01', 'valide', 3),
('Sport Extrême', 'Sport', '2024-10-05', 'refuse', 5),
('Club Photo', 'Art', '2024-10-10', 'valide', 7),
('Code & Innovation', 'Informatique', '2024-10-20', 'valide', 8);

-- ============================================================================
-- INSERTION: Evenement
-- Au moins 5 événements organisés par différents clubs
-- ============================================================================
INSERT INTO Evenement (titre, date_evenement, duree, lieu, id_club_organisateur) VALUES
('Conférence sur l''Intelligence Artificielle', '2025-02-10', '02:00:00', 'Amphithéâtre A', 1),
('Atelier Soudure Électronique', '2025-02-15', '03:00:00', 'Laboratoire Électronique', 1),
('Pièce de théâtre: Candide', '2025-03-01', '01:30:00', 'Salle des Fêtes', 2),
('Débat: Changement Climatique', '2025-03-20', '01:00:00', 'Salle B12', 4),
('Conférence Véganisme et Santé', '2025-04-05', '02:00:00', 'Amphithéâtre C', 3),
('Atelier Programmation Python', '2025-04-10', '04:00:00', 'Salle Informatique 101', 7),
('Conférence Cybersécurité', '2025-04-15', '02:30:00', 'Amphithéâtre B', 7);

-- ============================================================================
-- INSERTION: Conference
-- Événements de type conférence (id_evenement 1, 5, 7)
-- ============================================================================
INSERT INTO Conference (id_evenement, intervenant, support, capacite_max) VALUES
(1, 'Dr. Sophie Germain', 'PDF', 150),
(5, 'Jean-Marc Jancovici', 'PPTX', 200),
(7, 'Kevin Mitnick Jr.', 'PDF', 120);

-- ============================================================================
-- INSERTION: Atelier
-- Événements de type atelier (id_evenement 2, 6)
-- ============================================================================
INSERT INTO Atelier (id_evenement, nb_postes, materiel, niveau_requis) VALUES
(2, 10, 'fer à souder, multimètre, breadboard, composants électroniques', 'intermediaire'),
(6, 20, 'ordinateurs avec Python 3.11, IDE PyCharm', 'debutant');

-- ============================================================================
-- INSERTION: Adhere
-- Au moins 5 adhésions avec différents rôles
-- ============================================================================
INSERT INTO Adhere (id_membre, id_club, date_adhesion, role_dans_club) VALUES
-- Club Robotique (id_club = 1)
(1, 1, '2024-09-02', 'president'),
(2, 1, '2024-09-03', 'tresorier'),
(5, 1, '2024-09-05', 'membre'),
-- Théâtre Universitaire (id_club = 2)
(2, 2, '2024-09-12', 'secretaire'),
(5, 2, '2024-09-13', 'membre'),
(1, 2, '2024-10-01', 'membre'),
-- Eco Campus (id_club = 3)
(4, 3, '2024-09-16', 'president'),
(6, 3, '2024-09-17', 'membre'),
-- Débats & Philosophie (id_club = 4)
(3, 4, '2024-10-02', 'president'),
(7, 4, '2024-10-03', 'membre'),
-- Code & Innovation (id_club = 7)
(8, 7, '2024-10-21', 'president'),
(1, 7, '2024-10-22', 'membre'),
(4, 7, '2024-10-23', 'tresorier');

-- ============================================================================
-- INSERTION: Participe
-- Au moins 5 participations à des événements
-- ============================================================================
INSERT INTO Participe (id_membre, id_evenement, date_inscription, present) VALUES
-- Conférence IA (id_evenement = 1)
(1, 1, '2025-01-15 10:00:00', TRUE),
(2, 1, '2025-01-16 14:30:00', TRUE),
(3, 1, '2025-01-17 09:00:00', FALSE),
(4, 1, '2025-01-18 11:00:00', TRUE),
-- Atelier Soudure (id_evenement = 2)
(4, 2, '2025-02-01 08:00:00', TRUE),
(5, 2, '2025-02-02 10:00:00', TRUE),
-- Pièce de théâtre (id_evenement = 3)
(5, 3, '2025-02-20 15:00:00', TRUE),
(1, 3, '2025-02-21 16:00:00', TRUE),
-- Débat Climat (id_evenement = 4)
(1, 4, '2025-03-10 12:00:00', TRUE),
(3, 4, '2025-03-11 13:00:00', TRUE),
(7, 4, '2025-03-12 14:00:00', FALSE),
-- Conférence Véganisme (id_evenement = 5)
(2, 5, '2025-03-25 10:00:00', TRUE),
(6, 5, '2025-03-26 11:00:00', TRUE),
-- Atelier Python (id_evenement = 6)
(8, 6, '2025-04-01 09:00:00', FALSE),
(1, 6, '2025-04-02 10:00:00', FALSE);

-- ============================================================================
-- VÉRIFICATION: Affichage des données insérées
-- ============================================================================

-- Nombre de tuples par table
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

-- ============================================================================
-- FIN DU SCRIPT D'INSERTION
-- ============================================================================
