"""
Function calling tools for BSW scheduling agent.
Implements OpenAI-compatible function definitions and handlers for healthcare appointment scheduling.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
from mock_data import (
    PROVIDERS, PATIENTS, ALL_APPOINTMENT_SLOTS, INSURANCE_POLICIES, CLINICAL_PROTOCOLS,
    get_provider_by_id, get_patient_by_id, get_providers_by_specialty,
    get_insurance_policy, get_clinical_protocol as get_clinical_protocol_data,
    get_metro_area, get_metro_cities,
    Provider, Patient, AppointmentSlot
)


def check_provider_availability(provider_id: str) -> Dict[str, Any]:
    """
    Look up provider by ID and return detailed availability information.

    Args:
        provider_id: The unique identifier for the healthcare provider (e.g., 'DR001')

    Returns:
        Dictionary containing provider details and availability status, or error message
    """
    try:
        provider = get_provider_by_id(provider_id)

        if not provider:
            return {
                "success": False,
                "error": f"Provider with ID '{provider_id}' not found",
                "provider_id": provider_id
            }

        # Get available slots for this provider
        available_slots = [
            slot for slot in ALL_APPOINTMENT_SLOTS
            if slot.provider_id == provider_id and slot.is_available
        ]

        # Group slots by date
        slots_by_date = {}
        for slot in available_slots[:50]:  # Limit to next 50 available slots
            date = slot.date
            if date not in slots_by_date:
                slots_by_date[date] = []
            slots_by_date[date].append({
                "time": slot.time,
                "duration": slot.duration,
                "type": slot.appointment_type,
                "slot_id": slot.slot_id
            })

        return {
            "success": True,
            "provider_id": provider_id,
            "provider_name": f"Dr. {provider.first_name} {provider.last_name}",
            "specialty": provider.specialty,
            "sub_specialty": provider.sub_specialty,
            "credentials": provider.credentials,
            "location": provider.location,
            "city": provider.city,
            "phone": provider.phone,
            "accepting_new_patients": provider.accepting_new_patients,
            "languages": provider.languages,
            "insurance_accepted": provider.insurance_accepted,
            "availability_days": provider.availability_days,
            "typical_slot_duration": provider.typical_slot_duration,
            "available_slots_count": len(available_slots),
            "next_available_slots": slots_by_date
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking provider availability: {str(e)}",
            "provider_id": provider_id
        }


def search_appointment_slots(
    provider_id: Optional[str] = None,
    specialty: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    appointment_type: Optional[str] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """
    Search for available appointment slots with multiple filter options.

    Args:
        provider_id: Filter by specific provider ID (e.g., 'DR001')
        specialty: Filter by medical specialty (e.g., 'Cardiology', 'Orthopedic Surgery', 'Primary Care')
        start_date: Start date for search range (YYYY-MM-DD format)
        end_date: End date for search range (YYYY-MM-DD format)
        location: Filter by clinic location city (e.g., 'Dallas', 'Plano')
        appointment_type: Filter by appointment type (e.g., 'New Patient Consultation', 'Post-Operative Follow-up', 'Heart Failure Follow-up'). Supports exact and partial matching.
        max_results: Maximum number of results to return (default 20)

    Returns:
        Dictionary containing matching available slots and search metadata
    """
    try:
        # Start with all available slots
        available_slots = [slot for slot in ALL_APPOINTMENT_SLOTS if slot.is_available]

        # Apply filters
        if provider_id:
            available_slots = [s for s in available_slots if s.provider_id == provider_id]

        if specialty:
            # Get providers matching specialty
            specialty_providers = get_providers_by_specialty(specialty)
            provider_ids = [p.provider_id for p in specialty_providers]
            available_slots = [s for s in available_slots if s.provider_id in provider_ids]

        if start_date:
            available_slots = [s for s in available_slots if s.date >= start_date]

        if end_date:
            available_slots = [s for s in available_slots if s.date <= end_date]

        if location:
            # Use metropolitan area matching for more flexible location filtering
            # First try exact city match, then try metro area match
            metro_cities = get_metro_cities(location)

            # Get providers in the location's metro area
            location_provider_ids = []
            for provider in PROVIDERS:
                # Check if provider's city matches any city in the metro area
                if any(city.lower() == provider.city.lower() for city in metro_cities):
                    location_provider_ids.append(provider.provider_id)

            # Also support substring matching on location name (e.g., "Dallas" matches "BSW Medical Center - Dallas")
            available_slots = [
                s for s in available_slots
                if (s.provider_id in location_provider_ids or location.lower() in s.location.lower())
            ]

        if appointment_type:
            # Support both exact matching and partial matching
            # First try exact match, then fall back to partial match
            appointment_type_lower = appointment_type.lower()
            exact_match_slots = [
                s for s in available_slots
                if s.appointment_type.lower() == appointment_type_lower
            ]

            if exact_match_slots:
                available_slots = exact_match_slots
            else:
                # Try partial match (e.g., "follow-up" matches "Post-Operative Follow-up")
                available_slots = [
                    s for s in available_slots
                    if appointment_type_lower in s.appointment_type.lower()
                ]

        # Sort by date and time
        available_slots.sort(key=lambda s: (s.date, s.time))

        # Limit results
        available_slots = available_slots[:max_results]

        # Format results with provider details
        results = []
        for slot in available_slots:
            provider = get_provider_by_id(slot.provider_id)
            if provider:
                results.append({
                    "slot_id": slot.slot_id,
                    "provider_id": slot.provider_id,
                    "provider_name": f"Dr. {provider.first_name} {provider.last_name}",
                    "specialty": provider.specialty,
                    "sub_specialty": provider.sub_specialty,
                    "date": slot.date,
                    "time": slot.time,
                    "duration": slot.duration,
                    "appointment_type": slot.appointment_type,
                    "location": slot.location,
                    "city": provider.city,
                    "phone": provider.phone
                })

        return {
            "success": True,
            "total_results": len(results),
            "filters_applied": {
                "provider_id": provider_id,
                "specialty": specialty,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "appointment_type": appointment_type
            },
            "slots": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching appointment slots: {str(e)}",
            "total_results": 0,
            "slots": []
        }


def book_appointment(
    slot_id: str,
    patient_id: str,
    reason_for_visit: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Book an appointment slot for a patient.
    Validates slot availability and checks for scheduling conflicts.

    Args:
        slot_id: The unique identifier for the appointment slot
        patient_id: The patient's unique identifier
        reason_for_visit: Brief description of the appointment purpose
        notes: Optional additional notes or special requests

    Returns:
        Dictionary containing booking confirmation or error details
    """
    try:
        # Find the slot
        slot = None
        for s in ALL_APPOINTMENT_SLOTS:
            if s.slot_id == slot_id:
                slot = s
                break

        if not slot:
            return {
                "success": False,
                "error": f"Appointment slot '{slot_id}' not found",
                "slot_id": slot_id
            }

        if not slot.is_available:
            return {
                "success": False,
                "error": "This appointment slot is no longer available",
                "slot_id": slot_id,
                "slot_date": slot.date,
                "slot_time": slot.time
            }

        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            return {
                "success": False,
                "error": f"Patient with ID '{patient_id}' not found",
                "patient_id": patient_id
            }

        # Get provider details
        provider = get_provider_by_id(slot.provider_id)
        if not provider:
            return {
                "success": False,
                "error": f"Provider for this slot not found",
                "provider_id": slot.provider_id
            }

        # Check if patient's insurance is accepted by provider
        if patient.insurance_provider not in provider.insurance_accepted:
            return {
                "success": False,
                "error": f"Provider does not accept patient's insurance: {patient.insurance_provider}",
                "provider_insurance_accepted": provider.insurance_accepted,
                "patient_insurance": patient.insurance_provider,
                "recommendation": "Patient may need to pay out-of-pocket or find an in-network provider"
            }

        # Check if provider is accepting new patients (for new patient appointments)
        if slot.appointment_type == "New Patient" and not provider.accepting_new_patients:
            return {
                "success": False,
                "error": f"Dr. {provider.last_name} is not currently accepting new patients",
                "provider_id": provider.provider_id,
                "recommendation": "Search for another provider in the same specialty"
            }

        # Mark slot as unavailable (book it)
        slot.is_available = False

        # Generate confirmation details
        confirmation_number = f"CONF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            "success": True,
            "confirmation_number": confirmation_number,
            "message": "Appointment successfully booked",
            "appointment_details": {
                "slot_id": slot_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient_id,
                "provider_name": f"Dr. {provider.first_name} {provider.last_name}",
                "provider_id": provider.provider_id,
                "specialty": provider.specialty,
                "date": slot.date,
                "time": slot.time,
                "duration": slot.duration,
                "appointment_type": slot.appointment_type,
                "location": slot.location,
                "address": provider.address,
                "city": provider.city,
                "phone": provider.phone,
                "reason_for_visit": reason_for_visit,
                "notes": notes or "None",
                "insurance": patient.insurance_provider
            },
            "next_steps": [
                "You will receive a confirmation email shortly",
                f"Arrive 15 minutes early to complete paperwork",
                "Bring your insurance card and photo ID",
                "Bring a list of current medications"
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error booking appointment: {str(e)}",
            "slot_id": slot_id,
            "patient_id": patient_id
        }


