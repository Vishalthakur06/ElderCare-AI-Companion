"""
ElderCare AI Engine
- Health Risk Analyzer      : rule-based ML scoring on vitals
- Medicine Interaction      : known interaction database
- Symptom Chatbot           : NLP keyword matching
- AI Health Score           : weighted composite score 0-100
- Health Trend Analyzer     : trend detection (improving/worsening)
- Medicine Refill Alerts    : end_date proximity warnings
- Appointment Priority      : urgency prediction from purpose keywords
"""

import re as _re
from datetime import date, datetime

# ── Health Risk Analyzer ──────────────────────────────────────────────────────

def analyze_health(kind, value_str):
    kind = kind.lower().strip()
    v    = value_str.strip()
    if "blood pressure" in kind: return _analyze_bp(v)
    if "blood sugar"    in kind: return _analyze_sugar(v)
    if "pulse"          in kind: return _analyze_pulse(v)
    if "weight"         in kind: return {"level":"normal","label":"Logged ✅","advice":"Weight recorded. Track trends over time.","score":1}
    return {"level":"normal","label":"Logged ✅","advice":"Entry recorded successfully.","score":1}

def _parse_num(s):
    return [float(n) for n in _re.findall(r'\d+\.?\d*', s)]

def _analyze_bp(v):
    nums = _parse_num(v)
    if len(nums) < 2:
        return {"level":"normal","label":"Logged","advice":"Enter BP as systolic/diastolic e.g. 120/80.","score":0}
    sys, dia = nums[0], nums[1]
    if sys < 90 or dia < 60:
        return {"level":"critical","label":"Low BP ⚠️","advice":"Blood pressure is low. Sit down, drink water, contact your doctor if dizzy.","score":-2}
    if sys <= 120 and dia <= 80:
        return {"level":"normal","label":"Normal ✅","advice":"Blood pressure is in the healthy range. Keep it up!","score":2}
    if sys <= 129 and dia < 80:
        return {"level":"warning","label":"Elevated 🟡","advice":"BP slightly elevated. Reduce salt, stay hydrated, monitor daily.","score":1}
    if sys <= 139 or dia <= 89:
        return {"level":"warning","label":"High Stage 1 🟠","advice":"Stage 1 hypertension. Consult your doctor. Reduce stress and salty foods.","score":-1}
    return {"level":"critical","label":"High Stage 2 🔴","advice":"Stage 2 hypertension. Please contact your doctor immediately.","score":-2}

def _analyze_sugar(v):
    nums = _parse_num(v)
    if not nums:
        return {"level":"normal","label":"Logged","advice":"Enter blood sugar value in mg/dL.","score":0}
    s = nums[0]
    if s < 70:   return {"level":"critical","label":"Low Sugar ⚠️","advice":"Hypoglycemia. Eat something sweet immediately and rest.","score":-2}
    if s <= 99:  return {"level":"normal","label":"Normal ✅","advice":"Fasting blood sugar is normal. Great job!","score":2}
    if s <= 125: return {"level":"warning","label":"Pre-diabetic 🟡","advice":"Pre-diabetic range. Reduce sugar, exercise, consult doctor.","score":1}
    if s <= 180: return {"level":"warning","label":"High 🟠","advice":"Blood sugar high. Avoid sweets, drink water, recheck in 2 hours.","score":-1}
    return {"level":"critical","label":"Very High 🔴","advice":"Dangerously high blood sugar. Contact your doctor immediately.","score":-2}

def _analyze_pulse(v):
    nums = _parse_num(v)
    if not nums:
        return {"level":"normal","label":"Logged","advice":"Enter pulse in beats per minute.","score":0}
    p = nums[0]
    if p < 50:   return {"level":"critical","label":"Very Low ⚠️","advice":"Bradycardia. Sit down and contact your doctor.","score":-2}
    if p <= 60:  return {"level":"warning","label":"Low-Normal 🟡","advice":"Slightly low pulse. Normal for athletes. Monitor if dizzy.","score":1}
    if p <= 100: return {"level":"normal","label":"Normal ✅","advice":"Pulse rate is in the healthy range.","score":2}
    if p <= 120: return {"level":"warning","label":"Elevated 🟠","advice":"Elevated pulse. Rest 10 min, recheck. Avoid caffeine.","score":-1}
    return {"level":"critical","label":"Very High 🔴","advice":"Tachycardia. Sit down and contact your doctor immediately.","score":-2}


# ── AI Health Score (0–100) ───────────────────────────────────────────────────

