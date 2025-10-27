# Remaining Improvements for BSW Scheduling Agent

## Completed (6 of 12) ✅

1. ✅ Enhanced patient status logic (new to system vs new to provider)
2. ✅ Display patient addresses in chat sidebar
3. ✅ Created specialty-specific appointment types
4. ✅ Removed all emojis from UI
5. ✅ Fixed use_column_width deprecation warning
6. ✅ Fixed white text in feedback response boxes

---

## Remaining Tasks (6 of 12)

### 3. Filter Appointment Search to Requested Type Only

**Issue**: When patient asks for a specific appointment type (e.g., "annual wellness visit"), the agent shows all appointment types.

**Fix Location**: `prompts.py` - Update agent prompts to emphasize filtering

**Solution**:
```python
# In ORTHOPEDIC_AGENT_PROMPT, CARDIOLOGY_AGENT_PROMPT, PRIMARY_CARE_AGENT_PROMPT
# Add to the search_appointment_slots guidance:

When searching for appointments:
- If patient specifies an appointment type, ONLY search for that exact type
- Use the appointment_type parameter to filter results
- Example: Patient says "annual wellness visit" → search with appointment_type="Annual Wellness Visit"
- DO NOT show other appointment types unless no slots found for requested type
```

### 4. Add Provider Specialty Explanation When Suggesting Alternatives

**Issue**: When suggesting a different doctor, agent doesn't explain what type of doctor they are.

**Fix Location**: `prompts.py` - Update all specialty agent prompts

**Solution**:
```python
# Add to each agent prompt:

When suggesting an alternative provider:
- Always include their specialty and sub-specialty
- Explain why they're a good match
- Example: "Dr. Sarah Williams is a foot and ankle orthopedic surgeon who specializes in sports injuries"
- Include location information
```

### 6. Fix Agent Hallucination of Doctor Names and Slots

**Issue**: Agents are inventing doctor names and appointment slots that don't exist in mock_data.py

**Root Cause**: Agents not using tools reliably, generating responses without function calls

**Fix Locations**:
1. `prompts.py` - Strengthen tool usage requirements
2. `tools.py` - Ensure tools return clear "not found" messages

**Solution for prompts.py**:
```python
# Add to each specialty agent prompt:

CRITICAL RULES FOR TOOL USAGE:
1. ALWAYS use check_provider() before mentioning any doctor's name
2. ALWAYS use search_appointment_slots() before mentioning available times
3. NEVER invent or guess provider names - only use names returned by tools
4. NEVER invent or guess appointment times - only use times returned by tools
5. If no results from tools, say "I don't see any available slots" - do NOT make up times
```

**Solution for tools.py**:
```python
# In search_appointment_slots, add clearer messaging:
if not matching_slots:
    return {
        "success": True,
        "data": [],
        "message": "No appointment slots found matching your criteria. This data is coming directly from our scheduling system - these are the only slots available."
    }
```

### 9. Show Routing Spinner Only When Actually Routing

**Issue**: Loading circle appears even when staying with same agent

**Fix Location**: `pages/chat.py` - Conditional spinner logic

**Solution**:
```python
# In chat.py, around line 350-370:
# Change from:
with st.spinner("Processing..."):
    routing_result = route_patient(user_message)

# To:
# Only show routing spinner if we haven't routed yet OR agent explicitly requests routing
if st.session_state.current_agent == 'router':
    with st.spinner("Routing to specialist..."):
        routing_result = route_patient(user_message)
else:
    # Already with a specialist, no routing spinner
    routing_result = None
```

### 10. Fix Next Available Appointment Response Logic

**Issue**: Agent says "no availability for 2 weeks" before checking beyond 2 weeks

**Fix Locations**:
1. `mock_data.py` - Generate slots beyond 14 days
2. `prompts.py` - Update search logic guidance
3. `tools.py` - Update search_appointment_slots to search further if needed

**Solution for mock_data.py**:
```python
# Change generate_appointment_slots default:
def generate_appointment_slots(provider: Provider, days_ahead: int = 30):  # Was 14
```

**Solution for prompts.py**:
```python
# Add to appointment search guidance:

When searching for appointments:
1. Start with next 2 weeks (default)
2. If no slots found, automatically extend search to 4 weeks
3. If still nothing, tell patient the ACTUAL next available date (don't say "no availability")
4. Present the soonest available appointment, even if weeks away
```

**Solution for tools.py**:
```python
# In search_appointment_slots function:
# Add logic to find next available even if beyond initial date_range
# Return actual next available date instead of just "none found"
```

### 12. Make Metrics Dashboard Use Real Data OR Clearly Show It's Example Data

**Issue**: Metrics dashboard shows mock data but isn't clear it's not real

**Fix Location**: `pages/metrics_dashboard.py`

**Option A - Use Real Data**:
```python
# Create a metrics tracking system in session_state
# Store actual conversation metrics from chat.py
# Display real metrics in dashboard
```

**Option B - Clearly Label as Example**:
```python
# At top of metrics_dashboard.py:
st.warning("""
    **Example Data Displayed**

    The metrics shown below are example data for demonstration purposes.
    Real metrics will be collected from actual chat sessions once the system is in production.
""")
```

---

## Implementation Priority

**High Priority** (Affects core functionality):
1. Fix agent hallucination (#6)
2. Fix next available appointment logic (#10)
3. Filter appointment search (#3)

**Medium Priority** (UX improvements):
4. Add provider specialty explanations (#4)
5. Show routing spinner conditionally (#9)

**Low Priority** (Nice to have):
6. Metrics dashboard data source (#12)

---

## Quick Fixes You Can Apply Now

### For #6 (Hallucination):
Edit `prompts.py` lines ~220, ~470, ~700 to add this after existing tool descriptions:

```
**IMPORTANT**:
- Only mention doctor names that come from check_provider() tool results
- Only mention appointment times that come from search_appointment_slots() tool results
- If tools return no results, tell the patient truthfully - do not invent information
```

### For #10 (Next Available):
Edit `mock_data.py` line 698:
```python
def generate_appointment_slots(provider: Provider, days_ahead: int = 30):  # Changed from 14
```

Then regenerate slots by running:
```bash
python3 -c "from mock_data import *"
```

---

**Note**: The Streamlit app needs to be restarted for changes to take effect:
```bash
# Kill the current process
# Then restart:
streamlit run app.py
```
