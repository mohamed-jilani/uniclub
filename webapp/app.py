from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
from datetime import date

app = Flask(__name__)
app.secret_key = 'uniclub_secret_2026'

DB_CONFIG = {
    'dbname': 'uniclub_db',
    'user': 'uniclub_user',
    'password': 'password123',
    'host': 'localhost',
    'port': 5432
}

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    stats = {}
    for table in ['Membre', 'Club', 'Evenement', 'Adhere', 'Participe']:
        cur.execute(f'SELECT COUNT(*) AS n FROM {table}')
        stats[table.lower()] = cur.fetchone()['n']

    cur.execute("""
        SELECT c.nom, COUNT(e.id_evenement) AS nb_evenements
        FROM Club c
        LEFT JOIN Evenement e ON c.id_club = e.id_club_organisateur
        WHERE c.statut_validation = 'valide'
        GROUP BY c.id_club, c.nom
        ORDER BY nb_evenements DESC
        LIMIT 5
    """)
    top_clubs = cur.fetchall()

    cur.execute("""
        SELECT e.titre, e.date_evenement, e.lieu,
               CASE WHEN c.id_evenement IS NOT NULL THEN 'Conférence' ELSE 'Atelier' END AS type_ev
        FROM Evenement e
        LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
        LEFT JOIN Atelier a ON e.id_evenement = a.id_evenement
        WHERE e.date_evenement >= CURRENT_DATE
        ORDER BY e.date_evenement ASC
        LIMIT 5
    """)
    prochains = cur.fetchall()
    conn.close()
    return render_template('index.html', stats=stats, top_clubs=top_clubs, prochains=prochains)


# ── Membres ───────────────────────────────────────────────────────────────────

