"""
Mock healthcare data for BSW scheduling agent demo.
Realistic patient profiles, provider data, and scheduling information for Texas healthcare system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


@dataclass
class Patient:
    """Patient profile with demographics and medical history."""
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    age: int
    gender: str
    phone: str
    email: str
    address: str
    city: str
    state: str
    zip_code: str
    insurance_provider: str
    insurance_id: str
    primary_care_provider: Optional[str]
    medical_conditions: List[str]
    allergies: List[str]
    medications: List[str]
    recent_visits: List[Dict[str, str]]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.patient_id})"

    def has_seen_provider(self, provider_id: str) -> bool:
        """Check if patient has previously seen this provider."""
        return any(visit.get("provider") == provider_id for visit in self.recent_visits)

    def is_new_to_bsw(self) -> bool:
        """Check if patient is new to BSW Health system."""
        return len(self.recent_visits) == 0


@dataclass
class Provider:
    """Healthcare provider profile with specialty and availability."""
    provider_id: str
    first_name: str
    last_name: str
    specialty: str
    sub_specialty: Optional[str]
    credentials: str
    location: str
    address: str
    city: str
    phone: str
    accepting_new_patients: bool
    languages: List[str]
    insurance_accepted: List[str]
    availability_days: List[str]
    typical_slot_duration: int  # minutes
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}, {self.credentials} - {self.specialty}"


@dataclass
class AppointmentSlot:
    """Available appointment time slot."""
    slot_id: str
    provider_id: str
    date: str
    time: str
    duration: int  # minutes
    appointment_type: str
    is_available: bool
    location: str


@dataclass
class InsurancePolicy:
    """Insurance coverage rules and requirements."""
    insurance_name: str
    policy_type: str
    requires_referral: List[str]  # specialties requiring referral
    requires_prior_auth: List[str]  # procedures requiring prior authorization
    copay_specialist: float
    copay_primary: float
    deductible: float
    out_of_pocket_max: float
    covered_services: List[str]
    notes: str


@dataclass
class ClinicalProtocol:
    """Clinical scheduling guidelines and protocols."""
    protocol_id: str
    name: str
    specialty: str
    condition: str
    recommended_follow_up: str  # e.g., "2 weeks post-op"
    urgency_level: str  # routine, urgent, emergent
    special_instructions: str


# PATIENTS
PATIENTS = [
    Patient(
        patient_id="PT001",
        first_name="Sarah",
        last_name="Martinez",
        date_of_birth="1978-03-15",
        age=47,
        gender="Female",
        phone="214-555-0123",
        email="sarah.martinez@email.com",
        address="4521 Oak Lawn Ave",
        city="Dallas",
        state="TX",
        zip_code="75219",
        insurance_provider="Blue Cross Blue Shield",
        insurance_id="BCBS-TX-445821",
        primary_care_provider="DR006",
        medical_conditions=["Osteoarthritis", "Hypertension"],
        allergies=["Penicillin"],
        medications=["Lisinopril 10mg", "Ibuprofen 400mg PRN"],
        recent_visits=[
            {
                "date": "2024-10-10",
                "provider": "DR003",
                "specialty": "Orthopedic Surgery",
                "reason": "Right knee replacement surgery",
                "notes": "Post-op follow-up needed in 2 weeks"
            }
        ]
    ),
    Patient(
        patient_id="PT002",
        first_name="James",
        last_name="Wilson",
        date_of_birth="1945-07-22",
        age=80,
        gender="Male",
        phone="817-555-0198",
        email="j.wilson@email.com",
        address="2100 West Pioneer Pkwy",
        city="Arlington",
        state="TX",
        zip_code="76013",
        insurance_provider="Medicare",
        insurance_id="MED-1234567890A",
        primary_care_provider="DR007",
        medical_conditions=["Coronary Artery Disease", "Type 2 Diabetes", "Hyperlipidemia"],
        allergies=["None"],
        medications=["Metformin 1000mg", "Atorvastatin 40mg", "Aspirin 81mg"],
        recent_visits=[
            {
                "date": "2024-09-15",
                "provider": "DR007",
                "specialty": "Primary Care",
                "reason": "Chest pain evaluation",
                "notes": "Referred to cardiology for stress test"
            }
        ]
    ),
    Patient(
        patient_id="PT003",
        first_name="Lisa",
        last_name="Chen",
        date_of_birth="1992-11-08",
        age=32,
        gender="Female",
        phone="512-555-0234",
        email="lisa.chen@email.com",
        address="1500 Red River St",
        city="Austin",
        state="TX",
        zip_code="78701",
        insurance_provider="Aetna",
        insurance_id="AET-TX-889234",
        primary_care_provider="DR009",
        medical_conditions=["Anxiety"],
        allergies=["Latex"],
        medications=["Sertraline 50mg"],
        recent_visits=[
            {
                "date": "2024-08-20",
                "provider": "DR009",
                "specialty": "Primary Care",
                "reason": "Annual wellness exam",
                "notes": "Healthy, routine follow-up in 1 year"
            }
        ]
    ),
    Patient(
        patient_id="PT004",
        first_name="Michael",
        last_name="Thompson",
        date_of_birth="1985-05-30",
        age=39,
        gender="Male",
        phone="972-555-0156",
        email="m.thompson@email.com",
        address="7890 Legacy Dr",
        city="Plano",
        state="TX",
        zip_code="75024",
        insurance_provider="United Healthcare",
        insurance_id="UHC-445123789",
        primary_care_provider="DR008",
        medical_conditions=["None"],
        allergies=["None"],
        medications=["None"],
        recent_visits=[]
    ),
    Patient(
        patient_id="PT005",
        first_name="Maria",
        last_name="Rodriguez",
        date_of_birth="1960-02-14",
        age=64,
        gender="Female",
        phone="210-555-0167",
        email="maria.rodriguez@email.com",
        address="3456 Blanco Rd",
        city="San Antonio",
        state="TX",
        zip_code="78212",
        insurance_provider="Medicaid",
        insurance_id="MCAID-TX-556789",
        primary_care_provider="DR010",
        medical_conditions=["Rheumatoid Arthritis", "Osteoporosis"],
        allergies=["Sulfa drugs"],
        medications=["Methotrexate 15mg weekly", "Folic acid 1mg", "Calcium with Vitamin D"],
        recent_visits=[
            {
                "date": "2024-09-01",
                "provider": "DR002",
                "specialty": "Orthopedic Surgery",
                "reason": "Hip pain evaluation",
                "notes": "Considering hip replacement, follow-up in 3 months"
            }
        ]
    ),
    Patient(
        patient_id="PT006",
        first_name="Robert",
        last_name="Johnson",
        date_of_birth="1972-09-25",
        age=52,
        gender="Male",
        phone="469-555-0189",
        email="robert.j@email.com",
        address="9012 Preston Rd",
        city="Frisco",
        state="TX",
        zip_code="75034",
        insurance_provider="Blue Cross Blue Shield",
        insurance_id="BCBS-TX-992341",
        primary_care_provider="DR006",
        medical_conditions=["Atrial Fibrillation", "Hypertension", "Sleep Apnea"],
        allergies=["None"],
        medications=["Eliquis 5mg", "Metoprolol 50mg", "CPAP at night"],
        recent_visits=[
            {
                "date": "2024-10-01",
                "provider": "DR011",
                "specialty": "Cardiology",
                "reason": "A-fib monitoring",
                "notes": "Stable, continue current medications, follow-up in 6 months"
            }
        ]
    ),
    Patient(
        patient_id="PT007",
        first_name="Emily",
        last_name="Davis",
        date_of_birth="1998-12-03",
        age=26,
        gender="Female",
        phone="713-555-0145",
        email="emily.davis@email.com",
        address="1234 Westheimer Rd",
        city="Houston",
        state="TX",
        zip_code="77006",
        insurance_provider="Aetna",
        insurance_id="AET-TX-334567",
        primary_care_provider="DR010",
        medical_conditions=["None"],
        allergies=["Peanuts"],
        medications=["Epipen PRN"],
        recent_visits=[
            {
                "date": "2024-07-15",
                "provider": "DR004",
                "specialty": "Orthopedic Surgery",
                "reason": "Ankle sprain from sports",
                "notes": "Healed well, cleared for full activity"
            }
        ]
    )
]

# PROVIDERS
PROVIDERS = [
    # Orthopedic Specialists
    Provider(
        provider_id="DR001",
        first_name="David",
        last_name="Anderson",
        specialty="Orthopedic Surgery",
        sub_specialty="Joint Replacement",
        credentials="MD, FAAOS",
        location="BSW Medical Center - Dallas",
        address="3500 Gaston Ave",
        city="Dallas",
        phone="214-820-0111",
        accepting_new_patients=True,
        languages=["English", "Spanish"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Thursday", "Friday"],
        typical_slot_duration=30
    ),
    Provider(
        provider_id="DR002",
        first_name="Jennifer",
        last_name="Kim",
        specialty="Orthopedic Surgery",
        sub_specialty="Sports Medicine",
        credentials="MD, FAAOS",
        location="BSW Orthopedic & Spine Hospital - Arlington",
        address="1301 Brown Blvd",
        city="Arlington",
        phone="817-468-9100",
        accepting_new_patients=True,
        languages=["English", "Korean"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare"],
        availability_days=["Monday", "Wednesday", "Friday"],
        typical_slot_duration=30
    ),
    Provider(
        provider_id="DR003",
        first_name="Robert",
        last_name="Martinez",
        specialty="Orthopedic Surgery",
        sub_specialty="Joint Replacement",
        credentials="MD, FAAOS",
        location="BSW Medical Center - Plano",
        address="4708 Alliance Blvd",
        city="Plano",
        phone="469-814-4000",
        accepting_new_patients=False,
        languages=["English", "Spanish"],
        insurance_accepted=["Blue Cross Blue Shield", "United Healthcare", "Medicare"],
        availability_days=["Tuesday", "Wednesday", "Thursday"],
        typical_slot_duration=30
    ),
    Provider(
        provider_id="DR004",
        first_name="Sarah",
        last_name="Williams",
        specialty="Orthopedic Surgery",
        sub_specialty="Foot and Ankle",
        credentials="MD",
        location="BSW Medical Center - Temple",
        address="2401 South 31st St",
        city="Temple",
        phone="254-724-2111",
        accepting_new_patients=True,
        languages=["English"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Friday"],
        typical_slot_duration=30
    ),
    
    # Cardiologists
    Provider(
        provider_id="DR011",
        first_name="Michael",
        last_name="Patel",
        specialty="Cardiology",
        sub_specialty="Interventional Cardiology",
        credentials="MD, FACC",
        location="BSW Heart & Vascular Hospital - Dallas",
        address="621 North Hall St",
        city="Dallas",
        phone="214-820-7500",
        accepting_new_patients=True,
        languages=["English", "Hindi", "Gujarati"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Thursday"],
        typical_slot_duration=45
    ),
    Provider(
        provider_id="DR012",
        first_name="Elizabeth",
        last_name="Thompson",
        specialty="Cardiology",
        sub_specialty="Electrophysiology",
        credentials="MD, FACC, FHRS",
        location="BSW Medical Center - Plano",
        address="4708 Alliance Blvd",
        city="Plano",
        phone="469-814-4100",
        accepting_new_patients=True,
        languages=["English"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare"],
        availability_days=["Tuesday", "Wednesday", "Thursday", "Friday"],
        typical_slot_duration=45
    ),
    Provider(
        provider_id="DR013",
        first_name="James",
        last_name="Lee",
        specialty="Cardiology",
        sub_specialty="Heart Failure",
        credentials="MD, FACC",
        location="BSW Medical Center - Temple",
        address="2401 South 31st St",
        city="Temple",
        phone="254-724-2200",
        accepting_new_patients=False,
        languages=["English", "Mandarin"],
        insurance_accepted=["Blue Cross Blue Shield", "United Healthcare", "Medicare"],
        availability_days=["Monday", "Wednesday", "Thursday"],
        typical_slot_duration=45
    ),
    Provider(
        provider_id="DR014",
        first_name="Amanda",
        last_name="Garcia",
        specialty="Cardiology",
        sub_specialty="General Cardiology",
        credentials="MD, FACC",
        location="BSW Medical Center - Round Rock",
        address="300 University Blvd",
        city="Round Rock",
        phone="512-509-0100",
        accepting_new_patients=True,
        languages=["English", "Spanish"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Thursday", "Friday"],
        typical_slot_duration=45
    ),
    
    # Primary Care Physicians
    Provider(
        provider_id="DR006",
        first_name="Rachel",
        last_name="Foster",
        specialty="Primary Care",
        sub_specialty="Internal Medicine",
        credentials="MD",
        location="BSW Family Health Center - Dallas",
        address="3600 Gaston Ave",
        city="Dallas",
        phone="214-820-2000",
        accepting_new_patients=True,
        languages=["English"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        typical_slot_duration=20
    ),
    Provider(
        provider_id="DR007",
        first_name="Daniel",
        last_name="Brown",
        specialty="Primary Care",
        sub_specialty="Family Medicine",
        credentials="MD",
        location="BSW Family Health Center - Arlington",
        address="2200 South Cooper St",
        city="Arlington",
        phone="817-468-9200",
        accepting_new_patients=True,
        languages=["English", "Spanish"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        typical_slot_duration=20
    ),
    Provider(
        provider_id="DR008",
        first_name="Susan",
        last_name="White",
        specialty="Primary Care",
        sub_specialty="Internal Medicine",
        credentials="DO",
        location="BSW Family Health Center - Plano",
        address="6800 West Parker Rd",
        city="Plano",
        phone="469-814-5000",
        accepting_new_patients=False,
        languages=["English"],
        insurance_accepted=["Blue Cross Blue Shield", "United Healthcare", "Medicare"],
        availability_days=["Monday", "Wednesday", "Thursday", "Friday"],
        typical_slot_duration=20
    ),
    Provider(
        provider_id="DR009",
        first_name="Kevin",
        last_name="Nguyen",
        specialty="Primary Care",
        sub_specialty="Family Medicine",
        credentials="MD",
        location="BSW Family Health Center - Round Rock",
        address="4200 Marathon Blvd",
        city="Round Rock",
        phone="512-509-0200",
        accepting_new_patients=True,
        languages=["English", "Vietnamese"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        typical_slot_duration=20
    ),
    Provider(
        provider_id="DR010",
        first_name="Patricia",
        last_name="Miller",
        specialty="Primary Care",
        sub_specialty="Geriatric Medicine",
        credentials="MD",
        location="BSW Family Health Center - Temple",
        address="2700 South Clear Creek Rd",
        city="Temple",
        phone="254-724-3000",
        accepting_new_patients=True,
        languages=["English", "Spanish"],
        insurance_accepted=["Blue Cross Blue Shield", "Aetna", "United Healthcare", "Medicare", "Medicaid"],
        availability_days=["Monday", "Tuesday", "Wednesday", "Thursday"],
        typical_slot_duration=30
    )
]

# INSURANCE POLICIES
INSURANCE_POLICIES = [
    InsurancePolicy(
        insurance_name="Blue Cross Blue Shield of Texas",
        policy_type="PPO",
        requires_referral=["Cardiology", "Orthopedic Surgery", "Neurology"],
        requires_prior_auth=["MRI", "CT Scan", "Surgery", "Specialty Medications"],
        copay_specialist=60.0,
        copay_primary=30.0,
        deductible=1500.0,
        out_of_pocket_max=6000.0,
        covered_services=["Preventive care", "Specialist visits", "Surgery", "Imaging", "Lab work"],
        notes="Requires PCP selection. Referrals must be obtained before specialist visits."
    ),
    InsurancePolicy(
        insurance_name="Aetna",
        policy_type="HMO",
        requires_referral=["All Specialists"],
        requires_prior_auth=["MRI", "CT Scan", "Surgery", "Specialty Medications", "Durable Medical Equipment"],
        copay_specialist=50.0,
        copay_primary=25.0,
        deductible=1000.0,
        out_of_pocket_max=5000.0,
        covered_services=["Preventive care", "Specialist visits", "Surgery", "Imaging", "Lab work"],
        notes="Strict referral requirements. All specialist visits require PCP referral within last 90 days."
    ),
    InsurancePolicy(
        insurance_name="United Healthcare",
        policy_type="PPO",
        requires_referral=[],
        requires_prior_auth=["Surgery", "Advanced Imaging", "Specialty Medications"],
        copay_specialist=50.0,
        copay_primary=25.0,
        deductible=2000.0,
        out_of_pocket_max=7000.0,
        covered_services=["Preventive care", "Specialist visits", "Surgery", "Imaging", "Lab work"],
        notes="No referral required for specialists. Prior auth required for elective procedures."
    ),
    InsurancePolicy(
        insurance_name="Medicare",
        policy_type="Federal Insurance",
        requires_referral=[],
        requires_prior_auth=["Part B Drugs", "Durable Medical Equipment", "Home Health"],
        copay_specialist=0.0,
        copay_primary=0.0,
        deductible=226.0,
        out_of_pocket_max=0.0,
        covered_services=["Preventive care", "Specialist visits", "Surgery", "Imaging", "Lab work", "Hospital care"],
        notes="No referral required. Part B covers outpatient services. 20% coinsurance after deductible."
    ),
    InsurancePolicy(
        insurance_name="Medicaid",
        policy_type="State Insurance",
        requires_referral=["All Specialists"],
        requires_prior_auth=["MRI", "CT Scan", "Surgery", "Specialty Medications", "DME"],
        copay_specialist=0.0,
        copay_primary=0.0,
        deductible=0.0,
        out_of_pocket_max=0.0,
        covered_services=["Preventive care", "Specialist visits", "Surgery", "Imaging", "Lab work", "Prescriptions"],
        notes="Must have active Medicaid eligibility. PCP referral required for all specialist visits."
    )
]

# CLINICAL PROTOCOLS
CLINICAL_PROTOCOLS = [
    ClinicalProtocol(
        protocol_id="PROTO001",
        name="Post-Operative Knee Replacement Follow-up",
        specialty="Orthopedic Surgery",
        condition="Knee Replacement (Post-Op)",
        recommended_follow_up="2 weeks post-surgery, then 6 weeks, then 3 months",
        urgency_level="routine",
        special_instructions="Check incision healing, assess range of motion, review physical therapy progress. Patient should bring PT notes."
    ),
    ClinicalProtocol(
        protocol_id="PROTO002",
        name="Post-Operative Hip Replacement Follow-up",
        specialty="Orthopedic Surgery",
        condition="Hip Replacement (Post-Op)",
        recommended_follow_up="2 weeks post-surgery, then 6 weeks, then 3 months, then annually",
        urgency_level="routine",
        special_instructions="X-ray required at 6-week and 3-month visits. Assess gait and hip precautions compliance."
    ),
    ClinicalProtocol(
        protocol_id="PROTO003",
        name="Cardiac Stress Test Follow-up",
        specialty="Cardiology",
        condition="Abnormal Stress Test",
        recommended_follow_up="Within 1 week of test results",
        urgency_level="urgent",
        special_instructions="Discuss test results, potential need for cardiac catheterization. NPO not required for consultation."
    ),
    ClinicalProtocol(
        protocol_id="PROTO004",
        name="Atrial Fibrillation Monitoring",
        specialty="Cardiology",
        condition="Atrial Fibrillation",
        recommended_follow_up="Every 3-6 months based on stability",
        urgency_level="routine",
        special_instructions="Check INR if on warfarin. Review medication compliance and symptoms. EKG at each visit."
    ),
    ClinicalProtocol(
        protocol_id="PROTO005",
        name="Heart Failure Management",
        specialty="Cardiology",
        condition="Congestive Heart Failure",
        recommended_follow_up="Every 1-3 months based on NYHA class",
        urgency_level="urgent",
        special_instructions="Daily weights monitoring. Check BNP levels. Assess fluid status and medication adjustment."
    ),
    ClinicalProtocol(
        protocol_id="PROTO006",
        name="Diabetes Management",
        specialty="Primary Care",
        condition="Type 2 Diabetes",
        recommended_follow_up="Every 3 months",
        urgency_level="routine",
        special_instructions="Fasting labs required (A1C, lipid panel, CMP). Review blood glucose logs. Foot exam annually."
    ),
    ClinicalProtocol(
        protocol_id="PROTO007",
        name="Hypertension Follow-up",
        specialty="Primary Care",
        condition="Hypertension",
        recommended_follow_up="Every 3-6 months based on control",
        urgency_level="routine",
        special_instructions="Bring home blood pressure log. Review medication compliance and side effects."
    ),
    ClinicalProtocol(
        protocol_id="PROTO008",
        name="Annual Wellness Visit",
        specialty="Primary Care",
        condition="Preventive Care",
        recommended_follow_up="Annually",
        urgency_level="routine",
        special_instructions="Fasting labs recommended. Update immunizations. Age-appropriate cancer screenings."
    ),
    ClinicalProtocol(
        protocol_id="PROTO009",
        name="Sports Injury Follow-up",
        specialty="Orthopedic Surgery",
        condition="Acute Sports Injury",
        recommended_follow_up="2-4 weeks based on injury severity",
        urgency_level="routine",
        special_instructions="Imaging may be required. Assess healing progress and return-to-play readiness."
    ),
    ClinicalProtocol(
        protocol_id="PROTO010",
        name="Chest Pain Evaluation",
        specialty="Cardiology",
        condition="Chest Pain",
        recommended_follow_up="Within 1 week if stable, same day if concerning features",
        urgency_level="urgent",
        special_instructions="Patient should go to ER for acute/severe symptoms. Otherwise schedule urgent cardiology eval."
    )
]


def generate_appointment_slots(provider: Provider, days_ahead: int = 30) -> List[AppointmentSlot]:
    """Generate available appointment slots for a provider."""
    slots = []
    slot_counter = 1

    # Define specialty-specific appointment types
    appointment_types_by_specialty = {
        "Orthopedic Surgery": [
            "New Patient Consultation",
            "Post-Operative Follow-up",
            "Fracture Follow-up",
            "Joint Injection",
            "Surgical Consult"
        ],
        "Cardiology": [
            "New Patient Consultation",
            "Heart Failure Follow-up",
            "A-fib Management",
            "Post-Procedure Follow-up",
            "Annual Cardiology Exam"
        ],
        "Primary Care": [
            "New Patient Physical",
            "Annual Wellness Visit",
            "Sick Visit",
            "Chronic Disease Management",
            "Follow-up Visit"
        ]
    }

    # Get appropriate appointment types for this provider's specialty
    appointment_types = appointment_types_by_specialty.get(
        provider.specialty,
        ["New Patient", "Follow-up"]  # Default fallback
    )

    today = datetime.now()
    for day_offset in range(1, days_ahead + 1):
        date = today + timedelta(days=day_offset)
        day_name = date.strftime("%A")

        if day_name not in provider.availability_days:
            continue

        # Morning slots: 8:00 AM - 12:00 PM
        # Afternoon slots: 1:00 PM - 5:00 PM
        time_slots = []

        # Morning slots
        for hour in range(8, 12):
            for minute in [0, 30] if provider.typical_slot_duration <= 30 else [0]:
                time_slots.append(f"{hour:02d}:{minute:02d}")

        # Afternoon slots
        for hour in range(13, 17):
            for minute in [0, 30] if provider.typical_slot_duration <= 30 else [0]:
                time_slots.append(f"{hour:02d}:{minute:02d}")

        for time_slot in time_slots:
            # Randomly mark some slots as unavailable (simulate realistic booking)
            is_available = random.random() > 0.3  # 70% available

            # Select appropriate appointment type
            appointment_type = random.choice(appointment_types)

            slot = AppointmentSlot(
                slot_id=f"SLOT-{provider.provider_id}-{slot_counter:04d}",
                provider_id=provider.provider_id,
                date=date.strftime("%Y-%m-%d"),
                time=time_slot,
                duration=provider.typical_slot_duration,
                appointment_type=appointment_type,
                is_available=is_available,
                location=provider.location
            )
            slots.append(slot)
            slot_counter += 1

    return slots


def get_patient_by_id(patient_id: str) -> Optional[Patient]:
    """Retrieve patient by ID."""
    for patient in PATIENTS:
        if patient.patient_id == patient_id:
            return patient
    return None


def get_provider_by_id(provider_id: str) -> Optional[Provider]:
    """Retrieve provider by ID."""
    for provider in PROVIDERS:
        if provider.provider_id == provider_id:
            return provider
    return None


def get_providers_by_specialty(specialty: str) -> List[Provider]:
    """Get all providers for a given specialty."""
    return [p for p in PROVIDERS if p.specialty == specialty]


def get_insurance_policy(insurance_name: str) -> Optional[InsurancePolicy]:
    """Get insurance policy details by name."""
    for policy in INSURANCE_POLICIES:
        if insurance_name.lower() in policy.insurance_name.lower():
            return policy
    return None


def get_clinical_protocol(condition: str) -> Optional[ClinicalProtocol]:
    """Get clinical protocol for a condition."""
    for protocol in CLINICAL_PROTOCOLS:
        if condition.lower() in protocol.condition.lower() or condition.lower() in protocol.name.lower():
            return protocol
    return None


def get_patient_status_for_provider(patient: Patient, provider_id: str) -> str:
    """
    Determine patient status for a specific provider.

    Returns:
        - "New to BSW" - Patient has never been to BSW Health
        - "Established - New to Provider" - Patient has BSW history but not with this provider
        - "Established with Provider" - Patient has seen this provider before
    """
    if patient.is_new_to_bsw():
        return "New to BSW"
    elif patient.has_seen_provider(provider_id):
        return "Established with Provider"
    else:
        return "Established - New to Provider"


# Generate all appointment slots for all providers
ALL_APPOINTMENT_SLOTS = []
for provider in PROVIDERS:
    ALL_APPOINTMENT_SLOTS.extend(generate_appointment_slots(provider, days_ahead=14))


if __name__ == "__main__":
    print("BSW Health Scheduling Agent - Mock Data Summary\n")
    print(f"Total Patients: {len(PATIENTS)}")
    print(f"Total Providers: {len(PROVIDERS)}")
    print(f"  - Orthopedic: {len(get_providers_by_specialty('Orthopedic Surgery'))}")
    print(f"  - Cardiology: {len(get_providers_by_specialty('Cardiology'))}")
    print(f"  - Primary Care: {len(get_providers_by_specialty('Primary Care'))}")
    print(f"Total Insurance Policies: {len(INSURANCE_POLICIES)}")
    print(f"Total Clinical Protocols: {len(CLINICAL_PROTOCOLS)}")
    print(f"Total Appointment Slots Generated: {len(ALL_APPOINTMENT_SLOTS)}")
    print(f"  - Available: {sum(1 for s in ALL_APPOINTMENT_SLOTS if s.is_available)}")
    print(f"  - Booked: {sum(1 for s in ALL_APPOINTMENT_SLOTS if not s.is_available)}")


