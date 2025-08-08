import streamlit as st
import pyrebase

# Your Firebase config here
firebase_config = {
    "apiKey": "AIzaSyCtJfZ3NP0QAzvxuMy5g8OaoRvbAp38h7g",
    "authDomain": "coffee-spark-sample-app-6e3c3.firebaseapp.com",
    "projectId": "coffee-spark-sample-app-6e3c3",
    "storageBucket": "coffee-spark-sample-app-6e3c3.appspot.com",
    "messagingSenderId": "390421433463",
    "appId": "1:390421433463:web:d385b421e981ef85eb0a72",
    "databaseURL": ""  # leave empty
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize session state variables
if "user" not in st.session_state:
    st.session_state.user = None
if "email" not in st.session_state:
    st.session_state.email = ""
if "password" not in st.session_state:
    st.session_state.password = ""

# Sidebar login/logout section
st.sidebar.title("🔐 User Login")

if st.session_state.user:
    st.sidebar.success(f"👋 Logged in as: {st.session_state.user['email']}")
    if st.sidebar.button("🚪 Logout"):
        del st.session_state["user"]
        st.session_state.email = ""
        st.session_state.password = ""
        st.experimental_rerun()
else:
    # Login/signup form
    st.sidebar.text_input("📧 Email", key="email")
    st.sidebar.text_input("🔑 Password", type="password", key="password")

    col1, col2 = st.sidebar.columns(2)
    if col1.button("🔓 Login"):
        try:
            user = auth.sign_in_with_email_and_password(st.session_state.email, st.session_state.password)
            st.session_state.user = user
            st.session_state.email = ""
            st.session_state.password = ""
            st.success("✅ Login successful!")
            st.experimental_rerun()
        except Exception as e:
            st.error("❌ Login failed. Please check your credentials.")
    
    if col2.button("📝 Sign Up"):
        try:
            user = auth.create_user_with_email_and_password(st.session_state.email, st.session_state.password)
            st.session_state.user = user
            st.session_state.email = ""
            st.session_state.password = ""
            st.success("✅ Account created and logged in!")
            st.experimental_rerun()
        except Exception as e:
            st.error("❌ Error creating account. Try a stronger password or different email.")

import speech_recognition as sr

def recognize_symptoms_by_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎙️ Listening... Please speak your symptoms (e.g., fever, cough)...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"🗣️ You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Speech API error: {e}")
    return ""

import streamlit as st
import speech_recognition as sr
import random
import datetime  
if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []


import random

HEALTH_TIPS = [
    "Drink at least 8 glasses of water every day.",
    "Get at least 7–8 hours of sleep each night.",
    "Wash your hands regularly to prevent infections.",
    "Take a 10-minute walk after meals to improve digestion.",
    "Include fruits and vegetables in your diet every day.",
    "Avoid using mobile phones before bed for better sleep.",
    "Do regular stretching to prevent stiffness.",
    "Limit sugar intake to maintain stable energy levels.",
    "Do not skip breakfast — it's the most important meal of the day.",
    "Practice deep breathing or meditation to reduce stress."
]

def show_random_health_tip():
    tip = random.choice(HEALTH_TIPS)
    st.sidebar.markdown(f"🩺 **Health Tip:** _{tip}_")

import streamlit as st
from openai import OpenAI
from symptoms_disease_data import SYMPTOM_DISEASE_MAP
from blood_tests_data import DISEASE_BLOOD_TESTS
from medicine_data import DISEASE_MEDICINE
from food_suggestions import DISEASE_FOOD
from emergency_firstaid_data import FIRST_AID_GUIDELINES
from emergency_guidelines import EMERGENCY_GUIDELINES
from doctor_suggestions import CRITICAL_DISEASES, DOCTOR_RECOMMENDATIONS
import requests

# OpenAI client setup
client = OpenAI(api_key="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")

GOOGLE_API_KEY = "your_google_maps_api_key"

def get_real_doctors(query="doctor", location="kolkata"):
    try:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} in {location}",
            "key": GOOGLE_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [
                {
                    "name": r.get("name"),
                    "address": r.get("formatted_address"),
                    "rating": r.get("rating", "N/A")
                }
                for r in results[:5]
            ]
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching doctor data: {e}")
        return []

