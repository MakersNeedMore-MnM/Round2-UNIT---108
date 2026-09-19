"""
Standard legal clause templates used by Agent 5 (Template Comparator).
Each entry: category → standard clause text + what ideal looks like.
"""

STANDARD_TEMPLATES = {
    "Liability": {
        "standard": "The aggregate liability of either party under this Agreement shall not exceed the total fees paid or payable by the Client in the twelve (12) months preceding the event giving rise to liability. In no event shall either party be liable for indirect, incidental, consequential, special, or punitive damages.",
        "key_elements": ["liability cap", "exclusion of consequential damages", "12-month fee cap", "mutual applicability"],
        "red_flags": ["no cap on damages", "unlimited liability", "one-sided liability", "no exclusion of consequential damages"],
    },
    "Termination": {
        "standard": "Either party may terminate this Agreement for convenience upon thirty (30) days' written notice. Either party may terminate immediately upon material breach if such breach is not cured within fifteen (15) days of written notice.",
        "key_elements": ["30-day notice for convenience", "15-day cure period", "mutual termination rights", "written notice requirement"],
        "red_flags": ["unilateral termination", "no cure period", "less than 15 days notice", "termination without cause allowed only for one party"],
    },
    "Payment Terms": {
        "standard": "Client shall pay all undisputed invoices within thirty (30) days of receipt. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law, whichever is lower. Client may dispute invoices in good faith within 10 days.",
        "key_elements": ["Net 30 payment", "1.5% monthly late fee cap", "dispute mechanism", "interest cap at legal maximum"],
        "red_flags": ["no payment timeline", "excessive late fees above 2%", "no dispute mechanism", "automatic renewal with payment"],
    },
    "Confidentiality": {
        "standard": "Each party agrees to maintain the confidentiality of the other party's Confidential Information using at least the same degree of care it uses to protect its own confidential information, but no less than reasonable care. This obligation survives termination for a period of three (3) years.",
        "key_elements": ["mutual obligation", "reasonable care standard", "3-year survival", "clear definition of confidential information"],
        "red_flags": ["one-sided confidentiality", "no survival clause", "indefinite duration", "no carve-outs for public domain"],
    },
    "IP Ownership": {
        "standard": "All intellectual property, inventions, and work product created by Vendor specifically for Client under this Agreement ('Work Product') shall be owned by Client. Vendor retains ownership of its pre-existing IP and general tools/methodologies.",
        "key_elements": ["client owns deliverables", "vendor retains background IP", "clear work-for-hire language", "license grant for vendor background IP"],
        "red_flags": ["vendor owns all deliverables", "no background IP carve-out", "joint ownership without governance", "unlimited license grant"],
    },
    "Indemnity": {
        "standard": "Each party ('Indemnitor') shall indemnify, defend, and hold harmless the other party ('Indemnitee') from third-party claims arising from Indemnitor's gross negligence or willful misconduct. Indemnification is mutual and capped at the liability limit.",
        "key_elements": ["mutual indemnification", "gross negligence / willful misconduct threshold", "third-party claims only", "cap on indemnification"],
        "red_flags": ["one-sided indemnification", "unlimited indemnification", "indemnification for ordinary negligence", "no threshold for indemnification trigger"],
    },
    "Dispute Resolution": {
        "standard": "Any dispute arising under this Agreement shall first be subject to good-faith negotiation for thirty (30) days. If unresolved, disputes shall be resolved by binding arbitration under the rules of [AAA/SIAC/ICC], with each party bearing its own costs.",
        "key_elements": ["negotiation first", "binding arbitration", "specified arbitration body", "cost-sharing"],
        "red_flags": ["litigation only", "one-sided choice of venue", "no negotiation requirement", "all costs on one party"],
    },
    "Force Majeure": {
        "standard": "Neither party shall be liable for delays or failures caused by events beyond reasonable control, including natural disasters, war, government action, or pandemic. The affected party must notify the other within five (5) business days and use reasonable efforts to mitigate impact.",
        "key_elements": ["mutual applicability", "5-day notification", "mitigation obligation", "defined qualifying events"],
        "red_flags": ["one-sided force majeure", "no notification requirement", "no mitigation obligation", "overly broad definition"],
    },
    "Warranties": {
        "standard": "Vendor warrants that services will be performed in a professional and workmanlike manner consistent with industry standards. EXCEPT AS EXPRESSLY STATED, ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR PURPOSE, ARE DISCLAIMED.",
        "key_elements": ["professional standards warranty", "disclaimer of implied warranties", "explicit warranty scope", "remedy for breach"],
        "red_flags": ["no warranty at all", "unlimited warranty scope", "no disclaimer of implied warranties", "no remedy specified"],
    },
    "General / Miscellaneous": {
        "standard": "This Agreement constitutes the entire agreement between the parties. Amendments must be in writing and signed by both parties. If any provision is found unenforceable, the remainder continues in full force.",
        "key_elements": ["entire agreement clause", "written amendment requirement", "severability", "waiver provision"],
        "red_flags": ["oral amendments allowed", "no severability", "no integration clause"],
    },
}
