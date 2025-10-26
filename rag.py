"""
RAG System for Healthcare Policy Retrieval using ChromaDB.

This module implements a production-ready retrieval-augmented generation (RAG) system
for healthcare policies, insurance coverage rules, and clinical scheduling protocols.
Uses ChromaDB for vector storage and semantic search.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Healthcare Policy Documents
HEALTHCARE_POLICIES = [
    # ============================================================================
    # INSURANCE COVERAGE POLICIES
    # ============================================================================
    {
        "id": "policy_bcbs_001",
        "category": "insurance_coverage",
        "insurance_provider": "Blue Cross Blue Shield",
        "title": "BCBS Specialist Referral Requirements",
        "content": """
Blue Cross Blue Shield of Texas (BCBS TX) PPO Plan - Specialist Referral Policy

REFERRAL REQUIREMENTS:
- Cardiology: Requires PCP referral before first appointment
- Orthopedic Surgery: Requires PCP referral before first appointment
- Neurology: Requires PCP referral before first appointment
- All other specialists: No referral required for PPO members

REFERRAL VALIDITY:
- Referrals are valid for 90 days from issue date
- Referrals must be obtained BEFORE the specialist appointment
- Emergency/urgent care does not require referral

PROCESS:
1. Patient schedules with PCP to obtain referral
2. PCP submits referral electronically or by fax
3. Specialist's office verifies referral before appointment
4. If no referral on file, appointment may be rescheduled

COPAY AMOUNTS:
- Specialist visit copay: $60
- Primary care visit copay: $30
- Copay due at time of service

IMPORTANT: Patients should verify referral is on file before specialist appointment date.
        """,
        "metadata": {
            "policy_type": "referral_requirements",
            "specialties": ["Cardiology", "Orthopedic Surgery", "Neurology"],
            "plan_type": "PPO"
        }
    },
    {
        "id": "policy_bcbs_002",
        "category": "insurance_coverage",
        "insurance_provider": "Blue Cross Blue Shield",
        "title": "BCBS Prior Authorization Requirements",
        "content": """
Blue Cross Blue Shield of Texas - Prior Authorization Policy

SERVICES REQUIRING PRIOR AUTHORIZATION:
- All surgical procedures (inpatient and outpatient)
- MRI scans (all body parts)
- CT scans (all body parts)
- Advanced imaging (PET scans, nuclear medicine)
- Specialty medications and biologics
- Durable medical equipment (DME) over $500
- Home health services
- Inpatient rehabilitation stays

AUTHORIZATION TIMELINE:
- Elective procedures: Submit 5-7 business days in advance
- Urgent procedures: 24-48 hour review available
- Emergency procedures: Notification within 48 hours post-procedure

PROCESS:
1. Provider's office submits authorization request with clinical documentation
2. BCBS medical review team evaluates medical necessity
3. Authorization decision within 3-5 business days
4. Approval valid for 60 days from issue date

DENIAL APPEALS:
- Peer-to-peer review available for denials
- Standard appeal process: 30 days from denial
- Expedited appeal for urgent cases: 72 hours

NOTE: Services performed without required authorization may not be covered.
        """,
        "metadata": {
            "policy_type": "prior_authorization",
            "services": ["Surgery", "MRI", "CT Scan", "Imaging", "DME"]
        }
    },
    {
        "id": "policy_aetna_001",
        "category": "insurance_coverage",
        "insurance_provider": "Aetna",
        "title": "Aetna HMO Referral Policy",
        "content": """
Aetna HMO - Specialist Referral Requirements

STRICT REFERRAL POLICY:
- ALL specialist visits require PCP referral (no exceptions)
- Referral must be obtained BEFORE booking specialist appointment
- Standing referrals available for chronic conditions requiring ongoing specialist care

SPECIALTIES REQUIRING REFERRAL:
- Cardiology, Orthopedic Surgery, Neurology, Endocrinology, Rheumatology
- Gastroenterology, Pulmonology, Nephrology, Urology
- Dermatology, ENT, Ophthalmology (except routine vision)
- All surgical specialties