def compute_health_score(records):
    """
    Takes list of HealthRecord objects.
    Returns {score, grade, color, summary, breakdown}
    Uses weighted scoring per vital category.
    """
    if not records:
        return {"score": None, "grade": "N/A", "color": "var(--muted)",
                "summary": "No health records yet. Add measurements to get your AI Health Score.",
                "breakdown": []}

    weights   = {"blood pressure": 35, "blood sugar": 30, "pulse": 20, "weight": 15}
    seen      = {}
    for r in records:
        k = r.kind.lower()
        if k not in seen:
            seen[k] = analyze_health(r.kind, r.value)

    total_weight = 0
    total_score  = 0
    breakdown    = []

    for kind_key, weight in weights.items():
        matched = next((v for k, v in seen.items() if kind_key in k), None)
        if matched:
            # score: -2 to 2 → normalize to 0-100
            normalized = (matched["score"] + 2) / 4 * 100
            total_score  += normalized * weight
            total_weight += weight
            breakdown.append({
                "kind":   kind_key.title(),
                "label":  matched["label"],
                "level":  matched["level"],
                "weight": weight,
                "points": round(normalized)
            })

    if total_weight == 0:
        final = 50
    else:
        final = round(total_score / total_weight)

    if final >= 80:
        grade, color = "Excellent 🌟", "var(--green)"
        summary = "Your vitals look great! Keep up the healthy habits."
    elif final >= 60:
        grade, color = "Good 👍", "var(--teal)"
        summary = "Your health is generally good. Monitor the flagged areas."
    elif final >= 40:
        grade, color = "Fair ⚠️", "var(--amber)"
        summary = "Some vitals need attention. Consult your doctor soon."
    else:
        grade, color = "Needs Attention 🔴", "var(--red)"
        summary = "Multiple vitals are concerning. Please see your doctor as soon as possible."

    return {"score": final, "grade": grade, "color": color, "summary": summary, "breakdown": breakdown}


# ── Health Trend Analyzer ─────────────────────────────────────────────────────