def get_best_matching_disease(symptoms):
    disease_symptom_map = {}
    for symptom, diseases in SYMPTOM_DISEASE_MAP.items():
        for disease in diseases:
            disease_symptom_map.setdefault(disease, []).append(symptom)
    scores = {disease: sum(1 for symptom in symptoms if symptom in ds) for disease, ds in disease_symptom_map.items()}
    return max(scores, key=scores.get) if scores else None

def get_nearest_hospitals(city):
    return get_real_doctors("hospital", city)

def calculate_bmi(weight, height_cm):
    if height_cm <= 0:
        return 0
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

st.set_page_config(page_title="AI Doctor", layout="centered")
st.sidebar.title("🩺 AI Doctor")
st.sidebar.markdown("Built with ❤️ by Raj Mallick")
st.sidebar.markdown("This app helps you:")
st.sidebar.markdown("- Diagnose illness\n- Suggest medicines\n- Recommend blood tests\n- Recommend food\n- Emergency survival tips\n- Find real doctors\n- Calculate BMI & show alerts\n- Ask chatbot Mr. Doctor")
st.sidebar.info("⚠️ For educational/hackathon use only. Not real medical advice.")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏥 Diagnosis", "🆘 Emergency", "🌍 Find Doctors",
    "🚑 Emergency Help", "💬 Mr. Doctor", "📜 History", "📺 Doctor Advice", "ℹ️ About"
])