REFERRAL VALIDITY:
- Single visit referral: Valid for one appointment only
- Standing referral: Valid for 90 days, multiple visits allowed
- Must be for specific diagnosis/condition

EXCEPTIONS (No Referral Required):
- OB/GYN visits (routine and specialty)
- Emergency room visits
- Urgent care visits
- Preventive care screenings

COPAY STRUCTURE:
- Specialist copay: $50 per visit
- PCP copay: $25 per visit

IMPORTANT: Visiting specialist without valid referral will result in claim denial and patient financial responsibility.
        """,
        "metadata": {
            "policy_type": "referral_requirements",
            "plan_type": "HMO",
            "requires_referral": "all_specialists"
        }
    },
    {
        "id": "policy_medicare_001",
        "category": "insurance_coverage",
        "insurance_provider": "Medicare",
        "title": "Medicare Coverage and Referral Policy",
        "content": """
Medicare (Traditional/Original) - Coverage Policy

REFERRAL REQUIREMENTS:
- Original Medicare does NOT require referrals for specialist visits
- Patients can see any Medicare-participating provider
- Medicare Advantage plans may have different referral rules

COVERAGE DETAILS:
- Part B covers outpatient services including specialist visits
- 20% coinsurance applies after annual deductible ($226 in 2024)
- No copays for Medicare-covered services (coinsurance instead)
- Preventive services covered at 100% (no coinsurance)

PRIOR AUTHORIZATION:
- Part B drugs may require authorization
- Durable medical equipment (DME) may require documentation
- Home health services require physician certification

PREVENTIVE SERVICES (No Cost):
- Annual wellness visit
- Cardiovascular screening
- Diabetes screening
- Cancer screenings (mammogram, colonoscopy, etc.)
- Bone density testing
- Vaccinations (flu, pneumonia, COVID-19)

IMPORTANT NOTES:
- Verify provider accepts Medicare assignment
- Non-participating providers may charge more than Medicare-approved amount
- Part B deductible must be met before coinsurance applies
- No out-of-pocket maximum in Original Medicare
        """,
        "metadata": {
            "policy_type": "coverage_rules",
            "plan_type": "Federal Insurance",
            "referral_required": "no"
        }
    },
    {
        "id": "policy_medicaid_001",
        "category": "insurance_coverage",
        "insurance_provider": "Medicaid",
        "title": "Texas Medicaid Referral and Coverage Policy",
        "content": """
Texas Medicaid - Managed Care Referral Requirements

STRICT REFERRAL POLICY:
- ALL specialist visits require PCP referral
- Must select a Primary Care Provider (PCP) within network
- PCP coordinates all specialty care

REFERRAL PROCESS:
1. Contact PCP office to request specialist referral
2. PCP evaluates need and submits referral to managed care organization
3. MCO reviews and approves referral (typically 3-5 business days)
4. Approved referral sent to specialist's office
5. Patient can then schedule appointment

SERVICES REQUIRING REFERRAL:
- All specialty care (cardiology, orthopedics, etc.)
- Advanced imaging (MRI, CT scans)
- Surgical consultations
- Physical therapy (except initial evaluation)
- Mental health specialty services

SERVICES NOT REQUIRING REFERRAL:
- Emergency services
- Family planning services
- Prenatal care
- Well-child checkups

COST SHARING:
- No copays for covered services
- No deductibles
- No coinsurance
- Must verify active Medicaid eligibility before each visit

IMPORTANT: Eligibility must be active on date of service. Re-verify monthly.
        """,
        "metadata": {
            "policy_type": "referral_requirements",
            "plan_type": "State Insurance",
            "state": "Texas"
        }
    },
    {
        "id": "policy_uhc_001",
        "category": "insurance_coverage",
        "insurance_provider": "United Healthcare",
        "title": "United Healthcare PPO Coverage Policy",
        "content": """
United Healthcare PPO - Specialist Access and Coverage

REFERRAL REQUIREMENTS:
- NO REFERRALS REQUIRED for specialist visits
- Patients have freedom to choose any in-network specialist
- Out-of-network benefits available (higher cost-sharing)

PRIOR AUTHORIZATION REQUIREMENTS:
- Elective surgical procedures
- Advanced imaging (MRI, CT, PET scans)
- Specialty medications and biologics
- Inpatient hospital admissions (non-emergency)
- Durable medical equipment over $1,000

