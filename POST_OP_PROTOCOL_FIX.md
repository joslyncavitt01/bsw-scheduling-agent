# Post-Operative Follow-Up Protocol Fix

## Problem Statement

The agent was saying:
> "Since you're in Dallas, let me check for orthopedic surgeons available for your follow-up appointment in your area."

**This is medically inaccurate.** For post-operative follow-ups, the agent should IMMEDIATELY check the **original operating surgeon's** availability, not search broadly for "surgeons in the area."

## Medical Protocol (Correct Behavior)

### Post-Operative Follow-Up Provider Hierarchy:
1. **PREFERRED**: Original operating surgeon (continuity of care)
2. **IF SURGEON UNAVAILABLE**: Surgeon's PA/NP team (same practice)
3. **IF TEAM UNAVAILABLE**: Same-practice partner surgeon
4. **NEVER**: Random surgeon from different practice

### Rationale:
- Operating surgeon has intimate knowledge of the procedure performed
- PA/NP team members work directly with surgeon and have access to surgical notes
- Continuity of care improves outcomes
- Team-based care is standard in modern surgical practices

## Changes Implemented

### 1. Provider Data Model ([mock_data.py](mock_data.py))

**Added fields to Provider dataclass:**
```python
provider_type: str = "Physician"  # "Physician", "PA", "NP"
supervising_physician: Optional[str] = None  # For PAs/NPs
```

**Added 7 PA/NP providers:**

**Orthopedic Surgery Teams:**
- Emily Carter, PA-C (PA003) → Dr. Martinez (DR003)
- Michael Chen, PA-C (PA001) → Dr. Anderson (DR001)
- Jessica Rodriguez, NP-C (NP002) → Dr. Kim (DR002)
- Thomas Green, PA-C (PA004) → Dr. Williams (DR004)

**Cardiology Teams:**
- Lisa Wang, NP-C (NP011) → Dr. Patel (DR011)
- David Brown, PA-C (PA012) → Dr. Thompson (DR012)
- Maria Santos, NP-C (NP014) → Dr. Garcia (DR014)

**Characteristics:**
- Same location as supervising physician
- Credentials: PA-C or NP-C
- 20-minute typical slot duration (vs 30-45 for physicians)
- All accepting new patients for follow-ups
- Available 5 days/week

**Result**: Total providers increased from 13 to 20

### 2. RAG Healthcare Policy ([rag.py](rag.py:317-336))

**Enhanced post-operative protocol with team-based care guidance:**

```
POST-OPERATIVE FOLLOW-UP PROVIDER HIERARCHY:
1. PREFERRED: Original operating surgeon
2. IF SURGEON UNAVAILABLE: Surgeon's PA/NP from same team
3. IF TEAM UNAVAILABLE: Same-practice partner surgeon
4. NEVER: Random surgeon from different practice

RATIONALE FOR TEAM-BASED POST-OP CARE:
- Operating surgeon has most detailed knowledge
- PA/NP team members provide continuity when surgeon unavailable
- 2-week wound checks often handled by PAs/NPs
- Team-based care is standard practice

TYPICAL POST-OP VISIT PROVIDERS BY TIMEPOINT:
- 2-week follow-up: Surgeon's PA/NP common
- 6-week follow-up: Surgeon or PA/NP
- 3-month follow-up: Surgeon preferred
- Annual follow-up: Surgeon or PA/NP
```

### 3. Agent Prompts ([prompts.py](prompts.py))

**Updated all 3 specialty agents with new Step 4 logic:**

#### Orthopedic Agent (lines 260-284):
```
**Step 4: Find Appropriate Provider**
- **FOR POST-OPERATIVE FOLLOW-UPS:**
  - Extract patient's recent visits from get_patient_info()
  - **IMMEDIATELY say**: "I see Dr. [Surgeon] performed your [procedure].
    Let me check their availability for your follow-up."
  - **Search in this order (DO NOT SKIP)**:
    1. FIRST: Check operating surgeon's availability
    2. IF surgeon unavailable: Check their PA/NP team
       Say: "Dr. [Surgeon] doesn't have availability, but I can schedule you
       with [PA/NP Name], who works directly on Dr. [Surgeon]'s team."
    3. IF team unavailable: Check same-practice partners
    4. NEVER: Search broadly for "surgeons in the area"
```

#### Cardiology Agent (lines 554-578):
- Same logic adapted for post-procedure follow-ups
- Covers pacemaker, cardiac procedures, A-fib management

