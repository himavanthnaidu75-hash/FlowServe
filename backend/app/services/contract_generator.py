"""
Contract Generator — creates professional contracts from templates.
Supports: Service Agreements, SOWs, NDAs, Change Orders.
"""
from datetime import datetime, timezone

CONTRACT_TEMPLATES = {
    "service_agreement": {
        "name": "Service Agreement",
        "content": """# SERVICE AGREEMENT

**Effective Date:** {start_date}

**Between:**
- **Service Provider:** {provider_name}
- **Client:** {client_name}

---

## 1. Scope of Services

{scope_description}

## 2. Term

This Agreement shall commence on {start_date} and continue until {end_date}, unless terminated earlier.

## 3. Compensation

**Total Fee:** ${total_amount:,.2f}

**Payment Schedule:** {payment_terms}

## 4. Intellectual Property

Upon full payment, all work product created under this Agreement shall be assigned to the Client.

## 5. Confidentiality

Both parties agree to maintain confidentiality of proprietary information shared during the engagement.

## 6. Limitation of Liability

Provider's total liability shall not exceed the total fees paid under this Agreement.

## 7. Termination

Either party may terminate with 14 days written notice. Client shall pay for work completed through termination date.

---

**Provider Signature:** _________________________ Date: _________

**Client Signature:** _________________________ Date: _________
""",
    },
    "sow": {
        "name": "Statement of Work",
        "content": """# STATEMENT OF WORK

**Project:** {project_name}
**Client:** {client_name}
**Date:** {start_date}

---

## 1. Project Overview

{scope_description}

## 2. Deliverables

{deliverables}

## 3. Timeline

**Start Date:** {start_date}
**End Date:** {end_date}

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Discovery & Planning | 1 week | Requirements signed off |
| Design | 1 week | Design approved |
| Development | 2 weeks | Core features complete |
| Testing & QA | 1 week | All tests passing |
| Launch | 1 day | Go-live |

## 4. Acceptance Criteria

- All deliverables meet agreed specifications
- Client review and approval within 5 business days of submission
- No more than 2 rounds of revisions per deliverable

## 5. Fees

**Total Project Fee:** ${total_amount:,.2f}

| Milestone | Amount | Due |
|-----------|--------|-----|
| Project kickoff | ${milestone_1:,.2f} | Upon signing |
| Design approval | ${milestone_2:,.2f} | Week 2 |
| Final delivery | ${milestone_3:,.2f} | Week 4 |

## 6. Change Requests

Any changes to scope will be documented as Change Orders with separate pricing.

---

**Provider:** _________________________ Date: _________

**Client:** _________________________ Date: _________
""",
    },
    "nda": {
        "name": "Non-Disclosure Agreement",
        "content": """# NON-DISCLOSURE AGREEMENT

**Effective Date:** {start_date}

**Between:**
- **Disclosing Party:** {client_name}
- **Receiving Party:** {provider_name}

---

## 1. Purpose

This NDA protects confidential information shared during the business relationship.

## 2. Confidential Information

"Confidential Information" includes all non-public information disclosed by either party, including:
- Business plans, strategies, and financial information
- Technical data, designs, and specifications
- Client lists and customer information
- Proprietary processes and methods

## 3. Obligations

The Receiving Party shall:
- Use Confidential Information only for evaluation of business relationship
- Protect it with same care as its own confidential information
- Not disclose to third parties without written consent
- Return or destroy upon termination of relationship

## 4. Exclusions

Information that:
- Was publicly known at time of disclosure
- Becomes publicly known through no fault of receiving party
- Was already known to receiving party prior to disclosure
- Is independently developed without use of confidential information

## 5. Term

This NDA remains in effect for 2 years from {start_date}.

## 6. Remedies

Both parties acknowledge that breach may cause irreparable harm and entitle the injured party to seek injunctive relief.

---

**Provider:** _________________________ Date: _________

**Client:** _________________________ Date: _________
""",
    },
    "change_order": {
        "name": "Change Order",
        "content": """# CHANGE ORDER

**Change Order #:** {change_order_number}
**Project:** {project_name}
**Date:** {start_date}

---

## 1. Original Scope

{original_scope}

## 2. Requested Changes

{scope_description}

## 3. Impact

**Additional Fee:** ${total_amount:,.2f}
**Timeline Extension:** {timeline_extension} days

## 4. Justification

This change order addresses modifications to the original project scope as requested by the Client.

---

**Provider:** _________________________ Date: _________

**Client:** _________________________ Date: _________
""",
    },
}


def generate_contract(
    template_type: str,
    variables: dict,
    custom_content: str = None,
) -> dict:
    """Generate a contract from template with variable substitution."""
    template = CONTRACT_TEMPLATES.get(template_type)
    if not template:
        raise ValueError(f"Unknown template type: {template_type}")

    content = custom_content or template["content"]

    # Fill in default dates
    now = datetime.now(timezone.utc)
    defaults = {
        "start_date": now.strftime("%B %d, %Y"),
        "end_date": now.replace(month=now.month % 12 + 1 if now.month < 12 else 1).strftime("%B %d, %Y"),
        "provider_name": "[Your Company]",
        "client_name": "[Client Name]",
        "project_name": "[Project Name]",
        "scope_description": "[Project scope description]",
        "deliverables": "- Deliverable 1\n- Deliverable 2\n- Deliverable 3",
        "total_amount": 0,
        "payment_terms": "50% upfront, 50% upon completion",
        "milestone_1": 0,
        "milestone_2": 0,
        "milestone_3": 0,
        "original_scope": "[Original scope description]",
        "timeline_extension": 0,
        "change_order_number": "CO-001",
    }

    all_vars = {**defaults, **variables}

    try:
        filled = content.format(**all_vars)
    except KeyError:
        filled = content

    return {
        "template_type": template_type,
        "template_name": template["name"],
        "content": filled,
        "variables": all_vars,
    }