@app.route('/membres')
def membres():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, COUNT(DISTINCT a.id_club) AS nb_clubs, COUNT(DISTINCT p.id_evenement) AS nb_events
        FROM Membre m
        LEFT JOIN Adhere a ON m.id_membre = a.id_membre
        LEFT JOIN Participe p ON m.id_membre = p.id_membre
        GROUP BY m.id_membre
        ORDER BY m.nom, m.prenom
    """)
    membres = cur.fetchall()
    conn.close()
    return render_template('membres.html', membres=membres)

@app.route('/membres/ajouter', methods=['GET', 'POST'])
def ajouter_membre():
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip()
        statut = request.form['statut']
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Membre (nom, prenom, email, statut) VALUES (%s, %s, %s, %s)",
                (nom, prenom, email, statut)
            )
            conn.commit()
            conn.close()
            flash('Membre ajouté avec succès !', 'success')
            return redirect(url_for('membres'))
        except psycopg2.IntegrityError:
            flash("Cet email est déjà utilisé.", 'danger')
    return render_template('membre_form.html', membre=None)

@app.route('/membres/<int:id>/modifier', methods=['GET', 'POST'])
def modifier_membre(id):
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip()
        statut = request.form['statut']
        try:
            cur.execute(
                "UPDATE Membre SET nom=%s, prenom=%s, email=%s, statut=%s WHERE id_membre=%s",
                (nom, prenom, email, statut, id)
            )
            conn.commit()
            conn.close()
            flash('Membre modifié avec succès !', 'success')
            return redirect(url_for('membres'))
        except psycopg2.IntegrityError:
            flash("Cet email est déjà utilisé.", 'danger')
    cur.execute("SELECT * FROM Membre WHERE id_membre = %s", (id,))
    membre = cur.fetchone()
    conn.close()
    return render_template('membre_form.html', membre=membre)

@app.route('/membres/<int:id>/supprimer', methods=['POST'])
def supprimer_membre(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Membre WHERE id_membre = %s", (id,))
    conn.commit()
    conn.close()
    flash('Membre supprimé.', 'warning')
    return redirect(url_for('membres'))

@app.route('/membres/<int:id>')
def detail_membre(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Membre WHERE id_membre = %s", (id,))
    membre = cur.fetchone()
    cur.execute("""
        SELECT c.nom, c.thematique, a.role_dans_club, a.date_adhesion
        FROM Adhere a JOIN Club c ON a.id_club = c.id_club
        WHERE a.id_membre = %s ORDER BY a.date_adhesion DESC
    """, (id,))
    clubs = cur.fetchall()
    cur.execute("""
        SELECT e.titre, e.date_evenement, e.lieu, p.present,
               CASE WHEN c.id_evenement IS NOT NULL THEN 'Conférence' ELSE 'Atelier' END AS type_ev
        FROM Participe p
        JOIN Evenement e ON p.id_evenement = e.id_evenement
        LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
        WHERE p.id_membre = %s ORDER BY e.date_evenement DESC
    """, (id,))
    events = cur.fetchall()
    conn.close()
    return render_template('detail_membre.html', membre=membre, clubs=clubs, events=events)


# ── Clubs ─────────────────────────────────────────────────────────────────────

@app.route('/clubs')
def clubs():
    conn = get_db()
    cur = conn.cursor()
    filtre = request.args.get('statut', '')
    query = """
        SELECT c.*, m.nom || ' ' || m.prenom AS fondateur,
               COUNT(DISTINCT a.id_membre) AS nb_membres,
               COUNT(DISTINCT e.id_evenement) AS nb_events
        FROM Club c
        JOIN Membre m ON c.id_fondateur = m.id_membre
        LEFT JOIN Adhere a ON c.id_club = a.id_club
        LEFT JOIN Evenement e ON c.id_club = e.id_club_organisateur
    """
    params = []
    if filtre in ('en_attente', 'valide', 'refuse'):
        query += " WHERE c.statut_validation = %s"
        params.append(filtre)
    query += " GROUP BY c.id_club, m.nom, m.prenom ORDER BY c.date_creation DESC"
    cur.execute(query, params)
    clubs = cur.fetchall()
    conn.close()
    return render_template('clubs.html', clubs=clubs, filtre=filtre)

@app.route('/clubs/ajouter', methods=['GET', 'POST'])
def ajouter_club():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        thematique = request.form['thematique'].strip()
        id_fondateur = request.form['id_fondateur']
        try:
            cur.execute(
                "INSERT INTO Club (nom, thematique, id_fondateur) VALUES (%s, %s, %s)",
                (nom, thematique, id_fondateur)
            )
            conn.commit()
            conn.close()
            flash('Club créé et en attente de validation.', 'success')
            return redirect(url_for('clubs'))
        except psycopg2.IntegrityError:
            flash("Un club avec ce nom existe déjà.", 'danger')
    cur.execute("SELECT id_membre, nom || ' ' || prenom AS nom_complet FROM Membre ORDER BY nom")
    membres = cur.fetchall()
    conn.close()
    return render_template('club_form.html', club=None, membres=membres)

@app.route('/clubs/<int:id>/valider', methods=['POST'])
def valider_club(id):
    statut = request.form['statut']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE Club SET statut_validation = %s WHERE id_club = %s", (statut, id))
    conn.commit()
    conn.close()
    msg = {'valide': 'Club validé !', 'refuse': 'Club refusé.', 'en_attente': 'Club remis en attente.'}
    flash(msg.get(statut, 'Statut mis à jour.'), 'info')
    return redirect(url_for('clubs'))

@app.route('/clubs/<int:id>/supprimer', methods=['POST'])
def supprimer_club(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Club WHERE id_club = %s", (id,))
    conn.commit()
    conn.close()
    flash('Club supprimé.', 'warning')
    return redirect(url_for('clubs'))

@app.route('/clubs/<int:id>')
def detail_club(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*, m.nom || ' ' || m.prenom AS fondateur
        FROM Club c JOIN Membre m ON c.id_fondateur = m.id_membre
        WHERE c.id_club = %s
    """, (id,))
    club = cur.fetchone()
    cur.execute("""
        SELECT m.id_membre, m.nom, m.prenom, m.email, m.statut, a.role_dans_club, a.date_adhesion
        FROM Adhere a JOIN Membre m ON a.id_membre = m.id_membre
        WHERE a.id_club = %s ORDER BY a.role_dans_club, m.nom
    """, (id,))
    membres = cur.fetchall()
    cur.execute("""
        SELECT e.id_evenement, e.titre, e.date_evenement, e.lieu,
               CASE WHEN c.id_evenement IS NOT NULL THEN 'Conférence' ELSE 'Atelier' END AS type_ev,
               COUNT(p.id_membre) AS nb_inscrits
        FROM Evenement e
        LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
        LEFT JOIN Participe p ON e.id_evenement = p.id_evenement
        WHERE e.id_club_organisateur = %s
        GROUP BY e.id_evenement, c.id_evenement
        ORDER BY e.date_evenement DESC
    """, (id,))
    evenements = cur.fetchall()
    cur.execute("SELECT id_membre, nom || ' ' || prenom AS nom_complet FROM Membre ORDER BY nom")
    tous_membres = cur.fetchall()
    conn.close()
    return render_template('detail_club.html', club=club, membres=membres,
                           evenements=evenements, tous_membres=tous_membres)