def verify_insurance(
    patient_id: str,
    service_type: str,
    specialty: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify insurance coverage and check for special requirements.

    Args:
        patient_id: The patient's unique identifier
        service_type: Type of service (e.g., 'Specialist Visit', 'Primary Care', 'Surgery', 'Imaging')
        specialty: Medical specialty if applicable (e.g., 'Cardiology', 'Orthopedic Surgery')

    Returns:
        Dictionary containing coverage details, copay, and authorization requirements
    """
    try:
        # Get patient
        patient = get_patient_by_id(patient_id)
        if not patient:
            return {
                "success": False,
                "error": f"Patient with ID '{patient_id}' not found",
                "patient_id": patient_id
            }

        # Get insurance policy
        insurance_policy = get_insurance_policy(patient.insurance_provider)
        if not insurance_policy:
            return {
                "success": False,
                "error": f"Insurance policy for '{patient.insurance_provider}' not found",
                "insurance_provider": patient.insurance_provider,
                "recommendation": "Please contact insurance provider directly for coverage verification"
            }

        # Determine if service is covered
        service_covered = False
        for covered_service in insurance_policy.covered_services:
            if service_type.lower() in covered_service.lower():
                service_covered = True
                break

        # Check referral requirements
        referral_required = False
        if specialty:
            for required_specialty in insurance_policy.requires_referral:
                if required_specialty.lower() in specialty.lower() or specialty.lower() in required_specialty.lower():
                    referral_required = True
                    break

        # Check prior authorization requirements
        prior_auth_required = False
        for auth_service in insurance_policy.requires_prior_auth:
            if service_type.lower() in auth_service.lower():
                prior_auth_required = True
                break

        # Determine copay
        copay = insurance_policy.copay_primary
        if specialty and specialty != "Primary Care":
            copay = insurance_policy.copay_specialist

        # Generate next steps
        next_steps = []
        if referral_required:
            next_steps.append("Obtain a referral from your primary care physician before scheduling")
        if prior_auth_required:
            next_steps.append("Prior authorization required - contact insurance before procedure")
        if not referral_required and not prior_auth_required:
            next_steps.append("No special authorization required - you may proceed with scheduling")
        next_steps.append("Bring your insurance card to your appointment")

        return {
            "success": True,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "patient_id": patient_id,
            "insurance_provider": patient.insurance_provider,
            "insurance_id": patient.insurance_id,
            "policy_type": insurance_policy.policy_type,
            "service_type": service_type,
            "specialty": specialty,
            "coverage": {
                "is_covered": service_covered,
                "copay": copay,
                "deductible": insurance_policy.deductible,
                "out_of_pocket_max": insurance_policy.out_of_pocket_max
            },
            "requirements": {
                "referral_required": referral_required,
                "prior_authorization_required": prior_auth_required
            },
            "notes": insurance_policy.notes,
            "next_steps": next_steps
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error verifying insurance: {str(e)}",
            "patient_id": patient_id
        }


def check_referral_status(
    patient_id: str,
    specialty: str,
    referring_provider_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if a valid referral exists for a patient to see a specialist.

    Args:
        patient_id: The patient's unique identifier
        specialty: The specialty being referred to (e.g., 'Cardiology', 'Orthopedic Surgery')
        referring_provider_id: Optional ID of the referring provider

    Returns:
        Dictionary containing referral status and validity information
    """
    try:
        # Get patient
        patient = get_patient_by_id(patient_id)
        if not patient:
            return {
                "success": False,
                "error": f"Patient with ID '{patient_id}' not found",
                "patient_id": patient_id
            }

        # Check if patient has a PCP
        if not patient.primary_care_provider:
            return {
                "success": True,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient_id,
                "has_referral": False,
                "specialty": specialty,
                "message": "Patient does not have a designated primary care provider",
                "recommendation": "Patient should establish care with a PCP first or check if insurance requires referral"
            }

        # Get PCP details
        pcp = get_provider_by_id(patient.primary_care_provider)

        # Check recent visits for referrals
        has_recent_referral = False
        referral_date = None
        referral_notes = None

        for visit in patient.recent_visits:
            # Check if visit notes mention the specialty
            if specialty.lower() in visit.get("notes", "").lower():
                visit_date = datetime.strptime(visit["date"], "%Y-%m-%d")
                days_ago = (datetime.now() - visit_date).days

                # Referrals typically valid for 90 days
                if days_ago <= 90:
                    has_recent_referral = True
                    referral_date = visit["date"]
                    referral_notes = visit["notes"]
                    break

        if has_recent_referral:
            days_remaining = 90 - (datetime.now() - datetime.strptime(referral_date, "%Y-%m-%d")).days

            return {
                "success": True,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient_id,
                "has_referral": True,
                "specialty": specialty,
                "referral_date": referral_date,
                "referring_provider": f"Dr. {pcp.first_name} {pcp.last_name}" if pcp else "Unknown",
                "referring_provider_id": patient.primary_care_provider,
                "days_remaining_valid": days_remaining,
                "referral_notes": referral_notes,
                "status": "Valid" if days_remaining > 0 else "Expired",
                "message": f"Valid referral found, expires in {days_remaining} days"
            }
        else:
            return {
                "success": True,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient_id,
                "has_referral": False,
                "specialty": specialty,
                "primary_care_provider": f"Dr. {pcp.first_name} {pcp.last_name}" if pcp else None,
                "primary_care_provider_id": patient.primary_care_provider,
                "message": "No active referral found for this specialty",
                "recommendation": f"Patient should contact their PCP (Dr. {pcp.last_name if pcp else 'their primary care provider'}) to obtain a referral"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking referral status: {str(e)}",
            "patient_id": patient_id
        }


def get_patient_info(patient_id: str) -> Dict[str, Any]:
    """
    Retrieve patient demographics and medical history.

    Args:
        patient_id: The patient's unique identifier

    Returns:
        Dictionary containing patient information, medical history, and recent visits
    """
    try:
        patient = get_patient_by_id(patient_id)

        if not patient:
            return {
                "success": False,
                "error": f"Patient with ID '{patient_id}' not found",
                "patient_id": patient_id
            }

        # Get PCP details
        pcp = None
        if patient.primary_care_provider:
            pcp = get_provider_by_id(patient.primary_care_provider)

        return {
            "success": True,
            "patient_id": patient_id,
            "demographics": {
                "name": f"{patient.first_name} {patient.last_name}",
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth,
                "age": patient.age,
                "gender": patient.gender,
                "phone": patient.phone,
                "email": patient.email,
                "address": f"{patient.address}, {patient.city}, {patient.state} {patient.zip_code}",
                "city": patient.city,
                "state": patient.state,
                "zip_code": patient.zip_code
            },
            "insurance": {
                "provider": patient.insurance_provider,
                "insurance_id": patient.insurance_id
            },
            "primary_care_provider": {
                "provider_id": patient.primary_care_provider,
                "name": f"Dr. {pcp.first_name} {pcp.last_name}" if pcp else None,
                "specialty": pcp.specialty if pcp else None,
                "location": pcp.location if pcp else None,
                "phone": pcp.phone if pcp else None
            } if pcp else None,
            "medical_history": {
                "conditions": patient.medical_conditions,
                "allergies": patient.allergies,
                "medications": patient.medications
            },
            "recent_visits": patient.recent_visits,
            "visit_count": len(patient.recent_visits)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving patient information: {str(e)}",
            "patient_id": patient_id
        }


def get_clinical_protocol(condition: str, specialty: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve clinical scheduling guidelines and protocols for a specific condition.

    Args:
        condition: Medical condition or procedure (e.g., 'Knee Replacement', 'Diabetes', 'Chest Pain')
        specialty: Optional medical specialty to narrow search

    Returns:
        Dictionary containing clinical protocol details and scheduling recommendations
    """
    try:
        # Search for matching protocol
        protocol = None

        # First try exact match
        for p in CLINICAL_PROTOCOLS:
            if condition.lower() in p.condition.lower() or condition.lower() in p.name.lower():
                if specialty:
                    if specialty.lower() in p.specialty.lower():
                        protocol = p
                        break
                else:
                    protocol = p
                    break

        if not protocol:
            # Try broader search
            condition_keywords = condition.lower().split()
            for p in CLINICAL_PROTOCOLS:
                protocol_text = f"{p.name} {p.condition}".lower()
                if any(keyword in protocol_text for keyword in condition_keywords):
                    if specialty:
                        if specialty.lower() in p.specialty.lower():
                            protocol = p
                            break
                    else:
                        protocol = p
                        break

        if not protocol:
            return {
                "success": False,
                "error": f"No clinical protocol found for condition: {condition}",
                "condition": condition,
                "specialty": specialty,
                "recommendation": "Please consult with a healthcare provider for specific scheduling guidance"
            }

        # Parse follow-up timing
        follow_up_guidance = _parse_follow_up_timing(protocol.recommended_follow_up, protocol.urgency_level)

        return {
            "success": True,
            "protocol_id": protocol.protocol_id,
            "protocol_name": protocol.name,
            "specialty": protocol.specialty,
            "condition": protocol.condition,
            "urgency_level": protocol.urgency_level,
            "recommended_follow_up": protocol.recommended_follow_up,
            "follow_up_guidance": follow_up_guidance,
            "special_instructions": protocol.special_instructions,
            "scheduling_priority": _get_scheduling_priority(protocol.urgency_level)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving clinical protocol: {str(e)}",
            "condition": condition
        }


def _parse_follow_up_timing(recommended_follow_up: str, urgency_level: str) -> Dict[str, Any]:
    """Helper function to parse follow-up timing into actionable guidance."""
    timing_lower = recommended_follow_up.lower()

    guidance = {
        "raw_recommendation": recommended_follow_up,
        "urgency": urgency_level
    }

    if "week" in timing_lower:
        if "1 week" in timing_lower or "within 1 week" in timing_lower:
            guidance["suggested_date_range"] = "Within 7 days"
            guidance["days_from_now"] = 7
        elif "2 week" in timing_lower:
            guidance["suggested_date_range"] = "Within 14 days"
            guidance["days_from_now"] = 14
        elif "3 week" in timing_lower:
            guidance["suggested_date_range"] = "Within 21 days"
            guidance["days_from_now"] = 21
        elif "4 week" in timing_lower:
            guidance["suggested_date_range"] = "Within 28 days"
            guidance["days_from_now"] = 28

    if "month" in timing_lower:
        if "1 month" in timing_lower or "1-3 month" in timing_lower:
            guidance["suggested_date_range"] = "Within 1-3 months"
            guidance["days_from_now"] = 60
        elif "3 month" in timing_lower or "3-6 month" in timing_lower:
            guidance["suggested_date_range"] = "Within 3-6 months"
            guidance["days_from_now"] = 120
        elif "6 month" in timing_lower:
            guidance["suggested_date_range"] = "Within 6 months"
            guidance["days_from_now"] = 180

    if "annual" in timing_lower or "1 year" in timing_lower:
        guidance["suggested_date_range"] = "Within 1 year"
        guidance["days_from_now"] = 365

    if "same day" in timing_lower or "urgent" in urgency_level.lower():
        guidance["suggested_date_range"] = "Same day or within 24 hours"
        guidance["days_from_now"] = 1

    return guidance


def _get_scheduling_priority(urgency_level: str) -> str:
    """Helper function to determine scheduling priority."""
    urgency_map = {
        "emergent": "IMMEDIATE - Schedule within 24 hours or direct to ER",
        "urgent": "HIGH - Schedule within 1 week",
        "routine": "NORMAL - Schedule within recommended timeframe"
    }
    return urgency_map.get(urgency_level.lower(), "NORMAL")


def get_provider_team(physician_id: str) -> Dict[str, Any]:
    """
    Get all PAs/NPs who work under a specific physician's supervision.
    Useful for finding post-operative follow-up providers when surgeon unavailable.

    Args:
        physician_id: The physician's provider ID (e.g., 'DR003')

    Returns:
        Dictionary containing team member details
    """
    try:
        # Verify physician exists
        physician = get_provider_by_id(physician_id)
        if not physician:
            return {
                "success": False,
                "error": f"Physician with ID '{physician_id}' not found",
                "physician_id": physician_id
            }

        # Find all PAs/NPs supervised by this physician
        team_members = [
            p for p in PROVIDERS
            if p.supervising_physician == physician_id
        ]

        # Format team member details
        team_list = []
        for member in team_members:
            team_list.append({
                "provider_id": member.provider_id,
                "name": f"{member.first_name} {member.last_name}",
                "credentials": member.credentials,
                "provider_type": member.provider_type,
                "specialty": member.specialty,
                "sub_specialty": member.sub_specialty,
                "location": member.location,
                "city": member.city,
                "phone": member.phone,
                "availability_days": member.availability_days,
                "typical_slot_duration": member.typical_slot_duration
            })

        return {
            "success": True,
            "physician_id": physician_id,
            "physician_name": f"Dr. {physician.first_name} {physician.last_name}",
            "physician_specialty": physician.specialty,
            "team_size": len(team_members),
            "team_members": team_list,
            "message": f"Dr. {physician.last_name} has {len(team_members)} team member(s)" if team_members else f"Dr. {physician.last_name} has no PA/NP team members on file"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting provider team: {str(e)}",
            "physician_id": physician_id
        }


def find_nearest_providers(
    patient_city: str,
    specialty: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find providers nearest to the patient's location.
    Uses metropolitan area grouping - finds providers in patient's city AND nearby metro cities.
    For example, a patient in Dallas will see providers in Dallas, Plano, Arlington, Frisco, etc.

    Args:
        patient_city: The city where the patient lives
        specialty: Optional specialty filter

    Returns:
        Dictionary containing nearest providers and available locations
    """
    try:
        # Get all providers (optionally filtered by specialty)
        if specialty:
            providers = get_providers_by_specialty(specialty)
        else:
            providers = PROVIDERS

        # Find providers in the same city as patient
        same_city_providers = [p for p in providers if p.city.lower() == patient_city.lower()]

        # Get metropolitan area cities (includes patient's city + nearby cities)
        metro_cities = get_metro_cities(patient_city)
        metro_area_name = get_metro_area(patient_city)

        # Find providers in the same metropolitan area
        metro_providers = [
            p for p in providers
            if any(city.lower() == p.city.lower() for city in metro_cities)
        ]

        # Get all unique cities where providers are located
        all_cities = sorted(list(set(p.city for p in providers)))

        # Format results - prioritize same city, then metro area
        nearest_providers = []

        # Add same-city providers first
        for provider in same_city_providers[:3]:  # Up to 3 same-city providers
            nearest_providers.append({
                "provider_id": provider.provider_id,
                "name": f"Dr. {provider.first_name} {provider.last_name}",
                "specialty": provider.specialty,
                "sub_specialty": provider.sub_specialty,
                "location": provider.location,
                "city": provider.city,
                "phone": provider.phone,
                "accepting_new_patients": provider.accepting_new_patients,
                "distance_category": "same_city"
            })

        # Add metro area providers (different city, but nearby)
        for provider in metro_providers:
            if provider.city.lower() != patient_city.lower() and len(nearest_providers) < 5:
                nearest_providers.append({
                    "provider_id": provider.provider_id,
                    "name": f"Dr. {provider.first_name} {provider.last_name}",
                    "specialty": provider.specialty,
                    "sub_specialty": provider.sub_specialty,
                    "location": provider.location,
                    "city": provider.city,
                    "phone": provider.phone,
                    "accepting_new_patients": provider.accepting_new_patients,
                    "distance_category": "metro_area"
                })

        # Build message
        if same_city_providers:
            message = f"Found {len(same_city_providers)} providers in {patient_city}"
            if metro_area_name and len(metro_providers) > len(same_city_providers):
                other_metro_providers = len(metro_providers) - len(same_city_providers)
                message += f", plus {other_metro_providers} more in the {metro_area_name} area"
        elif metro_providers:
            message = f"No providers in {patient_city}, but found {len(metro_providers)} in the {metro_area_name} area"
        else:
            message = f"No providers found in {patient_city}. Available in: {', '.join(all_cities)}"

        return {
            "success": True,
            "patient_city": patient_city,
            "metro_area": metro_area_name,
            "metro_cities": metro_cities if metro_area_name else [patient_city],
            "providers_in_patient_city": len(same_city_providers),
            "providers_in_metro_area": len(metro_providers),
            "nearest_providers": nearest_providers,
            "all_available_cities": all_cities,
            "message": message
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error finding nearest providers: {str(e)}",
            "patient_city": patient_city
        }


# ============================================================================
# OPENAI FUNCTION CALLING DEFINITIONS
# ============================================================================

TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_provider_availability",
            "description": "Look up a healthcare provider by their ID and retrieve detailed availability information including their schedule, accepted insurance, languages spoken, and upcoming appointment slots. Use this when a patient asks about a specific doctor's availability or wants to know more about a provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "string",
                        "description": "The unique identifier for the healthcare provider (e.g., 'DR001', 'DR011'). Provider IDs typically start with 'DR' followed by numbers."
                    }
                },
                "required": ["provider_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_appointment_slots",
            "description": "Search for available appointment slots across providers with flexible filtering options. Can search by specific provider, medical specialty, date range, location, or appointment type. Returns detailed information about available time slots including provider details and location. Use this when a patient needs to find appointment availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "string",
                        "description": "Optional: Filter by specific provider ID (e.g., 'DR001')"
                    },
                    "specialty": {
                        "type": "string",
                        "description": "Optional: Filter by medical specialty. Valid specialties include: 'Orthopedic Surgery', 'Cardiology', 'Primary Care'",
                        "enum": ["Orthopedic Surgery", "Cardiology", "Primary Care"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional: Start date for search range in YYYY-MM-DD format (e.g., '2024-10-25')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional: End date for search range in YYYY-MM-DD format (e.g., '2024-11-15')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional: Filter by clinic location city (e.g., 'Dallas', 'Plano', 'Arlington', 'Temple', 'Round Rock')"
                    },
                    "appointment_type": {
                        "type": "string",
                        "description": "Optional: Filter by specific appointment type. Types are specialty-specific. Examples: 'New Patient Consultation', 'Post-Operative Follow-up', 'Fracture Follow-up', 'Joint Injection', 'Heart Failure Follow-up', 'A-fib Management', 'Annual Wellness Visit', 'Chronic Disease Management'. Use the exact appointment type name the patient requests."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Optional: Maximum number of results to return (default 20)",
                        "default": 20
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment slot for a patient. Validates slot availability, checks for conflicts, verifies insurance acceptance, and confirms the provider is accepting new patients if applicable. Returns a confirmation number and appointment details upon successful booking. Use this only after confirming the patient wants to book a specific slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slot_id": {
                        "type": "string",
                        "description": "The unique identifier for the appointment slot (e.g., 'SLOT-DR001-0015'). This is obtained from search_appointment_slots results."
                    },
                    "patient_id": {
                        "type": "string",
                        "description": "The patient's unique identifier (e.g., 'PT001', 'PT002')"
                    },
                    "reason_for_visit": {
                        "type": "string",
                        "description": "Brief description of the appointment purpose (e.g., 'Post-op follow-up for knee replacement', 'Annual physical', 'Chest pain evaluation')"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional: Additional notes or special requests for the appointment"
                    }
                },
                "required": ["slot_id", "patient_id", "reason_for_visit"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_insurance",
            "description": "Verify a patient's insurance coverage for a specific service or specialty. Checks coverage status, calculates copay amounts, and identifies any special requirements like referrals or prior authorization. Use this before booking appointments to ensure the patient understands their coverage and requirements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient's unique identifier (e.g., 'PT001', 'PT002')"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of service to verify coverage for (e.g., 'Specialist Visit', 'Primary Care', 'Surgery', 'Imaging', 'Lab work')"
                    },
                    "specialty": {
                        "type": "string",
                        "description": "Optional: Medical specialty if verifying specialist coverage (e.g., 'Cardiology', 'Orthopedic Surgery')"
                    }
                },
                "required": ["patient_id", "service_type"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_referral_status",
            "description": "Check if a valid referral exists for a patient to see a specialist. Verifies referral existence, validity period (typically 90 days), and provides referring provider information. Use this when a patient needs to see a specialist and their insurance requires referrals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient's unique identifier (e.g., 'PT001', 'PT002')"
                    },
                    "specialty": {
                        "type": "string",
                        "description": "The specialty being referred to (e.g., 'Cardiology', 'Orthopedic Surgery', 'Neurology')"
                    },
                    "referring_provider_id": {
                        "type": "string",
                        "description": "Optional: ID of the referring provider if known"
                    }
                },
                "required": ["patient_id", "specialty"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_info",
            "description": "Retrieve comprehensive patient information including demographics, insurance details, primary care provider, medical history (conditions, allergies, medications), and recent visits. Use this to understand a patient's background before scheduling or to answer questions about their medical history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient's unique identifier (e.g., 'PT001', 'PT002')"
                    }
                },
                "required": ["patient_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clinical_protocol",
            "description": "Retrieve clinical scheduling guidelines and protocols for a specific medical condition or procedure. Provides recommended follow-up timing, urgency level, special instructions, and scheduling priorities based on clinical best practices. Use this to understand how soon a patient should be seen for their specific condition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "Medical condition or procedure to look up (e.g., 'Knee Replacement', 'Diabetes', 'Chest Pain', 'Atrial Fibrillation', 'Hip Replacement')"
                    },
                    "specialty": {
                        "type": "string",
                        "description": "Optional: Medical specialty to narrow the search (e.g., 'Orthopedic Surgery', 'Cardiology', 'Primary Care')"
                    }
                },
                "required": ["condition"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_nearest_providers",
            "description": "Find healthcare providers nearest to the patient's location. Use this at the start of scheduling conversations to suggest the most convenient location for the patient. Returns providers in the patient's city first, then lists all available cities if none found locally.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_city": {
                        "type": "string",
                        "description": "The city where the patient lives (e.g., 'Dallas', 'Plano', 'Austin')"
                    },
                    "specialty": {
                        "type": "string",
                        "description": "Optional: Filter by medical specialty (e.g., 'Orthopedic Surgery', 'Cardiology', 'Primary Care')",
                        "enum": ["Orthopedic Surgery", "Cardiology", "Primary Care"]
                    }
                },
                "required": ["patient_city"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_provider_team",
            "description": "Get all Physician Assistants (PAs) and Nurse Practitioners (NPs) who work under a specific physician's supervision. Essential for post-operative follow-up scheduling when the operating surgeon is unavailable. Team members can handle routine follow-ups (wound checks, suture removal, post-op assessments) under physician supervision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "physician_id": {
                        "type": "string",
                        "description": "The physician's provider ID (e.g., 'DR003', 'DR001'). This is the supervising physician whose team you want to find."
                    }
                },
                "required": ["physician_id"],
                "additionalProperties": False
            }
        }
    }
]


