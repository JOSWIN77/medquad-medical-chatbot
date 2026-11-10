"""
ner.py
Lightweight medical Named Entity Recognition using keyword lists.
"""

ENTITIES = {
    "SYMPTOM": [
        "pain","fever","cough","fatigue","nausea","vomiting","diarrhea","headache",
        "dizziness","shortness of breath","chest pain","rash","swelling","itching",
        "bleeding","weight loss","weight gain","chills","sweating","insomnia",
        "anxiety","depression","confusion","seizure","fainting","numbness","tingling",
        "blurred vision","hearing loss","sore throat","runny nose","muscle weakness",
        "joint pain","back pain","abdominal pain","constipation","bloating","loss of appetite",
    ],
    "DISEASE": [
        "diabetes","cancer","hypertension","asthma","alzheimer","parkinson","arthritis",
        "stroke","heart disease","hepatitis","tuberculosis","hiv","aids","covid","influenza",
        "pneumonia","bronchitis","anemia","leukemia","lymphoma","melanoma","epilepsy",
        "multiple sclerosis","fibromyalgia","lupus","crohn","colitis","ibs","gerd",
        "hypothyroidism","hyperthyroidism","osteoporosis","autism","adhd","schizophrenia",
        "bipolar","obesity","celiac","psoriasis","eczema","glaucoma","cataracts",
    ],
    "TREATMENT": [
        "surgery","chemotherapy","radiation","medication","therapy","vaccine","antibiotic",
        "insulin","dialysis","transplant","immunotherapy","physiotherapy","psychotherapy",
        "biopsy","endoscopy","mri","ct scan","x-ray","blood test","ultrasound",
        "stem cell","gene therapy","laser","exercise","diet","supplement","vitamin",
    ],
    "BODY_PART": [
        "heart","lung","liver","kidney","brain","stomach","intestine","colon","pancreas",
        "bladder","thyroid","bone","muscle","skin","eye","ear","nose","throat","spine",
        "blood","nerve","artery","vein","lymph node","breast","prostate","ovary","uterus",
    ],
    "DRUG": [
        "aspirin","ibuprofen","acetaminophen","metformin","lisinopril","atorvastatin",
        "amoxicillin","penicillin","warfarin","omeprazole","levothyroxine","metoprolol",
        "amlodipine","gabapentin","sertraline","fluoxetine","prednisone","albuterol",
    ],
}

# Flatten for quick lookup
_LOWER_MAP = {}
for label, words in ENTITIES.items():
    for w in words:
        _LOWER_MAP[w.lower()] = label

_COLOR = {
    "SYMPTOM":    "#ff6b6b",
    "DISEASE":    "#a855f7",
    "TREATMENT":  "#22c55e",
    "BODY_PART":  "#3b82f6",
    "DRUG":       "#f59e0b",
}

_EMOJI = {
    "SYMPTOM":   "🤒",
    "DISEASE":   "🦠",
    "TREATMENT": "💊",
    "BODY_PART": "🫀",
    "DRUG":      "💉",
}


def extract_entities(text: str) -> list[dict]:
    """Return list of {text, label} dicts found in text."""
    lower = text.lower()
    found = {}
    # Longest match first
    for phrase in sorted(_LOWER_MAP, key=len, reverse=True):
        if phrase in lower and phrase not in found:
            found[phrase] = _LOWER_MAP[phrase]
    return [{"text": k, "label": v} for k, v in found.items()]


def highlight_entities(text: str, entities: list[dict]) -> str:
    """Return HTML with entity spans highlighted."""
    result = text
    for ent in sorted(entities, key=lambda e: len(e["text"]), reverse=True):
        color = _COLOR.get(ent["label"], "#gray")
        emoji = _EMOJI.get(ent["label"], "")
        badge = (
            f'<span style="background:{color}22;border:1px solid {color};'
            f'color:{color};border-radius:4px;padding:1px 5px;font-weight:600;'
            f'font-size:0.85em">{emoji} {ent["text"].title()} '
            f'<sup style="font-size:0.7em">{ent["label"]}</sup></span>'
        )
        result = result.replace(ent["text"], badge)
        result = result.replace(ent["text"].title(), badge)
    return result


def entity_color(label: str) -> str:
    return _COLOR.get(label, "#888")