@app.route('/clubs/<int:id_club>/adherer', methods=['POST'])
def adherer(id_club):
    id_membre = request.form['id_membre']
    role = request.form['role']
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Adhere (id_membre, id_club, role_dans_club) VALUES (%s, %s, %s)",
            (id_membre, id_club, role)
        )
        conn.commit()
        flash('Membre ajouté au club.', 'success')
    except psycopg2.IntegrityError:
        flash('Ce membre est déjà dans ce club.', 'warning')
    conn.close()
    return redirect(url_for('detail_club', id=id_club))

@app.route('/clubs/<int:id_club>/retirer/<int:id_membre>', methods=['POST'])
def retirer_membre_club(id_club, id_membre):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Adhere WHERE id_membre=%s AND id_club=%s", (id_membre, id_club))
    conn.commit()
    conn.close()
    flash('Membre retiré du club.', 'warning')
    return redirect(url_for('detail_club', id=id_club))


# ── Événements ────────────────────────────────────────────────────────────────

@app.route('/evenements')
def evenements():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id_evenement, e.titre, e.date_evenement, e.duree, e.lieu,
               cl.nom AS nom_club,
               CASE WHEN c.id_evenement IS NOT NULL THEN 'Conférence'
                    WHEN a.id_evenement IS NOT NULL THEN 'Atelier'
                    ELSE 'Inconnu' END AS type_ev,
               COUNT(p.id_membre) AS nb_inscrits
        FROM Evenement e
        JOIN Club cl ON e.id_club_organisateur = cl.id_club
        LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
        LEFT JOIN Atelier a ON e.id_evenement = a.id_evenement
        LEFT JOIN Participe p ON e.id_evenement = p.id_evenement
        GROUP BY e.id_evenement, cl.nom, c.id_evenement, a.id_evenement
        ORDER BY e.date_evenement DESC
    """)
    evenements = cur.fetchall()
    conn.close()
    return render_template('evenements.html', evenements=evenements)

@app.route('/evenements/ajouter', methods=['GET', 'POST'])
def ajouter_evenement():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        titre = request.form['titre'].strip()
        date_ev = request.form['date_evenement']
        duree = request.form['duree']
        lieu = request.form['lieu'].strip()
        id_club = request.form['id_club']
        type_ev = request.form['type_ev']
        try:
            cur.execute(
                "INSERT INTO Evenement (titre, date_evenement, duree, lieu, id_club_organisateur) VALUES (%s, %s, %s, %s, %s) RETURNING id_evenement",
                (titre, date_ev, duree + ' hours', lieu, id_club)
            )
            id_ev = cur.fetchone()['id_evenement']
            if type_ev == 'conference':
                cur.execute(
                    "INSERT INTO Conference (id_evenement, intervenant, support, capacite_max) VALUES (%s, %s, %s, %s)",
                    (id_ev, request.form['intervenant'].strip(),
                     request.form.get('support') or None,
                     request.form.get('capacite_max') or None)
                )
            else:
                cur.execute(
                    "INSERT INTO Atelier (id_evenement, nb_postes, materiel, niveau_requis) VALUES (%s, %s, %s, %s)",
                    (id_ev, request.form['nb_postes'],
                     request.form.get('materiel', '').strip() or None,
                     request.form['niveau_requis'])
                )
            conn.commit()
            conn.close()
            flash('Événement créé avec succès !', 'success')
            return redirect(url_for('evenements'))
        except Exception as e:
            conn.rollback()
            flash(f'Erreur : {e}', 'danger')
    cur.execute("SELECT id_club, nom FROM Club WHERE statut_validation='valide' ORDER BY nom")
    clubs = cur.fetchall()
    conn.close()
    return render_template('evenement_form.html', clubs=clubs)

@app.route('/evenements/<int:id>/supprimer', methods=['POST'])
def supprimer_evenement(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Evenement WHERE id_evenement = %s", (id,))
    conn.commit()
    conn.close()
    flash('Événement supprimé.', 'warning')
    return redirect(url_for('evenements'))

@app.route('/evenements/<int:id>')
def detail_evenement(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.*, cl.nom AS nom_club,
               CASE WHEN c.id_evenement IS NOT NULL THEN 'Conférence' ELSE 'Atelier' END AS type_ev
        FROM Evenement e
        JOIN Club cl ON e.id_club_organisateur = cl.id_club
        LEFT JOIN Conference c ON e.id_evenement = c.id_evenement
        WHERE e.id_evenement = %s
    """, (id,))
    ev = cur.fetchone()
    cur.execute("SELECT * FROM Conference WHERE id_evenement = %s", (id,))
    conf = cur.fetchone()
    cur.execute("SELECT * FROM Atelier WHERE id_evenement = %s", (id,))
    atelier = cur.fetchone()
    cur.execute("""
        SELECT m.id_membre, m.nom, m.prenom, m.email, p.date_inscription, p.present
        FROM Participe p JOIN Membre m ON p.id_membre = m.id_membre
        WHERE p.id_evenement = %s ORDER BY p.date_inscription
    """, (id,))
    participants = cur.fetchall()
    cur.execute("SELECT id_membre, nom || ' ' || prenom AS nom_complet FROM Membre ORDER BY nom")
    tous_membres = cur.fetchall()
    conn.close()
    return render_template('detail_evenement.html', ev=ev, conf=conf, atelier=atelier,
                           participants=participants, tous_membres=tous_membres)

