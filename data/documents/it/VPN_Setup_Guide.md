# VPN Setup Guide - AI_OOPS Pvt. Ltd.

## Purpose
To provide step-by-step instructions for employees to configure, connect, and troubleshoot the corporate Virtual Private Network (VPN). This document serves as a foundational pillar of governance within AI_OOPS Pvt. Ltd., ensuring that all operational milestones are met with the highest standard of professionalism, corporate discipline, and ethical execution. In an era of rapid technological advancement and changing market demands, having a clear and well-defined framework is crucial. This document acts as a guide to mitigate operational risk, align individual employee actions with corporate values, and streamline workflows. Our objective is to establish clear communication protocols, reduce ambiguity, and maintain a highly compliant environment across all regional offices and departments. All stakeholders, partners, and personnel are expected to reference this policy as the primary source of truth for corporate governance.

## Scope
Applies to all employees and contractors requiring remote access to the internal AI_OOPS network. Specifically, this policy applies to all business segments, research groups, engineering divisions, sales territories, and corporate administrative wings. It encompasses all modes of work, including hybrid configurations, fully remote engagements, client-site deployments, and travel assignments. No department, subsidiary, or regional branch is exempt from the provisions detailed within. The rules apply equally to executive leadership, senior managers, technical leads, and junior associates, fostering a culture of mutual accountability and transparent operational metrics. Furthermore, temporary contractors, vendor representatives, and third-party auditors must also adhere to relevant sections of this document during their engagement with AI_OOPS.

## Responsibilities
Users are responsible for following this guide. The IT Helpdesk is responsible for provisioning credentials and assisting with connection failures. In addition to the primary owners, secondary responsibilities fall upon the compliance and risk management teams, who are tasked with conducting periodic audits to verify adherence to this framework. Line managers are expected to guide their team members through the process of implementation and address early signs of non-compliance. Individual contributors must proactively report system discrepancies or policy ambiguities. The Chief Operations Officer (COO) and Chief Financial Officer (CFO) maintain ultimate veto power regarding exceptions, and any deviations must be backed by a written business case that has cleared legal review. The continuous feedback loop from audits is used to refine these instructions over time.

## Policy
Access to AI_OOPS internal networks is restricted to approved corporate VPN clients. The VPN session must run MFA for verification. VPN credentials must not be shared. Split tunneling is disabled; all remote traffic routes through the secure corporate web gateway. AI_OOPS Pvt. Ltd. believes in fostering an environment of trust, safety, and mutual respect. Our core policy principles dictate that all assets, files, client data, and internal resources are protected under strict access controls and monitoring. We emphasize clear reporting lines, performance metrics, and compliance logs. Every corporate transaction and communication must reflect our focus on quality, respect for data privacy, and zero compromise on security. The organization does not tolerate any form of discrimination, hostile behavior, or administrative negligence. Employees are expected to coordinate across departmental boundaries to maintain operational security, efficient cost management, and client data integrity. Periodic updates to the core policy are driven by changes in industry standards, statutory mandates, and legal counsel feedback.

## Procedures
In order to implement the policy rules effectively, all staff must execute the following procedures:

1. download client: Open the IT Self-Service Portal and download the Cisco AnyConnect client for your OS.
2. configuration: Open client, enter gateway URL: `vpn.aioops-solutions.com`.
3. authentication: Enter employee username and password, then approve the OKTA push notification on your registered mobile device.
4. verification: Confirm that the connection status is 'Connected' and security software agent is green.

5. Auditing and Logging: All activities related to this workflow are logged in the AI_OOPS central compliance database. Log files are reviewed monthly by the internal audit team to identify anomalies or process bottlenecks.
6. Exception Management: If an employee requires an exception to the standard procedures, they must file an Exception Request Form (ERF) in the corporate intranet portal, specifying the business justification, duration, and potential risk mitigation factors. ERFs require sign-off from the department head and the compliance officer.
7. Continuous Training: All employees must complete the training module for this policy on the company's LMS within 30 days of hiring and complete refresher courses annually.

## Examples
The following scenarios illustrate how these policy guidelines should be applied in day-to-day operations:

An employee working from a home broadband connection opens the client, selects the 'IN-WEST-GATEWAY', completes the password login, and clicks 'Approve' on their Okta Verify mobile app to start work.

Another scenario involves a project lead who identifies a potential conflict during vendor evaluation. Instead of proceeding, the lead immediately updates the conflict register and requests a peer review to ensure objectivity. This quick escalation prevents future legal complications and maintains the integrity of AI_OOPS's procurement pipeline.

## Notes
VPN sessions will automatically time out and disconnect after 12 hours of continuous connection, requiring re-authentication. Additional legal and compliance notes:
- All communication logs, invoices, and files are subject to disclosure under applicable subpoena or regulatory review.
- AI_OOPS protects employee privacy, but corporate devices and networks are monitored for security compliance.
- Violations of local laws will result in immediate termination of the engagement and referral to law enforcement authorities.
- Regular updates to this document are distributed through the company intranet, and continued work constitutes agreement to terms.

## Frequently Asked Questions
Below are answers to common questions regarding the interpretation and application of this policy:

Q: The connection timed out. What should I do?
A: Verify your internet connection, restart the client software, and check if Okta services are online at status.okta.com.

Q: Can I connect my mobile phone to the corporate VPN?
A: Yes, only if the mobile device has been enrolled in the company MDM program.

Q: Whom should I contact if I have questions about this policy?
A: You can open a ticket in the employee service portal or reach out directly to the compliance department representative.

Q: What should I do if my manager asks me to bypass a procedure?
A: You must refuse the request and report the incident directly to the internal ethics helpline or the legal department.

## Revision History
| Version | Date | Author | Description of Changes |
| --- | --- | --- | --- |
| 1.0 | 2026-01-15 | Amit Patel (IT Operations Lead) | Initial FY26 Remote Access Documentation |