#### Primary Care Agent (lines 825-847):
- Same continuity-of-care logic
- Notes that PCPs typically don't have PA/NP teams like surgery

### 4. New Tool Function ([tools.py](tools.py:738-797))

**Added `get_provider_team()` function:**

```python
def get_provider_team(physician_id: str) -> Dict[str, Any]:
    """
    Get all PAs/NPs who work under a specific physician's supervision.
    Useful for finding post-operative follow-up providers.
    """
```

**Returns:**
```json
{
  "success": true,
  "physician_name": "Dr. Robert Martinez",
  "team_size": 1,
  "team_members": [
    {
      "provider_id": "PA003",
      "name": "Emily Carter",
      "credentials": "PA-C",
      "provider_type": "PA",
      "location": "Plano",
      ...
    }
  ]
}
```

**Added to OpenAI function calling tools** (9 tools total now)

### 5. Appointment Data Impact

**Before**: 6,256 total slots (4,397 available)
**After**: 11,184 total slots (7,846 available)
**Increase**: 4,928 additional slots (78% more availability)

Why? 7 new PAs/NPs × 60 days × average 11 slots/day = ~4,600 slots

## Expected Agent Behavior

### Before (INCORRECT):
```
Patient: "I need my 2-week follow-up for knee replacement surgery"

Agent: "Since you're in Dallas, let me check for orthopedic surgeons
available for your follow-up appointment in your area."
```
❌ **WRONG** - searching random surgeons

### After (CORRECT):
```
Patient: "I need my 2-week follow-up for knee replacement surgery"

Agent: "I see Dr. Martinez performed your knee replacement surgery on
October 10th. Let me check his availability for your follow-up."

[Checks Dr. Martinez availability]

Agent: "Dr. Martinez has several openings:
- October 28 at 10:30 AM
- October 28 at 4:00 PM
- October 29 at 2:30 PM"
```
✓ **CORRECT** - immediately checking original surgeon

### If Surgeon Unavailable:
```
Agent: "Dr. Martinez doesn't have availability in the next 2 weeks,
but I can schedule you with Emily Carter, PA-C, who works directly on
Dr. Martinez's team and commonly handles post-operative follow-ups.
Emily has openings on:
- October 28 at 8:30 AM
- October 28 at 9:00 AM"
```
✓ **CORRECT** - offering surgeon's PA as backup

## Testing Results

All tests passed:

✓ Patient info retrieval identifies operating surgeon (DR003)
✓ `get_provider_team(DR003)` returns Emily Carter, PA-C
✓ Dr. Martinez has 5 post-op follow-up slots in next 2 weeks
✓ Emily Carter (PA) has 5 post-op follow-up slots in next 2 weeks
✓ All 7 PAs/NPs correctly linked to supervising physicians
✓ Team-based care structure complete

## Files Modified

1. **[mock_data.py](mock_data.py)** - Provider model + 7 PA/NP providers (~150 lines)
2. **[rag.py](rag.py)** - Enhanced post-op protocol (~25 lines)
3. **[prompts.py](prompts.py)** - All 3 specialty agent prompts (~60 lines)
4. **[tools.py](tools.py)** - New `get_provider_team()` function + tool definition (~80 lines)

**Total**: ~315 lines changed/added across 4 files

## Medical Accuracy

This implementation now reflects real-world post-operative care:

✓ **Continuity of care**: Same surgeon for follow-ups
✓ **Team-based care**: PAs/NPs handle routine follow-ups
✓ **Provider hierarchy**: Surgeon → PA/NP → partner surgeon
✓ **Standard practice**: Wound checks by PAs/NPs common at 2 weeks
✓ **Access**: More appointment availability with team members

## Benefits

### For Patients:
- See the surgeon who performed their procedure (preferred)
- More appointment availability (PA/NP team increases slots 78%)
- Confidence in PA/NP care (standard practice explained)

### For Healthcare System:
- Efficient use of surgeon time (complex cases vs routine follow-ups)
- Better access to post-op care
- Reflects real-world surgical practice patterns

### For AI Agent:
- Medically accurate responses
- Proper provider hierarchy
- Natural explanation of team-based care

---

**Date Applied**: 2025-10-27
**Issue Reported By**: User (accurate medical protocol observation)
**Root Cause**: Agent was searching broadly instead of checking original surgeon
**Resolution**: Implemented team-based post-op care with proper provider hierarchy