with tab1:
    st.header("🏥 Smart Diagnosis")

    # ✅ Ensure diagnosis_history is always a dict
    if "diagnosis_history" not in st.session_state:
        st.session_state["diagnosis_history"] = {}
    elif isinstance(st.session_state["diagnosis_history"], list):
        # convert old list into dict for current user
        if "user" in st.session_state and st.session_state["user"]:
            user_email = st.session_state["user"]["email"]
            st.session_state["diagnosis_history"] = {user_email: st.session_state["diagnosis_history"]}
        else:
            st.session_state["diagnosis_history"] = {"_legacy": st.session_state["diagnosis_history"]}

    # Form for user input
    with st.form("diagnosis_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=1, max_value=120)
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=200.0)
        with col2:
            gender = st.radio("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", min_value=30.0, max_value=250.0)
            default_symptoms = st.session_state.get("voice_symptoms", [])
            symptoms = st.multiselect(
                "Select your symptoms:",
                sorted(SYMPTOM_DISEASE_MAP.keys()),
                default=default_symptoms
            )
        submitted = st.form_submit_button("🔍 Diagnose")

    # Voice input button
    if st.button("🎙️ Speak Symptoms Instead"):
        spoken_text = recognize_symptoms_by_voice()
        detected = [sym for sym in SYMPTOM_DISEASE_MAP.keys() if sym.lower() in spoken_text]
        if detected:
            st.success(f"✅ Detected Symptoms: {', '.join(detected)}")
            st.session_state.voice_symptoms = detected
        else:
            st.warning("⚠️ No recognizable symptoms found.")

    # After diagnosis
    if submitted:
        st.markdown("---")
        st.markdown(f"### 👤 Patient Info: **{name or 'Unknown'}**")
        st.markdown(f"- **Age:** {age} | **Gender:** {gender} | **Weight:** {weight}kg | **Height:** {height}cm")

        bmi = calculate_bmi(weight, height)
        st.markdown(f"- **BMI:** {bmi}")
        if bmi < 18.5:
            st.warning("⚠️ Underweight BMI. Consider consulting a nutritionist.")
        elif bmi > 30:
            st.warning("⚠️ High BMI. Risk of obesity-related complications.")

        st.markdown(f"- **Symptoms:** {', '.join(symptoms) if symptoms else 'None selected'}")
        st.markdown("---")

        if not symptoms:
            st.warning("Please select at least one symptom.")
        else:
            best_disease = get_best_matching_disease(symptoms)
            if best_disease:
                st.success(f"🌟 Most Likely Diagnosis: **{best_disease}**")

                if age < 15 or age > 60:
                    st.warning("👶🧓 Based on age, we recommend consulting a doctor instead of self-medicating.")
                else:
                    st.markdown("**📊 Recommended Tests:**")
                    for test in DISEASE_BLOOD_TESTS.get(best_disease, []):
                        st.write(f"- {test}")

                    st.markdown("**💊 Medicines:**")
                    for med in DISEASE_MEDICINE.get(best_disease, []):
                        st.write(f"- {med}")

                    st.markdown("**🥗 Food Suggestions:**")
                    for food in DISEASE_FOOD.get(best_disease, []):
                        st.write(f"- {food}")

                if best_disease in CRITICAL_DISEASES:
                    st.warning("⚠️ This may be a critical condition. Please consult a doctor immediately.")
                    st.markdown("### 🧑‍⚕️ Offline Doctor Recommendations:")
                    for doc in DOCTOR_RECOMMENDATIONS.get(best_disease, []):
                        st.write(f"- **{doc['name']}** ({doc['specialty']}) — 📞 {doc['contact']}")

                # ✅ Save to per-user history
                if "user" in st.session_state and st.session_state["user"]:
                    user_email = st.session_state["user"]["email"]
                    st.session_state["diagnosis_history"].setdefault(user_email, []).append({
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "symptoms": symptoms,
                        "disease": best_disease,
                        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("📜 Diagnosis saved to your history!")
                else:
                    st.warning("🔐 Please log in to save diagnosis to history.")
            else:
                st.error("No disease match found.")

with tab2:
    st.header("🆘 Emergency Survival Assistant")
    em_type = st.radio("Choose emergency type:", ["Medical Emergency", "Natural Disaster"])

    if em_type == "Medical Emergency":
        em_list = list(FIRST_AID_GUIDELINES.keys())
        selected_em = st.selectbox("Select condition:", em_list)
        if selected_em:
            st.subheader(f"📋 First Aid: {selected_em}")
            for step in FIRST_AID_GUIDELINES[selected_em]:
                st.write(f"✅ {step}")

    elif em_type == "Natural Disaster":
        disasters = list(EMERGENCY_GUIDELINES.keys())
        selected = st.selectbox("Select disaster:", disasters)
        if selected:
            st.subheader(f"📋 Safety Tips: {selected}")
            for tip in EMERGENCY_GUIDELINES[selected]:
                st.write(f"✅ {tip}")

with tab3:
    st.header("🌍 Find Doctors Near You")
    doc_type = st.selectbox("What kind of doctor do you need?", [
        "General Physician", "Dermatologist", "Cardiologist", "Gynecologist",
        "Dentist", "ENT Specialist", "Pediatrician", "Neurologist", "Orthopedic", "Urologist"])
    city = st.text_input("Enter your city (e.g., Kolkata):")
    if st.button("🔍 Search Doctors"):
        if city:
            with st.spinner("Searching doctors near you..."):
                doctor_results = get_real_doctors(doc_type + " doctor", city)
                if doctor_results:
                    st.markdown(f"### Top {doc_type}s in {city}:")
                    for d in doctor_results:
                        st.write(f"**{d['name']}**\n📍 {d['address']}\n⭐ Rating: {d['rating']}")
                else:
                    st.error("No doctors found. Try a different city.")
        else:
            st.warning("Please enter a city name.")

with tab4:
    st.header("🚑 Emergency Hospital & Ambulance")
    city = st.text_input("Enter your city for emergency help:", key="emergency_city")
    if st.button("🚨 Find Nearby Hospitals"):
        if city:
            with st.spinner("Searching hospitals near you..."):
                hospitals = get_nearest_hospitals(city)
                if hospitals:
                    st.markdown(f"### 🏥 Hospitals in {city}:")
                    for h in hospitals:
                        st.write(f"**{h['name']}**\n📍 {h['address']}\n⭐ Rating: {h['rating']}")
                else:
                    st.error("No hospitals found.")
        else:
            st.warning("Please enter a city.")
    st.markdown("---")
    st.markdown("### 📞 Emergency Ambulance Numbers (India)")
    st.markdown("- **102** — Govt. Ambulance\n- **108** — Emergency Helpline\n- **112** — Universal emergency number")

with tab5:
    st.header("💬 Chat with Mr. Doctor")
    st.markdown("🤖 Ask anything about health, medicines, food, or emergencies!")

    from io import StringIO
    import speech_recognition as sr

    def recognize_speech():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            st.info("🎤 Listening... Please speak clearly.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand.")
        except sr.RequestError as e:
            st.error(f"API Error: {e}")
        return ""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Use a form instead of st.chat_input
    with st.form("chat_form"):
        user_message = st.text_input("Type your question for Mr. Doctor")
        voice_trigger = st.form_submit_button("🎙️ Use Voice Instead")
        text_trigger = st.form_submit_button("🧠 Ask Mr. Doctor")

    if voice_trigger:
        spoken = recognize_speech()
        if spoken:
            user_message = spoken

    if text_trigger or (voice_trigger and user_message):
        with st.spinner("Mr. Doctor is typing..."):
            st.session_state.chat_history.append({"role": "user", "content": user_message})

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.chat_history
                )
                reply = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            except Exception as e:
                reply = f"❌ Error: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Display the chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
with tab6:
    st.header("📜 My Diagnosis History")

    if "user" in st.session_state and st.session_state["user"]:
        user_email = st.session_state["user"]["email"]

        history = st.session_state["diagnosis_history"].get(user_email, [])

        if history:
            for entry in history:
                st.markdown(f"**🗓 {entry['datetime']}** — **{entry['disease']}**")
                st.markdown(f"- **Name:** {entry['name']}")
                st.markdown(f"- **Age:** {entry['age']} | **Gender:** {entry['gender']}")
                st.markdown(f"- **Symptoms:** {', '.join(entry['symptoms'])}")
                st.markdown("---")
        else:
            st.info("No diagnosis history found.")

        if st.button("🗑️ Clear My History"):
            st.session_state["diagnosis_history"][user_email] = []
            st.success("✅ Your diagnosis history has been cleared.")
    else:
        st.warning("🔐 Please log in to view your history.")
with tab7:
    st.header("📺 Doctor Advice — Coming Soon")
    
    st.markdown("""
    We are building a **trusted medical video library** to give you:
    - ✅ Quick advice from real doctors  
    - 🩺 Guidance on common conditions (like fever, cough, cold)  
    - 🚑 First-aid steps for emergencies  
    - 🛡️ Survival tips for natural disasters  
    
    📌 *Our team is curating and verifying each video for authenticity.*  
    This feature is currently **under development** — please check back soon.
    """)

    st.info("💡 You will soon be able to watch and learn from short, doctor-approved videos right here.")

    # Optional: Notification signup
    with st.expander("🔔 Notify me when Doctor Advice is available"):
        notify_email = st.text_input("Enter your email to get notified:", key="notify_email_doctor_advice")
        if st.button("📩 Add me to notification list"):
            if notify_email.strip():
                st.session_state.setdefault("doctor_advice_notify", [])
                if notify_email not in st.session_state["doctor_advice_notify"]:
                    st.session_state["doctor_advice_notify"].append(notify_email)
                    st.success("✅ You'll be notified when Doctor Advice launches!")
                else:
                    st.info("ℹ️ You're already on the notification list.")
            else:
                st.warning("⚠️ Please enter a valid email.")


with tab8:
    st.header("streamlit run ai_doctor_app.pyℹ️ About AI Doctor")
    st.markdown("""
    AI Doctor is a virtual health assistant developed for learning and hackathons. It helps users:
    - Diagnose illnesses based on symptoms
    - Recommend medicines, tests, and food (only for ages 15–60)
    - Survive emergency situations
    - Locate real doctors using Google Maps
    - Estimate your health via BMI alerts
    - 🚑 Find emergency hospitals and ambulance helpline
    - 💬 Ask chatbot Mr. Doctor for help

    **Developer:** Raj Mallick  
    **Tech Stack:** Python + Streamlit + OpenAI + Google Maps API
    """)

    st.markdown("---")
    st.subheader("📣 We'd love your feedback!")
    with st.expander("📝 Give Feedback via Google Form"):
        st.markdown("Please fill out the form below to help us improve:")
        st.components.v1.iframe(
            src="https://docs.google.com/forms/d/e/1FAIpQLSeAhlSlqyiCIvA_25h-Fa2TFj5UuIFh7j-0U2ZJ2nIwX_KJWw/viewform?usp=dialog",
            height=600
        )

