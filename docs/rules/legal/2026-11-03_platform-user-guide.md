# Poreva Open Platform User Guide

来源：2026-11-03 从 https://porevaopen.megalaxylab.com/challenges/egfr 页面内嵌的英文文件抽出。
这是页面里供勾选打开的正文，不是另行下载的 PDF。原文里的空段和 `$12` 段落按页面保留。

POREVA OPEN · PLATFORM USER GUIDE

Poreva Open — Global AI Protein Design Challenge: Platform User Guide

Table of Contents

1. What Is Poreva Open

2. Document Map: What You Should Read

3. Account and Verification

4. Platform Navigation

5. Participation Process

6. Submitting Designs: Formats and Fields

7. Pre-Submission Checklist

8. Viewing Results and Downloading Data

9. Awards and Prize Claims

10. Appeals and Feedback

11. Frequently Asked Questions

12. Contact Support

1. What Is Poreva Open Platform

Poreva Open Platform is a protein design challenge series platform initiated and hosted by MegaRobo Technologies (“MegaRobo”). The following 8 partners provide collaborative support in their respective fields of expertise (in the order in which cooperation commenced): Tencent Cloud, Twist, Galateck, Vazyme, Guangyao Digital Science & Technology, Silang, Future Capital, Inno Angel Fund. Each edition releases several real, clinically relevant targets, for which participants submit de novo designed binding molecules; the platform performs computational selection and wet-lab validation of the proposals and publishes the data publicly.

Wet-lab validation capacity is provided free of charge by Megalaxy Lab, so the designs you submit have the opportunity to complete the full “design — evaluation — experimental validation — data publication” cycle in a closed loop on a single platform.

2. Document Map: What You Should Read

We recommend reading the following four documents together in the order below; this guide assumes you already understand the basic concepts of the other three.

This guide (operational layer): how to do things

Platform Terms of Service (basic legal layer): permitted/prohibited conduct, consequences of breach

Official Competition Terms (competition charter layer): schedule, awards, IP, biosafety

Challenge Brief and Rules (challenge layer): specific targets, objectives, formats, submission details (one per challenge)

3. Account and Verification

3.1 Registration

Entry: “Register” at the top right of the official website homepage.

You will need:

An email address used by the team lead that can prove their affiliated work organization (domestic or overseas; an overseas email address will trigger the cross-border transfer under Section 8 of the Privacy Policy)

Steps:

Click “Register”

Enter your mobile phone number, email, username, and password (≥10 characters, including uppercase, lowercase, and digits)

Read and check to agree to the Platform Terms of Service and the Privacy Policy

After submitting, enter the Account Center

3.2 Real-Name Verification

Team name (≤30 characters)

Team member roster (≥3 members)

3.3 Notes on Team Participation

A team submits externally through a single account; the team representative is the holder of the registered account

Team member changes: may be adjusted before the submission window closes; no changes are permitted after it closes

4. Platform Navigation

The top main navigation has 5 sections:

| Section | Main Content |
| --- | --- |
| Home | Challenges currently in progress, key timeline, award announcements |
| Challenges | Past and current challenges (including targets, objectives, rules downloads, Q&A posts) |
| Submit | My designs, self-scoring metric calculator, submission history, review status |
| Data | Dataset downloads for completed rounds (under the ODC-BY 1.0 license) |
| Account Center | Profile, real-name verification, team, notifications, settings, help |

5. Participation Process

Participation has 5 steps. The description below follows a “what to do — where — what the result is” format.

1

Step 1: Read the Current Challenge Brief and Rules

Go to “Challenges” → select the current round

Download the Challenge Brief and Rules (PDF/Word)

Focus on: objectives (affinity/selectivity/others), format requirements, submission window

2

Step 2: Design Locally and Self-Score

Complete the sequence design as required by the rules

Complete the “self-check list” (see Section 7)

3

Step 3: Submit

Go to “Submit - New Design”

Select the current challenge

Paste or upload sequences (see Section 6 for details)

Enter your self-scores

Click “Submit” — the system immediately returns a submission_id and locks the status

Submissions cannot be edited once submitted. Please review and confirm your design before submitting.

4

Step 4: Wait for the Selection Notification

The platform applies hard screening to all submissions and confirms selected teams and sequences in order of submission time

Those who pass enter wet-lab validation at Megalaxy Lab free of charge

You will receive status changes such as “passed selection” and “not selected” in the “Notification Center”

5

Step 5: View Results and Download Data

Once the current round's wet-lab work is complete, the data will be publicly released on the Poreva Open platform

You can filter and download on the “Data” page by “Current Round - My Designs”

Winners claim prizes in accordance with Clause 7 of the Official Competition Terms

6. Submitting Designs: Formats and Fields

6.1 Accepted Design Types

| Format | Description | Length Limit (per chain) |
| --- | --- | --- |
| Single-chain protein | A single amino acid chain, with no constraints other than disulfide bonds | 40–250 aa |
| Nanobody | Single-domain antibody with an FR1–CDR3–FR4 framework | 40–250 aa |
| scFv | VH and VL are tandemly joined by a G4S flexible linker | 40–250 aa (counted as a single chain) |
| IgG1 paired variable regions (paired VH/VL) | VH/VL separated by an ASCII colon; the Organizer constructs full-length IgG1 for expression | 40–250 aa per chain |