def analyze_trends(records):
    """
    Takes list of HealthRecord objects (all records, not just latest).
    Returns dict of {kind: {trend, direction, data_points, labels}}
    trend: 'improving' | 'worsening' | 'stable' | 'insufficient'
    """
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in sorted(records, key=lambda x: x.recorded_at):
        nums = _parse_num(r.value)
        if nums:
            grouped[r.kind].append({
                "val":   nums[0],
                "label": r.recorded_at.strftime("%d %b")
            })

    trends = {}
    for kind, points in grouped.items():
        if len(points) < 2:
            trends[kind] = {"trend":"insufficient","direction":"—","data_points":[p["val"] for p in points],"labels":[p["label"] for p in points]}
            continue
        vals  = [p["val"] for p in points]
        first = sum(vals[:max(1,len(vals)//3)]) / max(1,len(vals)//3)
        last  = sum(vals[-max(1,len(vals)//3):]) / max(1,len(vals)//3)
        diff  = last - first
        # For BP/sugar/pulse: lower is generally better (except too low)
        if abs(diff) < 2:
            direction, trend = "→ Stable", "stable"
        elif diff < 0:
            direction, trend = "↓ Decreasing", "improving"
        else:
            direction, trend = "↑ Increasing", "worsening"
        trends[kind] = {
            "trend":       trend,
            "direction":   direction,
            "data_points": vals,
            "labels":      [p["label"] for p in points]
        }
    return trends


# ── Medicine Refill Alerts ────────────────────────────────────────────────────

def check_refill_alerts(medicines):
    """
    Takes list of Medicine objects.
    Returns list of {name, days_left, urgency}
    """
    today   = date.today()
    alerts  = []
    for m in medicines:
        if not m.end_date:
            continue
        try:
            end = datetime.strptime(m.end_date, "%Y-%m-%d").date()
            days_left = (end - today).days
            if days_left < 0:
                alerts.append({"name": m.name, "days_left": days_left, "urgency": "expired",
                                "message": f"{m.name} course ended {abs(days_left)} days ago. Consult your doctor."})
            elif days_left <= 3:
                alerts.append({"name": m.name, "days_left": days_left, "urgency": "critical",
                                "message": f"{m.name} runs out in {days_left} day(s). Refill immediately!"})
            elif days_left <= 7:
                alerts.append({"name": m.name, "days_left": days_left, "urgency": "warning",
                                "message": f"{m.name} runs out in {days_left} days. Plan your refill soon."})
        except ValueError:
            continue
    return sorted(alerts, key=lambda x: x["days_left"])


# ── Appointment Priority Predictor ────────────────────────────────────────────

URGENT_KEYWORDS   = ["chest","heart","emergency","urgent","pain","surgery","cancer","stroke","breathing","critical"]
ROUTINE_KEYWORDS  = ["checkup","routine","followup","follow up","review","general","annual","regular"]

def predict_appointment_priority(appointments):
    """
    Takes list of Appointment objects.
    Returns list with added priority field: 'urgent' | 'soon' | 'routine'
    """
    today   = date.today()
    results = []
    for a in appointments:
        try:
            appt_date = datetime.strptime(a.when[:10], "%Y-%m-%d").date()
            days_away = (appt_date - today).days
        except Exception:
            days_away = 999

        text = (a.purpose + " " + a.notes + " " + a.doctor).lower()

        if any(k in text for k in URGENT_KEYWORDS) or days_away <= 2:
            priority = "urgent"
            priority_label = "🔴 Urgent"
        elif days_away <= 7:
            priority = "soon"
            priority_label = "🟠 This Week"
        elif any(k in text for k in ROUTINE_KEYWORDS):
            priority = "routine"
            priority_label = "🟢 Routine"
        else:
            priority = "soon"
            priority_label = "🟡 Upcoming"

        results.append({
            "id":             a.id,
            "doctor":         a.doctor,
            "clinic":         a.clinic,
            "when":           a.when,
            "purpose":        a.purpose,
            "notes":          a.notes,
            "days_away":      days_away,
            "priority":       priority,
            "priority_label": priority_label,
        })

    return sorted(results, key=lambda x: x["days_away"])


# ── Medicine Interaction Checker ──────────────────────────────────────────────

INTERACTIONS = [
    ({"aspirin","ibuprofen"},       "High",   "Aspirin + Ibuprofen increases bleeding risk. Avoid taking together."),
    ({"aspirin","warfarin"},        "High",   "Aspirin + Warfarin significantly increases bleeding risk. Consult your doctor."),
    ({"metformin","alcohol"},       "Medium", "Metformin + Alcohol can cause lactic acidosis. Avoid alcohol."),
    ({"amlodipine","simvastatin"},  "Medium", "Amlodipine + Simvastatin may increase muscle pain risk. Monitor carefully."),
    ({"lisinopril","potassium"},    "Medium", "Lisinopril + Potassium supplements can raise potassium to dangerous levels."),
    ({"warfarin","vitamin k"},      "High",   "Warfarin + Vitamin K reduces warfarin effectiveness. Maintain consistent intake."),
    ({"digoxin","amiodarone"},      "High",   "Digoxin + Amiodarone can cause dangerous heart rhythm changes."),
    ({"ssri","tramadol"},           "High",   "SSRIs + Tramadol can cause serotonin syndrome. Consult your doctor immediately."),
    ({"methotrexate","nsaid"},      "High",   "Methotrexate + NSAIDs increases toxicity risk. Avoid combination."),
    ({"clopidogrel","omeprazole"},  "Medium", "Clopidogrel + Omeprazole may reduce clopidogrel effectiveness."),
]

def check_interactions(medicine_names):
    names    = {n.lower().strip() for n in medicine_names}
    warnings = []
    for pair, severity, msg in INTERACTIONS:
        matched = [p for p in pair if any(p in n for n in names)]
        if len(matched) >= 2:
            warnings.append({"severity": severity, "message": msg, "drugs": matched})
    return warnings


# ── Symptom Chatbot ───────────────────────────────────────────────────────────

SYMPTOM_RULES = [
    (["chest pain","chest tightness","chest pressure"],
     "🚨 Chest pain can be serious. Call emergency services (112) immediately if pain is severe or spreading to your arm/jaw."),
    (["breathless","short of breath","difficulty breathing","cannot breathe","cant breathe"],
     "🚨 Difficulty breathing needs immediate attention. Sit upright, stay calm, and call 112 if it doesn't improve in 2 minutes."),
    (["headache","head pain","migraine","sir dard","sar dard"],
     "💊 For headaches: rest in a quiet dark room, drink water, and take prescribed pain relief. See a doctor if sudden and severe."),
    (["dizzy","dizziness","lightheaded","vertigo","chakkar"],
     "⚠️ Dizziness can be caused by low BP, dehydration, or inner ear issues. Sit down, drink water, avoid sudden movements."),
    (["fever","temperature","chills","bukhar"],
     "🌡️ For fever: rest, drink plenty of fluids, take paracetamol if prescribed. See a doctor if fever exceeds 103°F / 39.4°C."),
    (["sugar","blood sugar","glucose","diabetic","diabetes"],
     "🍬 Monitor blood sugar regularly. If feeling shaky or sweaty, eat something sweet immediately. Log readings in Health Tracking."),
    (["blood pressure","hypertension","bp high","bp low"],
     "❤️ Check BP regularly and log it in Health Tracking. Reduce salt, exercise gently, take prescribed medicines on time."),
    (["pain","ache","sore","dard","dukh","takleef"],
     "💊 For general pain: rest the area, apply warm/cold compress, take prescribed pain relief. See a doctor if pain persists."),
    (["sleep","insomnia","cant sleep","cannot sleep","nahi so","neend nahi","neend"],
     "😴 For better sleep: maintain a fixed bedtime, avoid screens 1 hour before bed, try the breathing exercise on your dashboard."),
    (["anxiety","stress","worried","nervous","tension","ghabrahat"],
     "🧘 Try the 4-7-8 breathing exercise on your dashboard. Talk to a trusted family member. Consider speaking to your doctor."),
    (["fall","fell","balance","gira","gir gaya"],
     "⚠️ Falls are serious for elders. Check for injuries. Use support when walking and remove home hazards."),
    (["medicine","medication","tablet","pill","dose","dawai","dawa"],
     "💊 Check your Medicine Reminders page for your schedule. Never skip or double doses. Contact your doctor before changing any medicine."),
    (["lonely","alone","sad","depressed","akela","udaas"],
     "💙 Feeling lonely is common. Try calling a family member from your Emergency Contacts. Social connection is vital for health."),
    (["water","dehydrated","thirsty","paani"],
     "💧 Drink at least 8 glasses of water daily. Dehydration causes dizziness, headaches, and confusion in elders."),
    (["cold","cough","flu","runny nose","khansi","zukam"],
     "🤧 For cold/flu: rest, drink warm fluids, take prescribed medicines. See a doctor if symptoms worsen after 3 days."),
    (["vomit","nausea","nauseous","ulti","ji machlana"],
     "🤢 For nausea: sip water slowly, avoid solid food for a while, rest. See a doctor if vomiting persists more than 6 hours."),
    (["swelling","swollen","sujan"],
     "🦵 Swelling can indicate fluid retention or injury. Elevate the affected area and consult your doctor if it doesn't reduce."),
    (["eye","vision","blurry","aankhein","aankh"],
     "👁️ Eye issues in elders can be serious. Avoid straining your eyes. See an eye doctor if vision is blurry or painful."),
    (["memory","forget","bhool","yaad nahi"],
     "🧠 Memory concerns are common with age. Stay mentally active, sleep well, and discuss with your doctor at your next visit."),
    (["appetite","not eating","khana nahi","bhookh nahi"],
     "🍽️ Loss of appetite can be a sign of illness or medication side effects. Try small frequent meals and consult your doctor."),
]

GREETINGS = ["hello","hi","hey","namaste","namaskar","good morning","good evening","hii","helo"]
THANKS    = ["thank","thanks","thank you","shukriya","dhanyawad","shukriya"]

def _word_match(word, text):
    return bool(_re.search(r'\b' + _re.escape(word) + r'\b', text))

def chat_response(message):
    msg = message.lower().strip()

    for keywords, response in SYMPTOM_RULES:
        if any(kw in msg for kw in keywords):
            return response

    if any(_word_match(g, msg) for g in GREETINGS):
        return "👋 Hello! I'm your ElderCare AI Assistant. Describe your symptoms or ask a health question and I'll guide you."

    if any(_word_match(t, msg) for t in THANKS):
        return "😊 You're welcome! Stay healthy and take your medicines on time. I'm always here if you need guidance."

    if any(w in msg for w in ["emergency","sos","urgent","help me"]):
        return "🚨 For emergencies, go to your SOS page immediately and call your emergency contact. If life-threatening, call 112 now."

    if any(w in msg for w in ["score","health score","mera score"]):
        return "📊 Visit the AI Assistant page to see your personalized AI Health Score based on all your recorded vitals!"

    if any(w in msg for w in ["appointment","doctor","visit","appt"]):
        return "📅 Check your Appointments page for upcoming visits. The AI prioritizes them by urgency automatically."

    return "🤔 I didn't fully understand that. Try: 'I have a headache', 'my BP is high', 'I feel dizzy', or 'I cannot sleep'."
