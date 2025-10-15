from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "healthcare_secret_2025"

# -------------------- DATABASE SETUP --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------
class SymptomCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptoms = db.Column(db.Text, nullable=False)
    conditions = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)

# -------------------- RULE-BASED LOGIC --------------------
def analyze_symptoms(symptom_text):
    symptom_text = symptom_text.lower()

    # ---- COMBINED SYMPTOMS ----
    if "fever" in symptom_text and "cough" in symptom_text:
        return (
            "Common Cold or Flu",
            "Drink warm fluids, rest well, and monitor temperature. See a doctor if it lasts more than 3 days.",
            "Usually caused by viral infections. Symptoms include mild fever, cough, runny nose, and fatigue.",
            "If fever goes above 102°F or lasts more than 3 days."
        )
    elif "headache" in symptom_text and "nausea" in symptom_text:
        return (
            "Migraine",
            "Rest in a dark, quiet room and stay hydrated. Avoid loud noise and bright lights.",
            "Migraine headaches often cause intense throbbing pain with nausea and light sensitivity.",
            "If headaches are frequent or disrupt your daily activities."
        )
    elif "stomach" in symptom_text or "vomit" in symptom_text or "diarrhea" in symptom_text:
        return (
            "Stomach Infection or Food Poisoning",
            "Drink water with electrolytes and avoid oily food. Consult a doctor if vomiting persists.",
            "Usually caused by contaminated food or bacteria. Symptoms include nausea, vomiting, and stomach cramps.",
            "If you feel dizzy, weak, or can’t keep fluids down."
        )
    elif "sore throat" in symptom_text or "cold" in symptom_text:
        return (
            "Throat Infection",
            "Gargle with warm salt water and avoid cold drinks. Use lozenges for relief.",
            "Can be caused by viral or bacterial infection. Common signs include throat pain, hoarseness, and mild fever.",
            "If symptoms persist more than 5 days or worsen."
        )
    elif "fatigue" in symptom_text or "tired" in symptom_text or "weak" in symptom_text:
        return (
            "Dehydration or Vitamin Deficiency",
            "Drink more water and eat fruits. Get a basic blood test if it continues.",
            "Often caused by poor nutrition, low iron, or lack of sleep.",
            "If tiredness lasts more than two weeks despite rest."
        )

    # ---- SINGLE SYMPTOMS ----
    elif "fever" in symptom_text:
        return (
            "Fever (Possible Infection)",
            "Stay hydrated, rest, and check temperature regularly. Visit a doctor if fever persists over 3 days.",
            "Usually indicates the body is fighting an infection or inflammation.",
            "If temperature crosses 102°F or is accompanied by chills or rash."
        )
    elif "cough" in symptom_text:
        return (
            "Respiratory Irritation or Cold",
            "Drink warm fluids, avoid dusty environments, and consult a doctor if it continues more than a week.",
            "Coughs are often caused by viral infection, allergies, or throat irritation.",
            "If cough lasts over 10 days or includes blood or chest pain."
        )
    elif "headache" in symptom_text:
        return (
            "Mild Tension Headache",
            "Drink water, rest your eyes, and reduce stress or screen time.",
            "Often caused by eye strain, dehydration, or tension.",
            "If headaches occur frequently or are very painful."
        )
    elif "nausea" in symptom_text:
        return (
            "Possible Indigestion or Migraine",
            "Eat light food, avoid greasy meals, and rest well.",
            "Nausea can come from motion sickness, overeating, or viral infections.",
            "If vomiting or dizziness develops along with nausea."
        )
    elif "vomit" in symptom_text:
        return (
            "Stomach Upset",
            "Avoid solid food for a few hours, drink fluids, and see a doctor if vomiting continues.",
            "Can result from food poisoning or gastritis.",
            "If vomiting persists for 24 hours or has blood."
        )
    elif "cold" in symptom_text:
        return (
            "Common Cold",
            "Rest well, drink warm water, and take steam inhalation.",
            "A mild viral infection of the nose and throat.",
            "If cold lasts more than a week or includes high fever."
        )
    elif "sore throat" in symptom_text:
        return (
            "Throat Irritation",
            "Gargle warm salt water and avoid cold drinks.",
            "May be caused by allergies, dry air, or viral infection.",
            "If difficulty swallowing or persistent pain occurs."
        )

    # ---- DEFAULT ----
    else:
        return (
            "Unclear – could be multiple causes",
            "Please describe your symptoms in more detail or visit a doctor for an accurate diagnosis.",
            "Your symptoms could be due to various mild conditions or lifestyle factors.",
            "If symptoms persist, seek a medical checkup for accurate diagnosis."
        )

# -------------------- ROUTES --------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_symptoms():
    symptom_text = request.form['symptoms']

    # Get all four returned values
    condition, advice, description, warning = analyze_symptoms(symptom_text)

    # Save to database
    record = SymptomCheck(symptoms=symptom_text, conditions=condition, recommendations=advice)
    db.session.add(record)
    db.session.commit()

    flash("Symptoms checked successfully!", "success")

    info = {
        "description": description,
        "symptoms": [s.strip() for s in symptom_text.split(",")],  # optional: list for template
        "prevention": warning
    }

    return render_template('result.html', condition=condition, advice=advice, symptoms=symptom_text, info=info)

@app.route('/history')
def history():
    records = SymptomCheck.query.all()
    return render_template('history.html', records=records)

# -------------------- MAIN --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