# ============================================================================
# TOOL DISPATCHER
# ============================================================================

def execute_tool(tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function by name with provided arguments.

    Args:
        tool_name: Name of the tool function to execute
        tool_arguments: Dictionary of arguments to pass to the function

    Returns:
        Result dictionary from the tool function
    """
    tool_map = {
        "check_provider_availability": check_provider_availability,
        "search_appointment_slots": search_appointment_slots,
        "book_appointment": book_appointment,
        "verify_insurance": verify_insurance,
        "check_referral_status": check_referral_status,
        "get_patient_info": get_patient_info,
        "get_clinical_protocol": get_clinical_protocol,
        "find_nearest_providers": find_nearest_providers,
        "get_provider_team": get_provider_team,
    }

    if tool_name not in tool_map:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "available_tools": list(tool_map.keys())
        }

    try:
        return tool_map[tool_name](**tool_arguments)
    except TypeError as e:
        return {
            "success": False,
            "error": f"Invalid arguments for {tool_name}: {str(e)}",
            "tool_name": tool_name,
            "provided_arguments": tool_arguments
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing {tool_name}: {str(e)}",
            "tool_name": tool_name
        }


if __name__ == "__main__":
    """Test the tools with sample calls."""
    print("BSW Scheduling Agent - Tools Test\n")
    print("=" * 60)

    # Test 1: Check provider availability
    print("\n1. Testing check_provider_availability...")
    result = check_provider_availability("DR001")
    print(f"Provider: {result.get('provider_name')}")
    print(f"Specialty: {result.get('specialty')}")
    print(f"Available slots: {result.get('available_slots_count')}")

    # Test 2: Search appointment slots
    print("\n2. Testing search_appointment_slots...")
    result = search_appointment_slots(specialty="Cardiology", location="Dallas", max_results=5)
    print(f"Found {result.get('total_results')} slots")
    if result['slots']:
        print(f"First slot: {result['slots'][0]['date']} at {result['slots'][0]['time']}")

    # Test 3: Get patient info
    print("\n3. Testing get_patient_info...")
    result = get_patient_info("PT001")
    print(f"Patient: {result.get('demographics', {}).get('name')}")
    print(f"Insurance: {result.get('insurance', {}).get('provider')}")
    print(f"Conditions: {result.get('medical_history', {}).get('conditions')}")

    # Test 4: Verify insurance
    print("\n4. Testing verify_insurance...")
    result = verify_insurance("PT001", "Specialist Visit", "Orthopedic Surgery")
    print(f"Coverage: {result.get('coverage', {})}")
    print(f"Referral required: {result.get('requirements', {}).get('referral_required')}")

    # Test 5: Check referral status
    print("\n5. Testing check_referral_status...")
    result = check_referral_status("PT001", "Orthopedic Surgery")
    print(f"Has referral: {result.get('has_referral')}")
    print(f"Message: {result.get('message')}")

    # Test 6: Get clinical protocol
    print("\n6. Testing get_clinical_protocol...")
    result = get_clinical_protocol("Knee Replacement", "Orthopedic Surgery")
    print(f"Protocol: {result.get('protocol_name')}")
    print(f"Recommended follow-up: {result.get('recommended_follow_up')}")
    print(f"Priority: {result.get('scheduling_priority')}")

    # Test 7: Book appointment
    print("\n7. Testing book_appointment...")
    # First find an available slot
    slots_result = search_appointment_slots(provider_id="DR001", max_results=1)
    if slots_result['slots']:
        slot_id = slots_result['slots'][0]['slot_id']
        result = book_appointment(slot_id, "PT001", "Post-op knee replacement follow-up")
        print(f"Booking success: {result.get('success')}")
        if result.get('success'):
            print(f"Confirmation: {result.get('confirmation_number')}")
            print(f"Date: {result['appointment_details']['date']} at {result['appointment_details']['time']}")

    print("\n" + "=" * 60)
    print("\nAll tools tested successfully!")
    print(f"\nTotal tools available: {len(TOOLS_DEFINITIONS)}")
    for tool_def in TOOLS_DEFINITIONS:
        print(f"  - {tool_def['function']['name']}")