COST SHARING:
- Specialist copay: $50 per visit (in-network)
- PCP copay: $25 per visit (in-network)
- Annual deductible: $2,000 individual
- Out-of-pocket maximum: $7,000 individual

PREVENTIVE CARE (100% Covered):
- Annual physical examination
- Age-appropriate cancer screenings
- Immunizations per CDC guidelines
- Cardiovascular disease screening
- Diabetes screening

NETWORK REQUIREMENTS:
- Use in-network providers for maximum coverage
- Out-of-network: Higher deductible and coinsurance apply
- Emergency services covered at in-network level regardless of facility

AUTHORIZATION TIMELINE:
- Submit requests 7-10 days before service
- Urgent requests: 72-hour turnaround
        """,
        "metadata": {
            "policy_type": "coverage_rules",
            "plan_type": "PPO",
            "referral_required": "no"
        }
    },

    # ============================================================================
    # CLINICAL SCHEDULING PROTOCOLS
    # ============================================================================
    {
        "id": "protocol_ortho_001",
        "category": "clinical_protocol",
        "specialty": "Orthopedic Surgery",
        "title": "Post-Operative Joint Replacement Follow-Up Protocol",
        "content": """
BSW Health - Joint Replacement Post-Operative Follow-Up Schedule

KNEE REPLACEMENT FOLLOW-UP:
- 2 weeks post-op: Incision check, suture/staple removal, ROM assessment
- 6 weeks post-op: X-ray, physical therapy progress review, weight-bearing status
- 3 months post-op: X-ray, functional assessment, return to activities clearance
- 1 year post-op: Annual check-up, X-ray, long-term outcome assessment
- Annually thereafter: Routine surveillance

HIP REPLACEMENT FOLLOW-UP:
- 2 weeks post-op: Incision check, hip precautions review, gait assessment
- 6 weeks post-op: X-ray required, PT progress, driving clearance
- 3 months post-op: X-ray, functional assessment, return to work evaluation
- 1 year post-op: Annual surveillance with X-ray
- Annually thereafter: Long-term monitoring

APPOINTMENT BOOKING GUIDELINES:
- Post-op appointments are HIGH PRIORITY - schedule within requested timeframe
- 2-week follow-up should be scheduled before hospital discharge
- Patient should bring physical therapy notes to appointments
- Same surgeon who performed procedure should see patient for follow-ups

RED FLAGS requiring urgent appointment:
- Increasing pain, swelling, or drainage from incision
- Fever > 101 degrees F
- Inability to bear weight
- Signs of DVT (calf pain, swelling)

SCHEDULING NOTES:
- Allow 30-minute appointment slots
- Schedule X-ray 30 minutes before appointment time for 6-week and 3-month visits
        """,
        "metadata": {
            "protocol_type": "post_operative",
            "procedures": ["Knee Replacement", "Hip Replacement"],
            "urgency": "routine"
        }
    },
    {
        "id": "protocol_cardio_001",
        "category": "clinical_protocol",
        "specialty": "Cardiology",
        "title": "Cardiac Chest Pain Evaluation Protocol",
        "content": """
BSW Health - Chest Pain Evaluation and Scheduling Protocol

TRIAGE CRITERIA:

EMERGENT (Direct to ER - DO NOT SCHEDULE):
- Active chest pain at rest
- Chest pain with shortness of breath, diaphoresis, or nausea
- Chest pain lasting > 15 minutes
- New onset chest pain with cardiac risk factors

URGENT (Schedule within 24-48 hours):
- Recent chest pain episode (resolved)
- Abnormal stress test results
- Post-hospital discharge for ACS
- New or worsening exertional chest pain

ROUTINE (Schedule within 1-2 weeks):
- Atypical chest pain
- Follow-up after normal stress test
- Screening for patients with cardiac risk factors

APPOINTMENT REQUIREMENTS:
- New patient cardiology visit: 45-minute slot
- Follow-up visit: 30-minute slot
- Patient should bring list of current medications
- Recent EKG or stress test results if available

