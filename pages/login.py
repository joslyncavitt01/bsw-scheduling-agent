"""
Patient Login - Demo patient selection for BSW Scheduling Agent.

This page allows demo users to select a patient profile to "login" with.
In a production system, this would be replaced with actual authentication.
"""

import streamlit as st
from datetime import datetime
from mock_data import PATIENTS, get_patient_by_id

# Page configuration
st.set_page_config(
    page_title="Patient Login - BSW Scheduling Agent",
    page_icon="",
    layout="wide"
)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">Patient Login</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
        Select a demo patient profile to begin scheduling
    </p>
</div>
""", unsafe_allow_html=True)

# Check if already logged in
if st.session_state.get("logged_in_patient"):
    patient = st.session_state.logged_in_patient

    st.success(f"You are currently logged in as **{patient.first_name} {patient.last_name}**")

    col1, col2 = st.columns([3, 1])

    with col1:
        with st.expander("View Patient Information", expanded=True):
            st.markdown(f"""
            **Patient ID**: {patient.patient_id}
            **Name**: {patient.first_name} {patient.last_name}
            **Date of Birth**: {patient.date_of_birth}
            **Age**: {patient.age}
            **Gender**: {patient.gender}

            **Contact**
            Phone: {patient.phone}
            Email: {patient.email}

            **Address**
            {patient.address}
            {patient.city}, {patient.state} {patient.zip_code}

            **Insurance**
            Provider: {patient.insurance_provider}
            ID: {patient.insurance_id}

            **Medical History**
            Conditions: {', '.join(patient.medical_conditions) if patient.medical_conditions else 'None'}
            Allergies: {', '.join(patient.allergies) if patient.allergies else 'None'}
            Medications: {', '.join(patient.medications) if patient.medications else 'None'}
            """)

    with col2:
        st.markdown("### Actions")

        if st.button("Start Scheduling", use_container_width=True, type="primary"):
            st.switch_page("pages/chat.py")

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in_patient = None
            st.session_state.messages = []
            st.session_state.current_agent = "router"
            st.rerun()

else:
    # Login form
    st.markdown("### Select Demo Patient")

    st.info("""
    **Demo System Notice**

    This is a demonstration system with sample patient profiles.
    Select a patient below to experience the AI scheduling assistant.
    """)

    # Create patient options
    patient_options = []
    for patient in PATIENTS:
        label = f"{patient.first_name} {patient.last_name} - {patient.city}, {patient.state}"
        patient_options.append((label, patient))

    # Display patients in a more user-friendly way
    st.markdown("#### Available Demo Patients")

    for i, (label, patient) in enumerate(patient_options):
        with st.expander(f"👤 {label}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"""
                **ID**: {patient.patient_id}
                **DOB**: {patient.date_of_birth} (Age {patient.age})
                **Location**: {patient.city}, {patient.state}
                **Insurance**: {patient.insurance_provider}
                **Medical Conditions**: {', '.join(patient.medical_conditions) if patient.medical_conditions else 'None'}
                """)

            with col2:
                if st.button(f"Login as {patient.first_name}", key=f"login_{patient.patient_id}", use_container_width=True):
                    # Set the logged-in patient
                    st.session_state.logged_in_patient = patient
                    st.session_state.messages = []
                    st.session_state.current_agent = "router"
                    st.session_state.conversation_start_time = None
                    st.success(f"Logged in as {patient.first_name} {patient.last_name}!")
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    <p>BSW Health AI Scheduling Agent Demo</p>
    <p style="font-size: 0.8rem;">In a production system, patients would authenticate with MyChart credentials.</p>
</div>
""", unsafe_allow_html=True)
