#!/usr/bin/env python3
"""
Apply remaining prompt fixes for appointment search and provider explanations.
"""

import re

# Fix 1: Update cardiology search_slots description
def fix_cardiology_search(content):
    old = '''**search_slots(provider_id, date_range, appointment_type, time_preference)**
- Search for available appointment slots
- Parameters: provider_id, date_range, appointment_type ("New Patient" or "Follow-up"), time_preference
- Returns: Available appointments
- Note: Cardiology slots are typically 45 minutes'''

    new = '''**search_slots(provider_id, date_range, appointment_type, time_preference)**
- Search for available appointment slots
- Parameters: provider_id, date_range, appointment_type (MUST match specific type: "Heart Failure Follow-up", "A-fib Management", "New Patient Consultation", etc.), time_preference
- Returns: Available appointments
- **CRITICAL**: If patient specifies appointment type, ONLY return that exact type
- **CRITICAL**: If no slots in 2 weeks, search 4 weeks and present ACTUAL next available
- Note: Cardiology slots are typically 45 minutes'''

    return content.replace(old, new)

# Fix 2: Update primary care search_slots description
def fix_primary_search(content):
    old = '''**search_slots(provider_id, date_range, appointment_type, time_preference)**
- Search for available appointment slots
- Parameters: provider_id, date_range, appointment_type ("New Patient" or "Follow-up"), time_preference
- Returns: Available appointments
- Note: Primary care slots are typically 20-30 minutes'''

    new = '''**search_slots(provider_id, date_range, appointment_type, time_preference)**
- Search for available appointment slots
- Parameters: provider_id, date_range, appointment_type (MUST match specific type: "Annual Wellness Visit", "Sick Visit", "Chronic Disease Management", etc.), time_preference
- Returns: Available appointments
- **CRITICAL**: If patient specifies appointment type, ONLY return that exact type
- **CRITICAL**: If no slots in 2 weeks, search 4 weeks and present ACTUAL next available
- Note: Primary care slots are typically 20-30 minutes'''

    return content.replace(old, new)

# Fix 3: Add provider specialty explanation rule (for all three agents)
def add_provider_explanation_rule(content):
    # Add after "CRITICAL RULES - PREVENT HALLUCINATION" section in each agent
    rule_to_add = '''7. When suggesting an alternative provider, ALWAYS explain their specialty and sub-specialty
   Example: "Dr. Sarah Williams is a foot and ankle orthopedic surgeon" or "Dr. Michael Patel is an interventional cardiologist"
'''

    # Find all instances of the hallucination rules and add this as rule #7
    pattern = r'(6\. Only present appointment information that comes directly from tool responses)'
    replacement = r'\1\n' + rule_to_add

    return re.sub(pattern, replacement, content)

def main():
    print("Applying remaining prompt fixes...")
    print("=" * 60)

    filepath = 'prompts.py'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print("1. Fixing cardiology search_slots description...")
    content = fix_cardiology_search(content)

    print("2. Fixing primary care search_slots description...")
    content = fix_primary_search(content)

    print("3. Adding provider specialty explanation rule...")
    content = add_provider_explanation_rule(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("=" * 60)
    print("All prompt fixes applied successfully!")
    print("\nChanges made:")
    print("- Updated search_slots to enforce appointment type filtering")
    print("- Added logic for searching further when no slots found")
    print("- Added rule to explain provider specialty when suggesting alternatives")

if __name__ == "__main__":
    main()