PRE-VISIT INSTRUCTIONS:
- Fasting not required for consultation (required for stress test)
- Bring medication list and pharmacy information
- Bring prior cardiology records if seen elsewhere

INSURANCE CONSIDERATIONS:
- Verify referral requirements (BCBS, Aetna, Medicaid require referral)
- Medicare and United Healthcare do not require referral
- Prior authorization may be needed for stress testing

SCHEDULING PRIORITY:
- Post-stress test abnormal: URGENT (within 1 week)
- Chest pain evaluation: URGENT if recent symptoms
- Routine follow-up: Can schedule 2-3 weeks out
        """,
        "metadata": {
            "protocol_type": "evaluation",
            "condition": "Chest Pain",
            "urgency_levels": ["emergent", "urgent", "routine"]
        }
    },
    {
        "id": "protocol_cardio_002",
        "category": "clinical_protocol",
        "specialty": "Cardiology",
        "title": "Atrial Fibrillation Monitoring Protocol",
        "content": """
BSW Health - Atrial Fibrillation Follow-Up Protocol

ROUTINE MONITORING SCHEDULE:
- Newly diagnosed A-fib: Follow-up in 2-4 weeks after medication initiation
- Stable A-fib: Every 3-6 months based on symptom control
- Unstable/symptomatic A-fib: Monthly until stable

VISIT REQUIREMENTS:
- EKG at every visit (schedule 15 minutes before appointment)
- INR check if on warfarin (same day or within 24 hours)
- Medication review at each visit
- Symptom assessment (palpitations, fatigue, dyspnea)

APPOINTMENT DURATION:
- New patient A-fib: 45 minutes
- Follow-up stable: 30 minutes
- Follow-up unstable: 45 minutes

PRE-VISIT PREPARATION:
- Patient should bring medication list
- Bring home blood pressure log if monitoring at home
- Bring list of symptoms/episodes since last visit
- INR results if checked outside BSW system

MEDICATION MANAGEMENT:
- Rate control medications (beta-blockers, calcium channel blockers)
- Anticoagulation (warfarin, DOACs)
- Rhythm control (antiarrhythmics if applicable)

SCHEDULING CONSIDERATIONS:
- Same cardiologist for continuity of care
- Morning appointments preferred for fasting labs if needed
- Allow time for EKG before provider visit

RED FLAGS (needs urgent appointment):
- Rapid heart rate not controlled with medications
- New stroke symptoms
- Bleeding while on anticoagulation
        """,
        "metadata": {
            "protocol_type": "chronic_disease_management",
            "condition": "Atrial Fibrillation",
            "frequency": "3-6 months"
        }
    },
    {
        "id": "protocol_primary_001",
        "category": "clinical_protocol",
        "specialty": "Primary Care",
        "title": "Annual Wellness Visit Protocol",
        "content": """
BSW Health - Annual Wellness Visit and Preventive Care Protocol

ANNUAL WELLNESS EXAM COMPONENTS:
- Comprehensive physical examination
- Vital signs (BP, pulse, height, weight, BMI)
- Age-appropriate cancer screenings
- Cardiovascular risk assessment
- Immunization review and updates
- Depression screening (PHQ-9)
- Cognitive assessment (age 65+)
- Review of medications and allergies

RECOMMENDED FASTING LABS:
- Lipid panel (fasting 9-12 hours)
- Comprehensive metabolic panel
- Hemoglobin A1C (if diabetic or pre-diabetic)
- TSH (if indicated)

APPOINTMENT SCHEDULING:
- Duration: 40 minutes for comprehensive exam
- Schedule fasting labs same day BEFORE appointment (8-10 AM preferred)
- Allow time for immunizations during visit

INSURANCE COVERAGE:
- Most insurances cover 100% as preventive care
- Must be coded as wellness visit (not sick visit)
- Additional problems discussed may incur separate charge

AGE-SPECIFIC SCREENINGS:
- Age 40-49: Annual BP check, cholesterol every 5 years
- Age 50-75: Colonoscopy every 10 years OR Cologuard every 3 years
- Women 40+: Annual mammogram
- Women 21-65: Pap smear every 3 years (or co-testing every 5 years)
- Age 65+: Bone density scan (women)

