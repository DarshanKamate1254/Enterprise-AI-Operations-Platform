# Incident Response Plan - BIA Pvt. Ltd.

## Purpose
To define the processes for detecting, investigating, containing, and recovering from security breaches and IT system failures. This document serves as a foundational pillar of governance within BIA Pvt. Ltd., ensuring that all operational milestones are met with the highest standard of professionalism, corporate discipline, and ethical execution. In an era of rapid technological advancement and changing market demands, having a clear and well-defined framework is crucial. This document acts as a guide to mitigate operational risk, align individual employee actions with corporate values, and streamline workflows. Our objective is to establish clear communication protocols, reduce ambiguity, and maintain a highly compliant environment across all regional offices and departments. All stakeholders, partners, and personnel are expected to reference this policy as the primary source of truth for corporate governance.

## Scope
Applies to all security incidents, system outages, data leaks, and cyberattacks at bia. Specifically, this policy applies to all business segments, research groups, engineering divisions, sales territories, and corporate administrative wings. It encompasses all modes of work, including hybrid configurations, fully remote engagements, client-site deployments, and travel assignments. No department, subsidiary, or regional branch is exempt from the provisions detailed within. The rules apply equally to executive leadership, senior managers, technical leads, and junior associates, fostering a culture of mutual accountability and transparent operational metrics. Furthermore, temporary contractors, vendor representatives, and third-party auditors must also adhere to relevant sections of this document during their engagement with bia.

## Responsibilities
The Incident Response Team (IRT) executes this plan. The Incident Commander directs operations. The PR team manages communications. In addition to the primary owners, secondary responsibilities fall upon the compliance and risk management teams, who are tasked with conducting periodic audits to verify adherence to this framework. Line managers are expected to guide their team members through the process of implementation and address early signs of non-compliance. Individual contributors must proactively report system discrepancies or policy ambiguities. The Chief Operations Officer (COO) and Chief Financial Officer (CFO) maintain ultimate veto power regarding exceptions, and any deviations must be backed by a written business case that has cleared legal review. The continuous feedback loop from audits is used to refine these instructions over time.

## Policy
All security incidents must be classified by severity: Low, Medium, High, or Critical. The IRT must be activated immediately for High and Critical events. We prioritize containment and data preservation over service availability during a breach. Regulatory notifications must occur within 72 hours of verification. BIA Pvt. Ltd. believes in fostering an environment of trust, safety, and mutual respect. Our core policy principles dictate that all assets, files, client data, and internal resources are protected under strict access controls and monitoring. We emphasize clear reporting lines, performance metrics, and compliance logs. Every corporate transaction and communication must reflect our focus on quality, respect for data privacy, and zero compromise on security. The organization does not tolerate any form of discrimination, hostile behavior, or administrative negligence. Employees are expected to coordinate across departmental boundaries to maintain operational security, efficient cost management, and client data integrity. Periodic updates to the core policy are driven by changes in industry standards, statutory mandates, and legal counsel feedback.

## Procedures
In order to implement the policy rules effectively, all staff must execute the following procedures:

1. identification: Alert from SIEM or employee report via incident ticket.
2. triage: Incident Commander assesses impact and assigns severity level within 30 minutes.
3. containment: Isolate affected hosts, disable compromised accounts, and deploy firewall blocks.
4. eradication & recovery: Remove malware, patch vulnerabilities, and restore systems from clean backups.
5. lessons learned: Conduct a post-mortem review meeting within 5 days of incident resolution.

5. Auditing and Logging: All activities related to this workflow are logged in the bia central compliance database. Log files are reviewed monthly by the internal audit team to identify anomalies or process bottlenecks.
6. Exception Management: If an employee requires an exception to the standard procedures, they must file an Exception Request Form (ERF) in the corporate intranet portal, specifying the business justification, duration, and potential risk mitigation factors. ERFs require sign-off from the department head and the compliance officer.
7. Continuous Training: All employees must complete the training module for this policy on the company's LMS within 30 days of hiring and complete refresher courses annually.

## Examples
The following scenarios illustrate how these policy guidelines should be applied in day-to-day operations:

If ransomware is detected on a server, the IRT isolates the server from the subnet immediately, takes RAM and storage snapshots for forensics, terminates compromised user credentials, and starts system rebuilds.

Another scenario involves a project lead who identifies a potential conflict during vendor evaluation. Instead of proceeding, the lead immediately updates the conflict register and requests a peer review to ensure objectivity. This quick escalation prevents future legal complications and maintains the integrity of bia's procurement pipeline.

## Notes
Every team member must be familiar with the out-of-band communication channel (Slack Enterprise grid on backup network) if standard communication goes down. Additional legal and compliance notes:
- All communication logs, invoices, and files are subject to disclosure under applicable subpoena or regulatory review.
- bia protects employee privacy, but corporate devices and networks are monitored for security compliance.
- Violations of local laws will result in immediate termination of the engagement and referral to law enforcement authorities.
- Regular updates to this document are distributed through the company intranet, and continued work constitutes agreement to terms.

## Frequently Asked Questions
Below are answers to common questions regarding the interpretation and application of this policy:

Q: Who can classify an incident as Critical?
A: Only the CISO or the Incident Commander has the authority to declare a Critical Incident.

Q: Are logs collected during containment?
A: Yes, all system, network, and security logs are copied to a write-once read-many (WORM) storage container for legal evidence.

Q: Whom should I contact if I have questions about this policy?
A: You can open a ticket in the employee service portal or reach out directly to the compliance department representative.

Q: What should I do if my manager asks me to bypass a procedure?
A: You must refuse the request and report the incident directly to the internal ethics helpline or the legal department.

## Revision History
| Version | Date | Author | Description of Changes |
| --- | --- | --- | --- |
| 1.0 | 2026-01-15 | Sanjay Mehta (CISO) | FY26 Cybersecurity Incident Response Plan |
