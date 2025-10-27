"""
Script to update agent prompts with nearest provider logic
"""

with open('prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add find_nearest_providers to the tools list for each agent
old_tools_section = """You have access to these functions - use them systematically:

**check_provider(specialty, sub_specialty, location, insurance)**
- Use this to find orthopedic surgeons matching patient criteria
- Parameters: specialty="Orthopedic Surgery", sub_specialty (e.g., "Joint Replacement", "Sports Medicine"), location (city), insurance provider
- Returns: List of providers with details

**search_slots(provider_id, date_range, appointment_type, time_preference)**"""

new_tools_section = """You have access to these functions - use them systematically:

**find_nearest_providers(patient_city, specialty)** - START WITH THIS
- Find providers nearest to patient's location
- Parameters: patient_city (from patient demographics), specialty (optional)
- Returns: Providers in patient's city, or list of available cities if none found
- **USE THIS FIRST** to suggest convenient locations to the patient

**check_provider(specialty, sub_specialty, location, insurance)**
- Use this to find orthopedic surgeons matching patient criteria
- Parameters: specialty="Orthopedic Surgery", sub_specialty (e.g., "Joint Replacement", "Sports Medicine"), location (city), insurance provider
- Returns: List of providers with details

**search_slots(provider_id, date_range, appointment_type, time_preference)**"""

content = content.replace(old_tools_section, new_tools_section)

# Update the workflow to include nearest provider check
old_workflow_step1 = """**Step 1: Gather Information**
- Patient name/ID
- Type of orthopedic care needed
- New patient or follow-up?
- Location preference
- Insurance information
- Date/time preferences

**Step 2: Check Insurance & Referrals** (if applicable)"""

new_workflow_step1 = """**Step 1: Check Patient Demographics & Suggest Nearest Location**
- Use get_patient_info() to retrieve patient demographics including their city
- Use find_nearest_providers() with the patient's city to find convenient locations
- Proactively suggest providers in their city: "I see you're in [City]. We have [X] providers there..."
- If no providers in their city, offer the nearest available cities
- Confirm their location preference before proceeding

**Step 2: Gather Appointment Details**
- Type of orthopedic care needed
- New patient or follow-up?
- Insurance information
- Date/time preferences

**Step 3: Check Insurance & Referrals** (if applicable)"""

content = content.replace(old_workflow_step1, new_workflow_step1)

# Update Step 3 reference to Step 4
content = content.replace("**Step 3: Find Appropriate Provider**", "**Step 4: Find Appropriate Provider**")
content = content.replace("**Step 4: Search Available Appointments**", "**Step 5: Search Available Appointments**")
content = content.replace("**Step 5: Book Appointment**", "**Step 6: Book Appointment**")

with open('prompts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated prompts.py with nearest provider logic!")
print("- Added find_nearest_providers() tool")
print("- Updated workflow to suggest nearest location first")
