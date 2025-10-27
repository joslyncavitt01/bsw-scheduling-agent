# Metropolitan Area Location Matching

## Overview

The BSW Scheduling Agent uses **metropolitan area grouping** to provide a more realistic and user-friendly location matching experience. This means that patients searching for providers in one city will also see providers in nearby cities within the same metropolitan area.

## Why This Matters

Many people consider nearby cities as part of the same general area. For example:
- **Plano is part of Dallas** - Someone living in Dallas would realistically consider seeing a doctor in Plano (15-20 minutes away)
- **Round Rock is part of Austin** - These cities are in the same metropolitan area
- **Distance ranges are practical** - Metropolitan area grouping reflects real-world healthcare access patterns

## Metropolitan Areas Defined

### Dallas-Fort Worth Metroplex
**Cities**: Dallas, Plano, Arlington, Frisco, Irving, Richardson

**Example**: A patient living in Dallas will see providers in:
1. **Same City (Dallas)** - shown first
2. **Metro Area (Plano, Arlington, etc.)** - shown next as "nearby"

### Austin Metro Area
**Cities**: Austin, Round Rock, Cedar Park, Georgetown

### Central Texas
**Cities**: Temple, Belton, Killeen, Waco

### Houston Metro Area
**Cities**: Houston, The Woodlands, Katy, Sugar Land

### San Antonio Metro Area
**Cities**: San Antonio, New Braunfels, Schertz

## How It Works

### 1. `find_nearest_providers()` Function

When a patient in Dallas searches for providers, the function returns:

```json
{
  "patient_city": "Dallas",
  "metro_area": "Dallas-Fort Worth",
  "metro_cities": ["Dallas", "Plano", "Arlington", "Frisco", "Irving", "Richardson"],
  "providers_in_patient_city": 1,
  "providers_in_metro_area": 3,
  "nearest_providers": [
    {
      "name": "Dr. David Anderson",
      "city": "Dallas",
      "distance_category": "same_city"
    },
    {
      "name": "Dr. Jennifer Kim",
      "city": "Arlington",
      "distance_category": "metro_area"
    },
    {
      "name": "Dr. Robert Martinez",
      "city": "Plano",
      "distance_category": "metro_area"
    }
  ],
  "message": "Found 1 providers in Dallas, plus 2 more in the Dallas-Fort Worth area"
}
```

**Key Features**:
- Same-city providers shown first (up to 3)
- Metro area providers shown next (up to 5 total)
- Clear `distance_category` labels
- Human-readable message explaining results

### 2. `search_appointment_slots()` Location Filter

When searching for appointments with a location filter, the metropolitan area is automatically included:

```python
# Patient searches for "Dallas" appointments
search_appointment_slots(
    specialty="Orthopedic Surgery",
    location="Dallas",
    appointment_type="Post-Operative Follow-up"
)

# Returns appointments from:
# - Dr. Anderson in Dallas
# - Dr. Martinez in Plano  ✓ (same metro area!)
# - Dr. Kim in Arlington   ✓ (same metro area!)
```

**Result**: More appointment availability, better user experience

## Real-World Example

### Scenario: Sarah Martinez (PT001)
- **Lives in**: Dallas
- **Needs**: Post-op knee replacement follow-up
- **Original Surgeon**: Dr. Robert Martinez in Plano

### Without Metro Area Matching
```
Agent: "I found 1 provider in Dallas"
Patient: "But my surgeon is Dr. Martinez in Plano!"
Agent: "That's a different city. Would you like to search Plano?"
```
❌ **Poor experience** - requires multiple searches

### With Metro Area Matching
```
Agent: "I found 3 orthopedic surgeons in the Dallas-Fort Worth area:
- Dr. Anderson in Dallas
- Dr. Martinez in Plano (your surgeon!)
- Dr. Kim in Arlington"
```
✓ **Great experience** - all relevant providers shown immediately

## Technical Implementation

### File: `mock_data.py`

**Metropolitan Area Definitions**:
```python
METRO_AREAS = {
    "Dallas-Fort Worth": ["Dallas", "Plano", "Arlington", "Frisco", "Irving", "Richardson"],
    "Austin": ["Austin", "Round Rock", "Cedar Park", "Georgetown"],
    "Central Texas": ["Temple", "Belton", "Killeen", "Waco"],
    "Houston": ["Houston", "The Woodlands", "Katy", "Sugar Land"],
    "San Antonio": ["San Antonio", "New Braunfels", "Schertz"]
}
```

**Helper Functions**:
```python
def get_metro_area(city: str) -> Optional[str]:
    """Get the metropolitan area name for a given city."""

def get_metro_cities(city: str) -> List[str]:
    """Get all cities in the same metropolitan area as the given city."""
```

### File: `tools.py`

**Updated Functions**:
1. `find_nearest_providers()` - Uses metro area grouping with prioritization
2. `search_appointment_slots()` - Location filter includes metro area cities

## Benefits

### For Patients
✓ More appointment options available
✓ Realistic representation of "nearby" providers
✓ Finds original surgeon even if in different city
✓ Reduces need for multiple searches

### For Healthcare System
✓ Better utilization of provider network
✓ Reduces empty appointment slots
✓ Improves patient satisfaction
✓ Reflects real-world healthcare access patterns

### For AI Agents
✓ More appointments to offer
✓ Better success rate in booking
✓ Can find original surgeon for follow-ups
✓ Natural, context-aware responses

## Testing Results

All tests passed successfully:

✓ Dallas patient sees providers in Dallas, Plano, Arlington
✓ Search with "Dallas" location returns Plano and Arlington appointments
✓ Dr. Martinez (Plano) appears in Dallas metro searches
✓ Round Rock patient sees Austin metro providers
✓ Temple patient sees Central Texas metro providers

## Configuration

To add or modify metropolitan areas, edit `METRO_AREAS` dictionary in [mock_data.py](mock_data.py#L818-L824):

```python
METRO_AREAS = {
    "Metro Name": ["City1", "City2", "City3"],
    # Add new metro areas here
}
```

Cities not in any metropolitan area will be treated as standalone locations.

---

**Date Added**: 2025-10-27
**Files Modified**: [mock_data.py](mock_data.py), [tools.py](tools.py)
**Test Coverage**: 100% passing