SCHEDULING FREQUENCY:
- Annual wellness visit: Once per year
- Medicare Annual Wellness Visit: Covered annually after initial Welcome to Medicare visit

PATIENT INSTRUCTIONS:
- Fasting 9-12 hours before lab draw
- Bring current medication bottles or list
- Bring prior medical records if new patient
- Complete health questionnaire before visit
        """,
        "metadata": {
            "protocol_type": "preventive_care",
            "visit_type": "Annual Wellness",
            "frequency": "annually"
        }
    },
    {
        "id": "protocol_primary_002",
        "category": "clinical_protocol",
        "specialty": "Primary Care",
        "title": "Chronic Disease Management Protocol",
        "content": """
BSW Health - Primary Care Chronic Disease Follow-Up Protocol

DIABETES MANAGEMENT:
- Type 2 Diabetes: Follow-up every 3 months
- Required labs: Hemoglobin A1C every 3 months, lipid panel annually
- Annual foot exam, annual eye exam referral
- Appointment duration: 30 minutes
- Morning appointments preferred for fasting labs

HYPERTENSION MANAGEMENT:
- Uncontrolled HTN: Follow-up every 1-2 months until controlled
- Controlled HTN: Follow-up every 3-6 months
- Patient should bring home BP log
- Medication adjustment as needed
- Appointment duration: 20 minutes

HYPERLIPIDEMIA:
- Follow-up every 3-6 months if on statin therapy
- Lipid panel annually or after medication change
- Fasting labs required
- Appointment duration: 20 minutes

SCHEDULING GUIDELINES:
- Same PCP for continuity of care when possible
- Morning slots for patients requiring fasting labs
- Back-to-back scheduling not recommended for complex patients
- Allow buffer time for patients with multiple chronic conditions

PATIENT PREPARATION:
- Bring medication list or bottles
- Bring home monitoring logs (blood pressure, blood glucose)
- List questions/concerns before visit
- Complete lab work 3-5 days before appointment if ordered

COORDINATION OF CARE:
- Review specialist notes from recent visits
- Ensure patient has referrals for required specialty care
- Medication reconciliation at each visit
- Update problem list and care plan
        """,
        "metadata": {
            "protocol_type": "chronic_disease_management",
            "conditions": ["Diabetes", "Hypertension", "Hyperlipidemia"],
            "frequency": "varies"
        }
    },

    # ============================================================================
    # APPOINTMENT SCHEDULING POLICIES
    # ============================================================================
    {
        "id": "scheduling_001",
        "category": "scheduling_policy",
        "title": "Appointment Cancellation and No-Show Policy",
        "content": """
BSW Health - Appointment Cancellation and No-Show Policy

CANCELLATION REQUIREMENTS:
- Patients must cancel at least 24 hours before scheduled appointment
- Cancellations accepted by phone, patient portal, or BSW mobile app
- Same-day cancellations may be subject to no-show fee

NO-SHOW POLICY:
- No-show defined as: Failure to attend appointment without 24-hour notice
- First no-show: Warning letter sent to patient
- Second no-show: $50 fee may be charged
- Third no-show: Patient may be discharged from practice

NO-SHOW FEE EXCEPTIONS:
- Medical emergencies
- Hospital admissions
- Weather-related road closures
- Provider-initiated cancellations

RESCHEDULING:
- Patients who cancel with proper notice can reschedule immediately
- No-show patients may be required to pay fee before rescheduling
- High-demand appointments (new patient, procedures) given priority for reliable patients

LATE ARRIVAL POLICY:
- Patients arriving >15 minutes late may need to reschedule
- Appointment may be shortened if other patients scheduled
- Chronic late arrivals will be counseled and may be subject to discharge

IMPACT ON PRACTICE:
- No-shows prevent other patients from accessing care
- Average daily no-show rate impacts provider capacity planning
- Repeated no-shows may result in dismissal from practice

PATIENT RESPONSIBILITIES:
- Keep track of scheduled appointments
- Set reminders on phone/calendar
- Update contact information for appointment reminders
- Call immediately if unable to attend