6.2 CSV Fields

Submissions must be uploaded as a CSV file containing the following columns:

| Field | Meaning | Required | Notes |
| --- | --- | --- | --- |
| submission_id | Auto-generated by the system | No | Leave blank for first submission |
| AI model | The AI model used | Yes | e.g., AF2, Boltz-1, Chai-1 |
| name | Your sequence name for it | Yes | ≤50 characters |
| sequence | Sequence (single-chain / nanobody / scFv) | Depends on format | Required for single-chain format |
| description | Design rationale | No | ≤500 characters |

6.3 Sequence Character Requirements

Only the 20 standard amino acid letters are accepted (B/Z/U/X/* are not accepted; sequences containing stop codons will be rejected)

Length 40–250 aa; out-of-range sequences are rejected

No signal peptides or constant regions

Paired  VH/VL format: VH and VL must each meet the length requirement

6.4 How Many Designs Can Be Submitted per Challenge

| Format | Cap per Account |
| --- | --- |
| Single-chain protein, nanobody, scFv (combined), paired VH/VL | 24 |

7. Pre-Submission Checklist

| # | Check Item | Reason |
| --- | --- | --- |
| 1 | The sequence contains only the 20 standard amino acid letters | B/Z/U/X/* triggers a hard rejection |
| 2 | Sequence length 40–250 aa | Non-compliant length triggers a hard rejection |
| 3 | The sequence contains no signal peptide | Signal peptides alter membrane/secretion behavior |
| 4 | The sequence contains no stop codon | Stop codons trigger a hard rejection |
| 5 | Submission format fields match (single-chain vs. paired) | Field mismatches trigger a hard rejection |
| 6 | All sequences submitted by the same account in this cycle are pairwise distinct | Duplicate sequences trigger a hard rejection |
| 7 | The scFv linker is a standard GS linker (GGGGS×n recommended) | Non-standard linkers may alter expressibility |
| 8 | For the paired format, VH and VL each meet the length requirement | Non-compliance of either chain triggers a hard rejection |
| 9 | You have read the “hard screening criteria” in the current Challenge Brief and Rules | Those who do not meet the criteria cannot enter wet-lab validation |

8. Viewing Results and Downloading Data

8.1 Status Notifications

The platform sends you notifications at the following milestones:

Submission successful

Entered hard screening / failed hard screening

Entered wet-lab validation / not selected for wet-lab validation

Wet-lab validation completed; results published

Award won

You can choose notification channels (in-platform, email, SMS, WeCom) in “Account Center - Notification Settings.”

8.2 Dataset Downloads

Datasets from completed rounds are publicly available to everyone (under the ODC-BY 1.0 license; please read the full license before use)

Fields include: sequence, self-scored metrics, measured KD/expression level/specificity, etc.

Identity information of individual participants does not enter the public dataset; only the team name/account ID appears

9. Awards and Prize Claims

See Clause 7 of the Official Competition Terms for details

After winning, the system automatically enters the “prize claim” process; bank card and tax vouchers must be provided

Prize arrival time: subject to actual settlement with the third-party payment channel, usually within 30 working days

10. Appeals and Feedback

Selection/scoring objections: appeals may be submitted within 14 calendar days of the results publication

Technical failures: tickets may be submitted within 30 calendar days of the incident

Academic misconduct reports: open on an ongoing basis; after submission, the DPO leads the investigation

Appeals and reports are submitted via “Help - Appeals and Reports” or the official email. Appeals must provide complete facts and supporting evidence; the Organizer has the right not to accept objections submitted after the deadline.

11. Frequently Asked Questions

Q1: Can I participate in multiple challenges at the same time?

A: Yes. Each challenge is submitted separately and counted independently (see Section 6.4).

Q2: Can team members submit independently using different accounts?

A: No. The team representative's account is the team's sole submission entry. If other members submit using personal accounts, such submissions are deemed individual participation and are unrelated to the team.

Q3: Can I modify my submission after submitting?

A: Submissions cannot be withdrawn or modified after submission; please confirm before submitting.

Q4: I am not a resident of mainland China. Can I participate?

A: This competition is an open format for participants worldwide; non-residents of mainland China may also participate.

Q5: What AI tools can I use for design?

A: Fully open. This competition does not mandate tools or restrict their sources.

Q6: How likely is my design to be wet-lab validated?

A: Each challenge plans to validate approximately 2,000 design sequences. The likelihood of validation depends on the design quality of the submitted sequences, the completeness of the information provided, and the total number of competition submissions. Not all designs will enter the wet-lab validation list.

Q7: Can the public data be used commercially?

A: Yes, commercial use is permitted under the ODC-BY 1.0 license, but you must prominently mark it as “based on Poreva Open Challenge data.” Derivative databases must also be made available under the same license.

12. Contact Support

Official email (preferred): poreva_open@megarobo.com

Customer service hours: weekdays 09:00–18:00 (Beijing time)

For urgent security issues, please email directly and mark the subject “[URGENT] Security”; we commit to a first reply within 24 hours.
