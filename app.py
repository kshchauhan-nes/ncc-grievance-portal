from flask import Flask, render_template, request
import secrets
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "complaints.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS complaints (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id TEXT UNIQUE NOT NULL,

            complaint_type TEXT NOT NULL,

            institution TEXT NOT NULL,

            unit TEXT,

            category TEXT NOT NULL,

            incident_date TEXT,

            description TEXT NOT NULL,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS case_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id TEXT NOT NULL,

            event TEXT NOT NULL,

            description TEXT,

            created_at TEXT NOT NULL

        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/complaint", methods=["GET", "POST"])
def complaint():

    if request.method == "POST":

        complaint_type = request.form.get("complaint_type")
        institution = request.form.get("institution")
        unit = request.form.get("unit")
        category = request.form.get("category")
        incident_date = request.form.get("incident_date")
        description = request.form.get("description")

        case_id = "NCC-" + secrets.token_hex(4).upper()

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        connection = get_db()

        connection.execute("""
            INSERT INTO complaints (

                case_id,
                complaint_type,
                institution,
                unit,
                category,
                incident_date,
                description,
                status,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            case_id,
            complaint_type,
            institution,
            unit,
            category,
            incident_date,
            description,
            "Submitted",
            created_at

        ))

        connection.execute("""
            INSERT INTO case_events (

                case_id,
                event,
                description,
                created_at

            )

            VALUES (?, ?, ?, ?)

        """, (

            case_id,
            "Complaint Submitted",
            "The grievance was successfully submitted through the portal.",
            created_at

        ))

        connection.commit()
        connection.close()

        return render_template(
            "confirmation.html",
            case_id=case_id
        )

    return render_template("complaint.html")


@app.route("/track", methods=["GET", "POST"])
def track():

    complaint = None
    events = []
    error = None

    if request.method == "POST":

        case_id = request.form.get("case_id", "").strip().upper()

        connection = get_db()

        complaint = connection.execute(
            """
            SELECT *
            FROM complaints
            WHERE case_id = ?
            """,
            (case_id,)
        ).fetchone()

        if complaint:

            events = connection.execute(
                """
                SELECT *
                FROM case_events
                WHERE case_id = ?
                ORDER BY created_at ASC
                """,
                (case_id,)
            ).fetchall()

        else:

            error = "No case found with that Case ID."

        connection.close()

    return render_template(
        "track.html",
        complaint=complaint,
        events=events,
        error=error
    )


if __name__ == "__main__":

    init_db()

    app.run(debug=True)