AUTOMATED REMINDERS:
- Phone call reminder: 2 days before appointment
- Text message reminder: 1 day before appointment
- Email reminder: 2 days before appointment
        """,
        "metadata": {
            "policy_type": "scheduling_rules",
            "applies_to": "all_appointments"
        }
    },
    {
        "id": "scheduling_002",
        "category": "scheduling_policy",
        "title": "Appointment Booking and Waitlist Management",
        "content": """
BSW Health - Appointment Booking and Waitlist Policy

APPOINTMENT TYPES:
- New patient appointments: Longer duration, may have limited availability
- Established patient follow-up: Standard duration
- Urgent care visits: Same-day or next-day slots reserved
- Preventive care/wellness: Can schedule several weeks in advance

NEW PATIENT BOOKING:
- New patient slots limited per day (typically 2-4 slots)
- Require demographic information and insurance verification before booking
- May require referral verification before confirming appointment
- Typical lead time: 1-3 weeks depending on specialty

ESTABLISHED PATIENT BOOKING:
- Can book future appointments at checkout after current visit
- Online scheduling available through patient portal
- Same-day acute visits available based on capacity

URGENT APPOINTMENT SLOTS:
- Reserved slots each day for urgent/acute needs
- Released day-of if not needed for established patients
- Triage by nurse determines urgency level
- True emergencies directed to ER

WAITLIST MANAGEMENT:
- Patients can be added to cancellation waitlist
- Automatic notification when earlier slot becomes available
- 2-hour window to confirm or lose slot
- Priority given to patients with urgent medical needs

PROVIDER PREFERENCE REQUESTS:
- Patients can request specific provider
- May result in longer wait times
- Alternative: See first available in practice
- Continuity of care prioritized for chronic disease management

SCHEDULING WINDOWS:
- Primary care: Open 3 months in advance
- Specialists: Open 2-3 months in advance
- Post-operative follow-ups: Scheduled before discharge, can override limits

ONLINE SCHEDULING LIMITATIONS:
- New patient appointments may not be available online
- Urgent visits should call for triage
- Complex appointments require phone scheduling
        """,
        "metadata": {
            "policy_type": "scheduling_rules",
            "booking_types": ["new_patient", "follow_up", "urgent"]
        }
    },
    {
        "id": "scheduling_003",
        "category": "scheduling_policy",
        "title": "Insurance Verification and Pre-Visit Requirements",
        "content": """
BSW Health - Insurance Verification and Pre-Visit Requirements

INSURANCE VERIFICATION (Required before all appointments):
1. Verify active coverage on date of service
2. Confirm patient name matches insurance card
3. Check if provider is in-network
4. Verify copay amounts
5. Check if referral required
6. Verify prior authorization if needed

WHEN TO VERIFY:
- At time of booking for new patients
- 3 days before appointment for established patients
- Day of service for walk-in/urgent visits

REFERRAL VERIFICATION:
- Required for: BCBS (select specialists), Aetna HMO (all specialists), Medicaid (all specialists)
- Not required for: Medicare, United Healthcare PPO
- Confirm referral is on file 48 hours before appointment
- If no referral: Contact patient to obtain before appointment

PRIOR AUTHORIZATION CHECK:
- Verify if appointment type requires authorization
- Common triggers: New patient specialist visits, procedures, imaging
- Confirm authorization number is on file
- No authorization = possible claim denial

PATIENT REGISTRATION:
- New patients arrive 15 minutes early for paperwork
- Bring photo ID and current insurance card
- Complete forms online through patient portal when possible
- Update demographic information annually

COPAY COLLECTION:
- Copays collected at check-in before service
- Patients without copay may need to pay estimated charges
- Payment plans available for large balances

MISSING INFORMATION:
- Missing insurance: Patient may need to self-pay or reschedule
- Expired insurance: Contact patient to update
- Missing referral: Give patient 24 hours to obtain or reschedule

FINANCIAL COUNSELING:
- High deductible patients should be informed of costs
- Payment plans available for procedures
- Financial assistance programs for qualifying patients
        """,
        "metadata": {
            "policy_type": "scheduling_rules",
            "verification_required": ["insurance", "referral", "prior_auth"]
        }
    },
    {
        "id": "scheduling_004",
        "category": "scheduling_policy",
        "title": "Special Populations Scheduling Guidelines",
        "content": """