@app.route('/evenements/<int:id_ev>/inscrire', methods=['POST'])
def inscrire(id_ev):
    id_membre = request.form['id_membre']
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Participe (id_membre, id_evenement) VALUES (%s, %s)",
            (id_membre, id_ev)
        )
        conn.commit()
        flash('Membre inscrit à l\'événement.', 'success')
    except psycopg2.IntegrityError:
        flash('Ce membre est déjà inscrit.', 'warning')
    conn.close()
    return redirect(url_for('detail_evenement', id=id_ev))

@app.route('/evenements/<int:id_ev>/presence/<int:id_membre>', methods=['POST'])
def marquer_presence(id_ev, id_membre):
    present = request.form.get('present') == 'true'
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Participe SET present=%s WHERE id_evenement=%s AND id_membre=%s",
        (present, id_ev, id_membre)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('detail_evenement', id=id_ev))

@app.route('/evenements/<int:id_ev>/desinscrire/<int:id_membre>', methods=['POST'])
def desinscrire(id_ev, id_membre):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Participe WHERE id_evenement=%s AND id_membre=%s", (id_ev, id_membre))
    conn.commit()
    conn.close()
    flash('Membre désinscrit.', 'warning')
    return redirect(url_for('detail_evenement', id=id_ev))


# ── Statistiques ──────────────────────────────────────────────────────────────

@app.route('/stats')
def stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.nom, COUNT(a.id_membre) AS nb_membres
        FROM Club c LEFT JOIN Adhere a ON c.id_club = a.id_club
        WHERE c.statut_validation = 'valide'
        GROUP BY c.id_club, c.nom ORDER BY nb_membres DESC
    """)
    clubs_membres = cur.fetchall()

    cur.execute("""
        SELECT m.statut, COUNT(*) AS nb
        FROM Membre m GROUP BY m.statut
    """)
    repartition = cur.fetchall()

    cur.execute("""
        SELECT niveau_requis, COUNT(*) AS nb FROM Atelier GROUP BY niveau_requis
    """)
    niveaux = cur.fetchall()

    cur.execute("""
        SELECT m.nom || ' ' || m.prenom AS membre,
               COUNT(p.id_evenement) AS nb_events
        FROM Membre m JOIN Participe p ON m.id_membre = p.id_membre
        GROUP BY m.id_membre, m.nom, m.prenom
        ORDER BY nb_events DESC LIMIT 10
    """)
    top_participants = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) FILTER (WHERE present=true) AS presents,
               COUNT(*) FILTER (WHERE present=false) AS absents
        FROM Participe
    """)
    presence = cur.fetchone()

    conn.close()
    return render_template('stats.html', clubs_membres=clubs_membres,
                           repartition=repartition, niveaux=niveaux,
                           top_participants=top_participants, presence=presence)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
