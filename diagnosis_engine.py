from symptoms_disease_data import SYMPTOM_DISEASE_MAP
from blood_tests_data import DISEASE_BLOOD_TESTS
from medicine_data import DISEASE_MEDICINE

def get_diagnosis(symptoms):
    diseases = []
    for symptom in symptoms:
        if symptom in SYMPTOM_DISEASE_MAP:
            diseases += SYMPTOM_DISEASE_MAP[symptom]
    return list(set(diseases))  # unique

def get_blood_tests(disease):
    return DISEASE_BLOOD_TESTS.get(disease, [])

def get_medicines(disease):
    return DISEASE_MEDICINE.get(disease, [])