BSW Health - Special Populations Scheduling Considerations

GERIATRIC PATIENTS (Age 65+):
- Longer appointment times may be needed (add 10 minutes)
- Morning appointments preferred (better cognition/energy)
- Transportation considerations (avoid rush hour)
- May need assistance with patient portal/online scheduling
- Medication reconciliation critical at each visit
- Consider scheduling all appointments same day if possible

PEDIATRIC PATIENTS:
- Schedule during school hours when possible for school-age children
- Well-child visits: Book series of appointments in advance
- Sick visits: Same-day slots available
- Parent/guardian must be present
- Immunization visits may take longer

PATIENTS WITH DISABILITIES:
- Ensure accessible appointment times and locations
- Allow extra time for mobility challenges
- Sign language interpreter available with advance notice (48 hours)
- Transportation assistance available through some insurance plans
- Ground floor or elevator access locations preferred

NON-ENGLISH SPEAKING PATIENTS:
- Language line available for 200+ languages
- Bilingual providers noted in scheduling system
- In-person medical interpreters for complex visits (schedule in advance)
- Translated materials available in Spanish, Vietnamese, Chinese
- Family members should not interpret for medical visits

PATIENTS WITH COMPLEX MEDICAL NEEDS:
- Multiple chronic conditions: Longer appointment slots
- Care coordination between multiple specialists
- Consider scheduling multiple appointments same day/location
- Social work referral if needed for care coordination
- Case management for high-risk patients

BEHAVIORAL HEALTH CONSIDERATIONS:
- Patients with anxiety: First appointment of day may reduce wait stress
- Patients with dementia: Routine/consistency important
- Patients with substance use disorder: Non-judgmental scheduling approach

TRANSPORTATION BARRIERS:
- Public transportation: Consider bus routes and schedules
- Medicaid transportation benefits (arrange 3-5 days in advance)
- Volunteer driver programs for eligible patients
- Telehealth options when appropriate
        """,
        "metadata": {
            "policy_type": "scheduling_rules",
            "populations": ["geriatric", "pediatric", "disabilities", "language_barriers"]
        }
    }
]


class HealthcarePolicyRAG:
    """
    Healthcare Policy Retrieval System using ChromaDB.

    Provides semantic search over healthcare policies, insurance coverage rules,
    clinical protocols, and scheduling guidelines.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG system.

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.collection_name = "healthcare_policies"
        self.client = None
        self.collection = None

    def initialize(self) -> None:
        """
        Initialize ChromaDB client and collection.
        Idempotent - safe to call multiple times.
        """
        try:
            # Initialize persistent ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Use default embedding function (all-MiniLM-L6-v2)
            embedding_function = embedding_functions.DefaultEmbeddingFunction()

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Healthcare policies, insurance rules, and clinical protocols"}
            )

            # Check if collection is empty and populate if needed
            if self.collection.count() == 0:
                logger.info("Collection empty - populating with healthcare policies...")
                self._populate_policies()
            else:
                logger.info(f"Collection already populated with {self.collection.count()} documents")

        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise

    def _populate_policies(self) -> None:
        """Populate the vector database with healthcare policy documents."""
        try:
            documents = []
            metadatas = []
            ids = []

            for policy in HEALTHCARE_POLICIES:
                # Extract content and metadata
                documents.append(policy["content"])

                # Build metadata dictionary
                metadata = {
                    "category": policy["category"],
                    "title": policy["title"]
                }

                # Add optional fields
                if "insurance_provider" in policy:
                    metadata["insurance_provider"] = policy["insurance_provider"]
                if "specialty" in policy:
                    metadata["specialty"] = policy["specialty"]
                if "metadata" in policy:
                    # Add nested metadata fields
                    for key, value in policy["metadata"].items():
                        if isinstance(value, (str, int, float, bool)):
                            metadata[key] = str(value)
                        elif isinstance(value, list):
                            metadata[key] = ", ".join(str(v) for v in value)

                metadatas.append(metadata)
                ids.append(policy["id"])

            # Add documents to collection in batch
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Successfully populated {len(documents)} policy documents")

        except Exception as e:
            logger.error(f"Error populating policies: {e}")
            raise

    def retrieve_policies(
        self,
        query: str,
        n_results: int = 3,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant policy documents based on semantic search.

        Args:
            query: Search query (natural language)
            n_results: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"category": "insurance_coverage"})

        Returns:
            List of dictionaries containing:
                - content: Policy document text
                - metadata: Policy metadata
                - distance: Relevance score (lower = more relevant)
                - id: Document ID
        """
        try:
            if self.collection is None:
                raise RuntimeError("RAG system not initialized. Call initialize() first.")

            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_dict  # Optional metadata filtering
            )

            # Format results
            formatted_results = []
            if results and results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None,
                        "id": results['ids'][0][i] if results['ids'] else None
                    })

            logger.info(f"Retrieved {len(formatted_results)} relevant policies for query: '{query[:50]}...'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving policies: {e}")
            return []

    def reset(self) -> None:
        """Reset the collection (for testing purposes)."""
        try:
            if self.client:
                self.client.delete_collection(name=self.collection_name)
                logger.info("Collection reset successfully")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            if self.collection is None:
                return {"error": "Collection not initialized"}

            count = self.collection.count()

            # Get all metadata to analyze
            all_docs = self.collection.get()

            categories = {}
            for metadata in all_docs['metadatas']:
                category = metadata.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1

            return {
                "total_documents": count,
                "categories": categories,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}


# Global RAG instance
_rag_instance = None

def get_rag_instance() -> HealthcarePolicyRAG:
    """
    Get or create the global RAG instance (singleton pattern).

    Returns:
        Initialized HealthcarePolicyRAG instance
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = HealthcarePolicyRAG()
        _rag_instance.initialize()
    return _rag_instance


