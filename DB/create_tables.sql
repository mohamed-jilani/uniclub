-- ============================================================================
-- Projet: UniClub Connect - Gestion de la vie associative universitaire
-- Auteur: Projet de Modélisation de Base de Données
-- SGBD: PostgreSQL 15+
-- Description: Script de création des tables
-- ============================================================================

-- Suppression des tables existantes (dans l'ordre inverse des dépendances)
DROP TABLE IF EXISTS Participe CASCADE;
DROP TABLE IF EXISTS Adhere CASCADE;
DROP TABLE IF EXISTS Atelier CASCADE;
DROP TABLE IF EXISTS Conference CASCADE;
DROP TABLE IF EXISTS Evenement CASCADE;
DROP TABLE IF EXISTS Club CASCADE;
DROP TABLE IF EXISTS Membre CASCADE;

-- ============================================================================
-- TABLE: Membre
-- Description: Représente les étudiants et professeurs de l'université
-- ============================================================================
CREATE TABLE Membre (
    id_membre SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('etudiant', 'professeur'))
);

COMMENT ON TABLE Membre IS 'Table des membres (étudiants et professeurs)';
COMMENT ON COLUMN Membre.id_membre IS 'Identifiant unique du membre';
COMMENT ON COLUMN Membre.email IS 'Email unique du membre';
COMMENT ON COLUMN Membre.statut IS 'Statut: etudiant ou professeur';

-- ============================================================================
-- TABLE: Club
-- Description: Représente les clubs universitaires (sport, culture, science)
-- ============================================================================
CREATE TABLE Club (
    id_club SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    thematique VARCHAR(100) NOT NULL,
    date_creation DATE NOT NULL DEFAULT CURRENT_DATE,
    statut_validation VARCHAR(20) NOT NULL DEFAULT 'en_attente' 
        CHECK (statut_validation IN ('en_attente', 'valide', 'refuse')),
    id_fondateur INT NOT NULL,
    FOREIGN KEY (id_fondateur) REFERENCES Membre(id_membre) ON DELETE RESTRICT
);

COMMENT ON TABLE Club IS 'Table des clubs universitaires';
COMMENT ON COLUMN Club.nom IS 'Nom unique du club';
COMMENT ON COLUMN Club.statut_validation IS 'Statut de validation: en_attente, valide, refuse';
COMMENT ON COLUMN Club.id_fondateur IS 'Référence au membre fondateur du club';

-- ============================================================================
-- TABLE: Evenement
-- Description: Représente les événements organisés par les clubs
-- ============================================================================
CREATE TABLE Evenement (
    id_evenement SERIAL PRIMARY KEY,
    titre VARCHAR(150) NOT NULL,
    date_evenement DATE NOT NULL,
    duree INTERVAL NOT NULL,
    lieu VARCHAR(100) NOT NULL,
    id_club_organisateur INT NOT NULL,
    FOREIGN KEY (id_club_organisateur) REFERENCES Club(id_club) ON DELETE CASCADE
);

COMMENT ON TABLE Evenement IS 'Table des événements organisés par les clubs';
COMMENT ON COLUMN Evenement.duree IS 'Durée de l''événement (format INTERVAL)';
COMMENT ON COLUMN Evenement.id_club_organisateur IS 'Référence au club organisateur';

-- ============================================================================
-- TABLE: Conference
-- Description: Spécialisation d'Événement - Conférences avec intervenant
-- ============================================================================
CREATE TABLE Conference (
    id_evenement INT PRIMARY KEY,
    intervenant VARCHAR(100) NOT NULL,
    support VARCHAR(50) CHECK (support IN ('PDF', 'PPT', 'PPTX', 'Autre')),
    capacite_max INT CHECK (capacite_max > 0),
    FOREIGN KEY (id_evenement) REFERENCES Evenement(id_evenement) ON DELETE CASCADE
);

COMMENT ON TABLE Conference IS 'Spécialisation d''Evenement: conférences';
COMMENT ON COLUMN Conference.intervenant IS 'Nom de l''intervenant extérieur';
COMMENT ON COLUMN Conference.support IS 'Type de support de présentation';
COMMENT ON COLUMN Conference.capacite_max IS 'Capacité maximale de l''auditorium';

-- ============================================================================
-- TABLE: Atelier
-- Description: Spécialisation d'Événement - Ateliers pratiques
-- ============================================================================
CREATE TABLE Atelier (
    id_evenement INT PRIMARY KEY,
    nb_postes INT NOT NULL CHECK (nb_postes >= 1),
    materiel TEXT,
    niveau_requis VARCHAR(20) NOT NULL 
        CHECK (niveau_requis IN ('debutant', 'intermediaire', 'avance')),
    FOREIGN KEY (id_evenement) REFERENCES Evenement(id_evenement) ON DELETE CASCADE
);

COMMENT ON TABLE Atelier IS 'Spécialisation d''Evenement: ateliers pratiques';
COMMENT ON COLUMN Atelier.nb_postes IS 'Nombre de postes de travail disponibles';
COMMENT ON COLUMN Atelier.materiel IS 'Liste du matériel requis';
COMMENT ON COLUMN Atelier.niveau_requis IS 'Niveau requis: debutant, intermediaire, avance';

-- ============================================================================
-- TABLE: Adhere
-- Description: Association N:N entre Membre et Club (adhésion)
-- ============================================================================
CREATE TABLE Adhere (
    id_membre INT NOT NULL,
    id_club INT NOT NULL,
    date_adhesion DATE NOT NULL DEFAULT CURRENT_DATE,
    role_dans_club VARCHAR(50) NOT NULL 
        CHECK (role_dans_club IN ('membre', 'president', 'tresorier', 'secretaire')),
    PRIMARY KEY (id_membre, id_club),
    FOREIGN KEY (id_membre) REFERENCES Membre(id_membre) ON DELETE CASCADE,
    FOREIGN KEY (id_club) REFERENCES Club(id_club) ON DELETE CASCADE
);

COMMENT ON TABLE Adhere IS 'Association entre membres et clubs (adhésions)';
COMMENT ON COLUMN Adhere.role_dans_club IS 'Rôle: membre, president, tresorier, secretaire';

-- ============================================================================
-- TABLE: Participe
-- Description: Association N:N entre Membre et Evenement (participation)
-- ============================================================================
CREATE TABLE Participe (
    id_membre INT NOT NULL,
    id_evenement INT NOT NULL,
    date_inscription TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    present BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id_membre, id_evenement),
    FOREIGN KEY (id_membre) REFERENCES Membre(id_membre) ON DELETE CASCADE,
    FOREIGN KEY (id_evenement) REFERENCES Evenement(id_evenement) ON DELETE CASCADE
);

COMMENT ON TABLE Participe IS 'Association entre membres et événements (participations)';
COMMENT ON COLUMN Participe.present IS 'Indique si le membre était présent (vrai/faux)';

-- ============================================================================
-- INDEX pour améliorer les performances
-- ============================================================================
CREATE INDEX idx_club_statut ON Club(statut_validation);
CREATE INDEX idx_evenement_date ON Evenement(date_evenement);
CREATE INDEX idx_evenement_club ON Evenement(id_club_organisateur);
CREATE INDEX idx_adhere_membre ON Adhere(id_membre);
CREATE INDEX idx_adhere_club ON Adhere(id_club);
CREATE INDEX idx_participe_evenement ON Participe(id_evenement);

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