def retrieve_policies(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to retrieve policies using the global RAG instance.

    Args:
        query: Search query
        n_results: Number of results to return

    Returns:
        List of relevant policy documents with metadata
    """
    rag = get_rag_instance()
    return rag.retrieve_policies(query, n_results)


def initialize_rag() -> HealthcarePolicyRAG:
    """
    Initialize the RAG system and return the instance.
    Idempotent - safe to call multiple times.

    Returns:
        Initialized HealthcarePolicyRAG instance
    """
    return get_rag_instance()


if __name__ == "__main__":
    """
    Command-line interface for initializing and testing the RAG system.
    Usage: python rag.py
    """
    print("=" * 80)
    print("BSW Health - Healthcare Policy RAG System")
    print("=" * 80)
    print()

    # Initialize RAG system
    print("Initializing RAG system...")
    rag = initialize_rag()
    print(" RAG system initialized successfully")
    print()

    # Display collection statistics
    stats = rag.get_collection_stats()
    print("Collection Statistics:")
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Collection Name: {stats['collection_name']}")
    print(f"  Persist Directory: {stats['persist_directory']}")
    print()
    print("Documents by Category:")
    for category, count in stats['categories'].items():
        print(f"  - {category}: {count}")
    print()

    # Test queries
    print("=" * 80)
    print("Testing Retrieval Queries")
    print("=" * 80)
    print()

    test_queries = [
        "Does Blue Cross Blue Shield require referrals for cardiology?",
        "What is the follow-up schedule after knee replacement surgery?",
        "Does Medicare require prior authorization?",
        "What is the no-show policy for appointments?",
        "How often should diabetic patients follow up?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        results = rag.retrieve_policies(query, n_results=2)

        for j, result in enumerate(results, 1):
            print(f"\n  Result {j} (Relevance Score: {result['distance']:.4f}):")
            print(f"  Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  Category: {result['metadata'].get('category', 'N/A')}")
            print(f"  Content Preview: {result['content'][:200].strip()}...")

        print("\n" + "-" * 80 + "\n")

    print("=" * 80)
    print("RAG System Ready for Use!")
    print("=" * 80)
    print()
    print("Usage in your application:")
    print("  from rag import retrieve_policies")
    print("  results = retrieve_policies('your query here', n_results=3)")
