import os
import csv
import random
import datetime

# Setup directories
base_dir = r"d:\projects\ai_eng\data"
doc_dirs = {
    "hr": os.path.join(base_dir, "documents", "hr"),
    "finance": os.path.join(base_dir, "documents", "finance"),
    "sales": os.path.join(base_dir, "documents", "sales"),
    "it": os.path.join(base_dir, "documents", "it"),
    "customer_support": os.path.join(base_dir, "documents", "customer_support"),
    "inventory": os.path.join(base_dir, "documents", "inventory")
}
db_dir = os.path.join(base_dir, "database")

for d in list(doc_dirs.values()) + [db_dir]:
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------
# 1. TEXT TEMPLATE DATA FOR MARKDOWN DOCUMENTS
# ----------------------------------------------------

# We will define a rich generator helper to compile detailed documents that meet word counts.
# Each document has structured sections that are specific, realistic, and contain no Lorem Ipsum.

docs_metadata = {
    "hr": {
        "Employee_Handbook.md": {
            "title": "Employee Handbook",
            "purpose": "To serve as a comprehensive reference guide outlining the core values, employment conditions, workplace guidelines, and standard operating expectations at Darshan_AI_Engineer_Ops Pvt. Ltd.",
            "scope": "This handbook applies to all regular full-time, part-time, temporary, and contract employees of Darshan_AI_Engineer_Ops Pvt. Ltd., across all locations, subsidiaries, and corporate offices globally.",
            "responsibilities": "The Human Resources Department is responsible for maintaining and updating this handbook. Executive leadership is responsible for reinforcing these policies, and all employees are responsible for reading, understanding, and adhering to the guidelines outlined herein.",
            "policy": "Darshan_AI_Engineer_Ops is committed to providing a professional, inclusive, and high-performing workspace. We operate under a strict code of equal opportunity, zero tolerance for harassment, and dedication to personal development. We expect all team members to exhibit professionalism, integrity, and client-centric behavior in all operations.",
            "procedures": "1. onboarding: All new hires must complete background verification and sign this handbook's acknowledgment within 3 business days.\n2. working hours: Standard business hours are 9:00 AM to 6:00 PM, Monday through Friday, with flexible core hours from 10:00 AM to 4:00 PM.\n3. performance reviews: Done semi-annually in June and December. Review templates must be completed in the HR portal.\n4. reporting grievances: Any violation of workplace policy must be reported immediately to the HR generalist via the anonymous hotline or HR portal.",
            "examples": "If an employee experiences a conflict with a colleague, they should first attempt to resolve it professionally. If unresolved, they must document the incident and schedule a resolution meeting with HR.\nFor flex-time, if an employee needs to start at 8:00 AM, they should log this preference in the HR MS and ensure core-hour availability is maintained.",
            "notes": "This handbook is subject to local employment laws and statutory regulations in India, the USA, and Singapore. In the event of a conflict between this document and local labor laws, local laws will take precedence.",
            "faq": "Q: Can I work fully remote?\nA: Remote work eligibility is determined by the department head and HR. Darshan_AI_Engineer_Ops operates on a hybrid model (3 days in-office, 2 days remote).\n\nQ: How do I request a duplicate ID card?\nA: Submit an IT service ticket under the 'Facilities' category.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Ananya Sharma (HR Director) | Initial Release for FY 2026 |\n| 1.1 | 2026-06-01 | Ananya Sharma (HR Director) | Updated Hybrid Work Policy guidelines |"
        },
        "Leave_Policy.md": {
            "title": "Leave Policy",
            "purpose": "To define the types of leaves available to Darshan_AI_Engineer_Ops employees, eligibility criteria, accrual methods, and the application and approval processes.",
            "scope": "Applies to all regular full-time and part-time employees on the Darshan_AI_Engineer_Ops payroll globally.",
            "responsibilities": "Employees must submit leave requests in advance. Managers are responsible for reviewing and approving leaves in a timely manner while ensuring operational continuity. HR tracks balances and handles compliance.",
            "policy": "Darshan_AI_Engineer_Ops offers generous paid time off to promote work-life balance, recovery, and personal well-being. Annual leave allocations include Casual Leave (CL), Sick Leave (SL), Earned Leave (EL), Maternity Leave, Paternity Leave, and Bereavement Leave. Unused Earned Leaves up to 30 days can be carried forward to the next calendar year.",
            "procedures": "1. application: Submit leave requests via the HR Portal at least 5 business days in advance for planned leaves (EL).\n2. emergency leave: For unplanned leaves (SL/CL), notify the immediate manager via email/Slack before 9:30 AM on the day of absence.\n3. documentation: Medical certificates are mandatory for sick leaves exceeding 3 consecutive business days.\n4. approval workflow: Requests go to the immediate manager. If approved, the HR portal updates leave balances automatically.",
            "examples": "An employee planning a 10-day vacation must submit the request in the HR Portal at least 2 weeks in advance. The manager reviews team calendar availability and approves, allowing the employee to plan without causing workflow bottleneck.",
            "notes": "Leaves cannot be clubbed in a manner that disrupts critical deliverable milestones. Maternity leave provides 26 weeks of paid leave, and Paternity leave provides 2 weeks of paid leave, in accordance with statutory guidelines.",
            "faq": "Q: Can I encash my leaves?\nA: Earned leaves can be encashed only at the time of separation from the company, up to a maximum of 45 days.\n\nQ: What happens if I take leave without approval?\nA: Unauthorized absences are treated as loss of pay (LOP) and may lead to disciplinary action.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Ananya Sharma (HR Director) | FY26 Consolidated Leave Policy Launch |"
        },
        "Attendance_Policy.md": {
            "title": "Attendance Policy",
            "purpose": "To establish clear guidelines regarding punctuality, daily attendance tracking, core working hours, and the management of unscheduled absences.",
            "scope": "Applies to all employees working from corporate offices or remote locations on behalf of Darshan_AI_Engineer_Ops.",
            "responsibilities": "All employees must log their daily attendance. Managers must monitor attendance logs, review timecards weekly, and address chronic punctuality issues with HR guidance.",
            "policy": "Consistent attendance and punctuality are essential for Darshan_AI_Engineer_Ops's collaborative work culture. We expect employees to be ready to work by their scheduled start time. Daily tracking is managed via biometric access in office facilities and VPN logs for remote workers. Core operational hours are 10:00 AM to 4:00 PM IST.",
            "procedures": "1. daily check-in: Tap biometric card at the security gate or log into the VPN and check-in on the HR Portal.\n2. core-hour compliance: Be present or online during core hours (10:00 AM - 4:00 PM).\n3. late arrivals: Notify the manager if arriving after 10:30 AM. Accumulating more than 3 late arrivals in a month triggers warning.\n4. tracking corrections: Submit attendance regularization requests within 48 hours in the portal for missed taps.",
            "examples": "If an employee's biometric card fails to register a check-in, they must log into the HR portal, click 'Regularize Attendance', choose the date, input actual check-in/out times, and submit for manager approval.",
            "notes": "Chronic absenteeism or tardiness without justifiable cause is considered a violation of employment terms and will be subject to progressive disciplinary action, up to termination.",
            "faq": "Q: How are remote days tracked?\nA: Remote attendance is tracked by checking in on the portal and maintaining active VPN session connectivity during standard hours.\n\nQ: What is the penalty for missed check-ins?\nA: Unregularized missed check-ins will automatically default to Leave Without Pay (LWP) at the end of the month.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Rajesh Verma (Operations Manager) | Initial Release for FY 2026 |\n| 1.1 | 2026-05-10 | Rajesh Verma (Operations Manager) | Added biometric correction protocols |"
        },
        "Travel_Policy.md": {
            "title": "Travel Policy",
            "purpose": "To outline rules, approvals, and spending limits for corporate business travel, ensuring employee safety, cost control, and consistent expense recording.",
            "scope": "Applies to all domestic and international business travel undertaken by Darshan_AI_Engineer_Ops employees.",
            "responsibilities": "Employees must obtain prior travel approval and submit accurate expenses. The Finance travel desk handles bookings. Managers approve travel requests and budget allocations.",
            "policy": "Darshan_AI_Engineer_Ops supports necessary business travel. We expect employees to exercise prudent judgment when incurring travel expenses. Travel classes (Economy for domestic, Premium Economy or Business for international flights exceeding 8 hours) are determined by employee grade levels. Safe and clean accommodation must be booked via approved corporate vendors.",
            "procedures": "1. pre-approval: Submit a Travel Request Form (TRF) on the travel portal at least 14 days before domestic and 30 days before international travel.\n2. booking: Once approved, the travel desk shares flight and hotel options. Select options within the grade limits.\n3. daily allowance: Daily out-of-pocket allowances (Per Diem) are provided based on location tier.\n4. expense report: Submit an expense report with original receipts in the Finance portal within 7 business days of return.",
            "examples": "An Engineer travelling to Hyderabad for a client installation submits a TRF. The system routes it to the VP of Engineering. Upon approval, the travel desk books a Tier-1 business hotel and economy flight. The engineer tracks meal receipts during the trip.",
            "notes": "Any corporate credit card utilization during travel must strictly comply with the credit card usage guidelines. Personal travel extensions combined with business trips are allowed but all incremental costs must be paid by the employee.",
            "faq": "Q: Can I book my own flights?\nA: No, all bookings must be processed by the Darshan_AI_Engineer_Ops travel desk to avail of corporate discount rates.\n\nQ: What happens if I lose a receipt?\nA: For expenses under INR 500, a written declaration is accepted. Above that, missing receipts require department head approval.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Vikram Sen (VP Finance) | FY26 Unified Corporate Travel Policy |"
        },
        "Code_of_Conduct.md": {
            "title": "Code of Conduct",
            "purpose": "To define the ethical standards, behavioral expectations, and corporate responsibilities required of all employees and stakeholders at Darshan_AI_Engineer_Ops.",
            "scope": "Applies to all employees, board members, vendors, partners, and contractors representing Darshan_AI_Engineer_Ops globally.",
            "responsibilities": "Every individual is responsible for acting with integrity. Managers must foster an ethical work culture and escalate potential violations. The Ethics Committee investigates reports.",
            "policy": "Darshan_AI_Engineer_Ops maintains a zero-tolerance policy for unethical behavior, bribery, conflicts of interest, discrimination, and harassment. We operate transparently and protect intellectual property. We respect diversity and are committed to creating a safe work environment.",
            "procedures": "1. conflict disclosure: Employees must disclose potential conflicts of interest (e.g., family member working for a competitor) annually or when they arise.\n2. reporting: Report violations to ethics@Darshan_AI_Engineer_Ops.com or via the anonymous whistleblower portal.\n3. investigation: The Ethics Committee conducts a confidential inquiry within 15 business days.\n4. disciplinary actions: Violations will lead to disciplinary measures, including warning, suspension, or immediate termination.",
            "examples": "If a vendor offers an employee a gift of high value (above INR 2,000) during contract negotiations, the employee must politely decline and report the gesture to the Ethics Committee.",
            "notes": "This policy complies with global anti-bribery statutes, including the FCPA (US) and the Bribery Act (UK). Whistleblowers are protected from any form of retaliation or adverse career impact.",
            "faq": "Q: Can I take a freelance job on weekends?\nA: External employment is generally not permitted if it conflicts with Darshan_AI_Engineer_Ops's business or uses company resources. Prior written approval from HR is mandatory.\n\nQ: What should I do if I suspect financial fraud in my team?\nA: File a report through the whistleblower portal immediately. It will be routed directly to the Head of Audit.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Devendra Rao (Chief Legal Officer) | FY26 Global Code of Conduct Launch |"
        }
    },
    "finance": {
        "Finance_Policy.md": {
            "title": "Finance Policy",
            "purpose": "To establish the core financial controls, authorization matrices, budget allocations, and auditing protocols of Darshan_AI_Engineer_Ops.",
            "scope": "Applies to all financial transactions, procurements, vendor payments, and cost-center allocations within Darshan_AI_Engineer_Ops.",
            "responsibilities": "The Chief Financial Officer (CFO) has ultimate oversight. Department heads manage their allocated budgets. The internal audit team conducts quarterly compliance checks.",
            "policy": "All financial operations must be conducted with transparency, strict record-keeping, and compliance with statutory financial reporting standards (GAAP/IFRS). Capital expenditures (CAPEX) and Operational expenditures (OPEX) require explicit sign-offs in accordance with the authorization matrix. No transaction may be processed without a valid purchase order or invoice.",
            "procedures": "1. vendor setup: Submit vendor onboarding forms, tax registration numbers, and banking details to the Finance portal.\n2. purchase requisitions: Raise a PR in the ERP tool for any purchase exceeding INR 10,000.\n3. payment run: Standard vendor payment cycle is Net-30 from invoice approval date, executed weekly on Fridays.\n4. internal audit: Cooperate with the audit team by providing all ledger records, invoices, and bank reconciliation statements.",
            "examples": "To procure new software licenses for engineering, the manager raises a PR, routes it for VP approval, receives a PO, receives the vendor invoice, and routes the invoice to finance for Net-30 payment processing.",
            "notes": "All financial records must be preserved for a minimum of 7 years in compliance with national tax laws and corporate accounting regulations.",
            "faq": "Q: Can we expedite vendor payments?\nA: Urgent payments (Net-7 or Net-15) require written justification and approval from the VP of Finance.\n\nQ: What is a cost-center code?\nA: A unique code assigned to each department to track their monthly expenditures. Contact finance support to get your team's code.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Vikram Sen (VP Finance) | FY26 Financial Controls Framework |"
        },
        "Expense_Reimbursement.md": {
            "title": "Expense Reimbursement Policy",
            "purpose": "To define guidelines for claiming reimbursement for business-related expenses incurred by employees during corporate duties.",
            "scope": "Applies to all employees of Darshan_AI_Engineer_Ops claiming reimbursements for business travel, client entertainment, internet allowance, and minor office supplies.",
            "responsibilities": "Employees must submit accurate claims with receipts. Managers must review claims for policy compliance before approval. Finance audits and processes payouts.",
            "policy": "Darshan_AI_Engineer_Ops reimburses legitimate business expenses. Claims must be submitted within 30 days of the expense date. Entertainment expenses must specify client names and business purposes. Personal expenses, traffic fines, and alcohol purchases are strictly non-reimbursable.",
            "procedures": "1. claim submission: Log into the Expense Tool, enter claim details, select cost center, and upload digital receipts.\n2. approval workflow: The claim is routed to the line manager. Claims above INR 25,000 also require VP approval.\n3. auditing: Finance reviews receipts against policy limits. Non-compliant items are rejected or returned for explanation.\n4. payout: Approved claims are processed and paid out on the 10th and 25th of every month.",
            "examples": "An employee hosting a client dinner spends INR 5,000. They request an itemized tax invoice, take a photo, log a claim under 'Client Entertainment', name the client attendees, and submit for manager approval.",
            "notes": "Falsification of receipts, claiming personal expenses, or double-claiming will be treated as serious financial misconduct and may lead to termination.",
            "faq": "Q: Can I claim broadband expenses?\nA: Yes, employees on hybrid/remote setups can claim internet reimbursement up to INR 1,500 monthly by uploading the service bill.\n\nQ: Is there a limit on client lunch expenses?\nA: Yes, client meals are capped at INR 1,500 per person. Exceptions require pre-approval from the department head.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Vikram Sen (VP Finance) | Consolidated Expense Guidelines FY26 |"
        },
        "Budget_Guidelines.md": {
            "title": "Budget Guidelines",
            "purpose": "To outline the corporate budgeting cycle, methods for department budget planning, tracking rules, and variance management.",
            "scope": "Applies to all department heads, project managers, and budget owners across Darshan_AI_Engineer_Ops.",
            "responsibilities": "The Finance Planning & Analysis (FP&A) team defines the budget calendar. Department heads prepare, submit, and manage their department budgets. CFO approves the master budget.",
            "policy": "Darshan_AI_Engineer_Ops operates on an annual budgeting cycle with quarterly reviews. Departments must stick to their allocated budgets. Over-budget spends are not permitted without an approved variance request. Underspent budgets cannot be rolled over to the next year without CFO approval.",
            "procedures": "1. planning: FP&A releases budget templates in October. Department heads submit drafts by November 15.\n2. review: FP&A and CFO conduct review meetings in December to align department budgets with corporate revenue goals.\n3. allocation: Approved budgets are uploaded into the ERP system on January 1.\n4. tracking: Monthly variance reports (Actual vs. Budget) are sent to department heads on the 5th of every month.",
            "examples": "If the engineering team needs to recruit 5 additional developers, the VP must check if the salary budget has variance room. If not, they must submit a budget amendment request to the FP&A team.",
            "notes": "Emergency budget requests are subject to strict scrutiny and require direct approval from the Executive Committee (CEO and CFO).",
            "faq": "Q: What is a variance threshold?\nA: A variance within +/- 5% is acceptable. Anything exceeding 5% over-budget requires a formal explanation to the CFO.\n\nQ: Can I transfer budget from marketing to engineering?\nA: No, budget transfers between departments are not allowed without written approval from both department heads and the CFO.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Vikram Sen (VP Finance) | FY26 Corporate Budget Allocation Rules |"
        }
    },
    "sales": {
        "Sales_Guidelines.md": {
            "title": "Sales Guidelines",
            "purpose": "To define the ethical guidelines, pipeline stages, lead allocation, and performance metrics for the Darshan_AI_Engineer_Ops Sales team.",
            "scope": "Applies to all Sales Representatives, Account Executives, and Sales Managers at Darshan_AI_Engineer_Ops.",
            "responsibilities": "Sales team members must represent Darshan_AI_Engineer_Ops with integrity. Sales managers are responsible for pipeline reviews. The VP of Sales oversees revenue targets and commissions.",
            "policy": "Sales efforts must be conducted with honesty. We do not engage in predatory sales practices, deceptive comparisons, or side-agreements. All client commitments must be written and approved in the formal Master Services Agreement (MSA) or Statement of Work (SOW). Leads are allocated based on geography and industry expertise.",
            "procedures": "1. lead capture: Log all inquiries in the CRM system within 2 hours of receipt.\n2. qualification: Use the BANT framework (Budget, Authority, Need, Timeline) to qualify leads.\n3. proposal: Use corporate proposal templates. Any customization of standard pricing must follow the Pricing Policy.\n4. contract closure: Route all contracts through the Legal team before client signature.",
            "examples": "A sales representative qualifying an enterprise lead identifies a budget of INR 2,000,000. They log it in the CRM under 'Qualified Stage', and assign it to the appropriate Technical Account Executive.",
            "notes": "Sales commissions are calculated based on closed-won deals that have completed their first invoice payment. Late client payments will delay commission payouts.",
            "faq": "Q: Can I sell to a customer in another region?\nA: Territory rules are strict. Cross-region sales require coordination and approval from the VPs of both regions.\n\nQ: How often should the CRM be updated?\nA: The CRM must be updated daily. Outdated pipelines will impact commission calculations.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Sarah Jenkins (VP Sales) | FY26 Sales Standard Operating Procedures |"
        },
        "Pricing_Policy.md": {
            "title": "Pricing Policy",
            "purpose": "To establish the official product pricing sheets, subscription models, and pricing authority levels at Darshan_AI_Engineer_Ops.",
            "scope": "Applies to all products, SaaS services, and support contracts offered by Darshan_AI_Engineer_Ops.",
            "responsibilities": "The Product Management and Finance teams set standard prices. Sales representatives must quote prices in alignment with the official pricing sheet. CFO approves any custom price structures.",
            "policy": "Darshan_AI_Engineer_Ops offers transparent subscription-based and usage-based pricing. Standard pricing is updated annually on January 1. Quoted rates are valid for 30 days from the proposal date. All custom bundles or enterprise packages require pricing committee sign-off.",
            "procedures": "1. pricing quote: Retrieve standard pricing from the CRM product catalog.\n2. custom quote: For non-standard deals, compile a pricing proposal using the Custom Deal calculator.\n3. submission: Route custom proposals to the Pricing Committee in the ERP system.\n4. documentation: Attach the approved pricing sheet to the contract draft.",
            "examples": "For a customer requesting 500 licenses of NovaShield Enterprise, the Sales Rep quotes the standard rate of INR 10,000/license/year. For a discount request, they must consult the Discount Policy.",
            "notes": "All prices exclude applicable local sales taxes, VAT, and GST, which are calculated and added at the time of invoicing.",
            "faq": "Q: Can we guarantee a price lock for 3 years?\nA: Price locks are permitted for multi-year contracts, subject to a minimum contract duration of 36 months and VP Sales approval.\n\nQ: What is usage-based pricing?\nA: It applies to data ingestion products where customers pay based on gigabytes processed monthly.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Sarah Jenkins (VP Sales) | FY26 Master Product Pricing Policy |"
        },
        "Discount_Policy.md": {
            "title": "Discount Policy",
            "purpose": "To define the limits, approval matrices, and criteria for applying discounts to Darshan_AI_Engineer_Ops products and services.",
            "scope": "Applies to all sales deals, renewals, and enterprise contracts.",
            "responsibilities": "Sales representatives must apply discounts within authorized boundaries. Sales Managers and VPs review and approve higher discounts in CRM.",
            "policy": "Darshan_AI_Engineer_Ops discourages excessive discounting to preserve product value and margin. Discounts are categorized as Standard, Manager-approved, or VP-approved. No discount above 30% is allowed without written CFO and VP Sales approval. Multi-year commitments (2+ years) qualify for automatic tier discounts.",
            "procedures": "1. threshold check: Up to 5% discount: Sales Rep auto-approval. 5.1% to 15%: Line Manager approval. 15.1% to 30%: VP Sales approval. > 30%: CFO approval.\n2. request submission: Input the requested discount percentage in the CRM deal record, attaching a business justification.\n3. approval tracking: The system automatically blocks deal progress until approval is logged.\n4. invoicing: The finance billing team verifies the CRM discount approval log before generating the invoice.",
            "examples": "A client requests a 12% discount on a 1-year SaaS contract. The Sales Rep enters the discount in the CRM, which routes to their Manager. The Manager reviews the client's growth potential and approves it.",
            "notes": "Discounts cannot be applied retroactively to invoices that have already been generated or paid.",
            "faq": "Q: Do renewals qualify for discounts?\nA: Renewals are usually processed at flat pricing. Discounts on renewals are discouraged unless there is a significant volume expansion.\n\nQ: Can we bundle free support as a discount?\nA: Yes, but the cost of support must be accounted for and approved in accordance with the discount matrix.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Sarah Jenkins (VP Sales) | FY26 Consolidated Discount Guidelines |"
        }
    },
    "it": {
        "IT_SOP.md": {
            "title": "IT Standard Operating Procedures",
            "purpose": "To outline standard operating procedures for IT assets, user onboarding/offboarding, systems management, and hardware replacement.",
            "scope": "Applies to all IT hardware, software licenses, network infrastructure, and connected devices owned or managed by Darshan_AI_Engineer_Ops.",
            "responsibilities": "The IT Operations team implements this SOP. Employees must comply with device handling rules. The IT Manager audits hardware audits quarterly.",
            "policy": "All corporate assets are company property. They must be secured, monitored, and used for professional purposes. Unapproved software installation is strictly prohibited. Operating systems and security agents must be kept up to date automatically.",
            "procedures": "1. hardware provisioning: Onboard new hires with a standard laptop, monitor, and peripherals. Record serial numbers in the IT asset database.\n2. software requests: Raise software license requests through the IT Service Desk. All software must be from the approved catalog.\n3. offboarding: Upon separation, return all hardware to the IT desk on or before the last working day.\n4. patching: Standard OS updates are pushed weekly on Wednesday nights. Laptops must be kept connected.",
            "examples": "An employee needs Docker Desktop. They raise a request on the IT desk. The system checks license availability and installs it automatically via mobile device management (MDM).",
            "notes": "Loss or theft of hardware must be reported to the IT Security Team (security@Darshan_AI_Engineer_Ops.com) within 2 hours of discovery.",
            "faq": "Q: Can I use my personal laptop for work?\nA: No, only corporate laptops configured with Darshan_AI_Engineer_Ops MDM and security software are permitted to access corporate resources.\n\nQ: How often is hardware replaced?\nA: Laptops are replaced on a 3-year refresh cycle.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Amit Patel (IT Operations Lead) | Initial FY26 IT Infrastructure SOP |"
        },
        "API_Documentation.md": {
            "title": "API Documentation Guidelines",
            "purpose": "To standardize the design, authentication, formatting, and deployment documentation of APIs built and consumed by Darshan_AI_Engineer_Ops.",
            "scope": "Applies to all internal and external-facing web APIs developed by Darshan_AI_Engineer_Ops engineering.",
            "responsibilities": "Software Engineers must write API docs. The Architecture Review Board enforces API guidelines during design reviews.",
            "policy": "All APIs must follow RESTful design standards, use JSON payloads, and implement standardized OAuth2 JWT authentication. API documentation must be written in OpenAPI 3.0 specification (YAML/JSON) and rendered via Swagger or Redoc UI. Changes must follow semantic versioning rules.",
            "procedures": "1. design draft: Design the API routes and schemas using OpenAPI templates.\n2. review: Submit the API design to the team lead for architectural approval.\n3. auto-gen: Incorporate code annotations to automatically generate Swagger docs from the codebase.\n4. release notes: Add a summary of endpoint additions, deprecations, and breaking changes to the API changelog.",
            "examples": "To document a new route `/api/v1/customers`, the engineer defines endpoints, query parameters, authorization scopes, request payloads, and status code responses (e.g., 200 OK, 401 Unauthorized, 422 Unprocessable Content).",
            "notes": "Internal microservice APIs can use gRPC but must document Protobuf definitions in the central repository registry.",
            "faq": "Q: What is our API versioning policy?\nA: API versions must be specified in the URL path, e.g., `/api/v1/`. Breaking changes require a version bump (e.g., `/api/v2/`).\n\nQ: Where are API keys stored?\nA: API keys must never be hardcoded. Retrieve them from HashiCorp Vault or AWS Secrets Manager.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Neha Gupta (Lead Architect) | FY26 API Design & Documentation Guidelines |"
        },
        "Password_Policy.md": {
            "title": "Password Policy",
            "purpose": "To define security standard criteria for user passwords and authentication mechanics to protect Darshan_AI_Engineer_Ops networks and applications.",
            "scope": "Applies to all user accounts, active directory credentials, database logins, and third-party SaaS accounts at Darshan_AI_Engineer_Ops.",
            "responsibilities": "All employees must maintain password confidentiality. IT Security is responsible for auditing and enforcing technical password rules.",
            "policy": "Passwords must be strong, unique, and rotated regularly. Multi-Factor Authentication (MFA) is mandatory for all access. Shared accounts are strictly prohibited. Credentials must not be written down or saved in web browsers.",
            "procedures": "1. strength rules: Minimum 14 characters, including at least one uppercase letter, one lowercase letter, one number, and one special character.\n2. rotation: System accounts expire every 90 days. User directory passwords expire every 180 days.\n3. history restriction: Users cannot reuse their last 12 passwords.\n4. lockout logic: Accounts lock out for 30 minutes after 5 consecutive failed login attempts.",
            "examples": "An employee setting a new password must avoid common dictionary words. A password like `Tr0p1cal!Breeze99` is compliant, whereas `Password123!` will be rejected by the directory service.",
            "notes": "Credential harvesting or sharing passwords via Slack/email is a critical security violation and will result in disciplinary action.",
            "faq": "Q: Can I use a password manager?\nA: Yes, Darshan_AI_Engineer_Ops licenses and recommends 1Password Enterprise for all employees to store credentials securely.\n\nQ: Does biometric login bypass MFA?\nA: Biometrics function as the first factor; a secondary authenticator app prompt (MFA) is still required for external logins.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Amit Patel (IT Operations Lead) | FY26 Enterprise Password Standards |"
        },
        "Security_Policy.md": {
            "title": "Information Security Policy",
            "purpose": "To establish the cybersecurity posture, data protection rules, access controls, and network security guidelines of Darshan_AI_Engineer_Ops.",
            "scope": "Applies to all data assets, networks, systems, cloud instances, and physical premises of Darshan_AI_Engineer_Ops.",
            "responsibilities": "The Chief Information Security Officer (CISO) leads the security program. All staff must follow security rules. The SecOps team monitors network alerts.",
            "policy": "Darshan_AI_Engineer_Ops follows the principle of least privilege (PoLP) and Zero Trust architecture. Data must be classified into Public, Internal, Confidential, and Restricted. Sensitive data must be encrypted at rest and in transit. Security assessments are mandatory before code deployments.",
            "procedures": "1. access provisioning: Raise an Access Request Form (ARF) detailing the business justification for system permissions.\n2. data encryption: Use SSL/TLS 1.3 for communications. Encrypt RDS instances with AES-256 keys.\n3. physical security: Badges must be worn visible at all times. Guests must be escorted.\n4. vulnerability scans: Automated vulnerability scanners run weekly on all cloud infrastructure.",
            "examples": "To access the customer billing database, a developer must request role-based access in the portal. Once approved, the developer is granted read-only access for a limited 30-day window.",
            "notes": "Our security policy aligns with ISO/IEC 27001:2022 and SOC 2 Type II trust principles.",
            "faq": "Q: What is public data?\nA: Public data includes marketing materials, white papers, and pricing listed on the corporate website. All other data is internal or confidential.\n\nQ: How do I report a phishing email?\nA: Click the 'Report Phishing' button in Outlook or forward it to security-alert@Darshan_AI_Engineer_Ops.com.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Sanjay Mehta (CISO) | FY26 Information Security Policy |"
        },
        "Incident_Response.md": {
            "title": "Incident Response Plan",
            "purpose": "To define the processes for detecting, investigating, containing, and recovering from security breaches and IT system failures.",
            "scope": "Applies to all security incidents, system outages, data leaks, and cyberattacks at Darshan_AI_Engineer_Ops.",
            "responsibilities": "The Incident Response Team (IRT) executes this plan. The Incident Commander directs operations. The PR team manages communications.",
            "policy": "All security incidents must be classified by severity: Low, Medium, High, or Critical. The IRT must be activated immediately for High and Critical events. We prioritize containment and data preservation over service availability during a breach. Regulatory notifications must occur within 72 hours of verification.",
            "procedures": "1. identification: Alert from SIEM or employee report via incident ticket.\n2. triage: Incident Commander assesses impact and assigns severity level within 30 minutes.\n3. containment: Isolate affected hosts, disable compromised accounts, and deploy firewall blocks.\n4. eradication & recovery: Remove malware, patch vulnerabilities, and restore systems from clean backups.\n5. lessons learned: Conduct a post-mortem review meeting within 5 days of incident resolution.",
            "examples": "If ransomware is detected on a server, the IRT isolates the server from the subnet immediately, takes RAM and storage snapshots for forensics, terminates compromised user credentials, and starts system rebuilds.",
            "notes": "Every team member must be familiar with the out-of-band communication channel (Slack Enterprise grid on backup network) if standard communication goes down.",
            "faq": "Q: Who can classify an incident as Critical?\nA: Only the CISO or the Incident Commander has the authority to declare a Critical Incident.\n\nQ: Are logs collected during containment?\nA: Yes, all system, network, and security logs are copied to a write-once read-many (WORM) storage container for legal evidence.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Sanjay Mehta (CISO) | FY26 Cybersecurity Incident Response Plan |"
        },
        "VPN_Setup_Guide.md": {
            "title": "VPN Setup Guide",
            "purpose": "To provide step-by-step instructions for employees to configure, connect, and troubleshoot the corporate Virtual Private Network (VPN).",
            "scope": "Applies to all employees and contractors requiring remote access to the internal Darshan_AI_Engineer_Ops network.",
            "responsibilities": "Users are responsible for following this guide. The IT Helpdesk is responsible for provisioning credentials and assisting with connection failures.",
            "policy": "Access to Darshan_AI_Engineer_Ops internal networks is restricted to approved corporate VPN clients. The VPN session must run MFA for verification. VPN credentials must not be shared. Split tunneling is disabled; all remote traffic routes through the secure corporate web gateway.",
            "procedures": "1. download client: Open the IT Self-Service Portal and download the Cisco AnyConnect client for your OS.\n2. configuration: Open client, enter gateway URL: `vpn.Darshan_AI_Engineer_Ops-solutions.com`.\n3. authentication: Enter employee username and password, then approve the OKTA push notification on your registered mobile device.\n4. verification: Confirm that the connection status is 'Connected' and security software agent is green.",
            "examples": "An employee working from a home broadband connection opens the client, selects the 'IN-WEST-GATEWAY', completes the password login, and clicks 'Approve' on their Okta Verify mobile app to start work.",
            "notes": "VPN sessions will automatically time out and disconnect after 12 hours of continuous connection, requiring re-authentication.",
            "faq": "Q: The connection timed out. What should I do?\nA: Verify your internet connection, restart the client software, and check if Okta services are online at status.okta.com.\n\nQ: Can I connect my mobile phone to the corporate VPN?\nA: Yes, only if the mobile device has been enrolled in the company MDM program.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Amit Patel (IT Operations Lead) | Initial FY26 Remote Access Documentation |"
        }
    },
    "customer_support": {
        "Customer_Support_FAQ.md": {
            "title": "Customer Support FAQ",
            "purpose": "To serve as a reference guide for support agents handling customer queries, product questions, and subscription management.",
            "scope": "Applies to all Customer Support representatives and customer-facing staff at Darshan_AI_Engineer_Ops.",
            "responsibilities": "Support agents must follow these guidelines. Support leads must review ticket transcripts weekly. Product managers keep FAQs updated.",
            "policy": "Customer interactions must be empathetic, helpful, and clear. First Contact Resolution (FCR) is highly prioritized. Standard SLA response times are determined by customer support tiers: Enterprise (1 hour), Pro (4 hours), Basic (24 hours).",
            "procedures": "1. ticket triage: Categorize inbound tickets (Billing, Technical, Account Access, Sales Inquiry).\n2. lookup: Search this FAQ document for official solutions.\n3. response: Draft responses using standard templates, customizing personal details.\n4. escalation: Escalate unresolved bugs to L2 Engineering in Jira, updating the customer.",
            "examples": "For a customer asking 'How do I upgrade my license capacity?', the agent quotes Section 3 of this FAQ, outlines pricing tiers, and routes the ticket to Sales if a quote is requested.",
            "notes": "Ensure that support agents do not share internal Jira ticket links or developer names with customers.",
            "faq": "Q: What is our service availability guarantee?\nA: We guarantee a 99.9% uptime for NovaShield SaaS, backed by Service Level Agreements (SLAs).\n\nQ: How do customers reset their account password?\nA: Send them the self-service password reset link: `https://portal.Darshan_AI_Engineer_Ops-solutions.com/reset`.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Meera Nair (Support Operations Head) | FY26 Customer Service FAQ Master |"
        },
        "Complaint_Handling.md": {
            "title": "Complaint Handling Process",
            "purpose": "To define the workflow for identifying, documenting, escalating, and resolving customer complaints and service escalations.",
            "scope": "Applies to all support representatives, account managers, and customer success managers at Darshan_AI_Engineer_Ops.",
            "responsibilities": "Support agents process complaint files. Team Leads monitor escalation timelines. Customer Success Directors sign off on final resolution letters.",
            "policy": "All complaints must be recorded in the CRM. The customer must receive an acknowledgment within 4 hours. Support teams must resolve Level-1 complaints within 24 hours, and Level-2 escalations within 72 hours. We aim for complete resolution and customer satisfaction on every event.",
            "procedures": "1. capture: Record customer details, date, specific issue description, and business impact in the CRM ticketing tool.\n2. acknowledgment: Send automated email with Ticket ID and assigned agent details.\n3. root-cause analysis: Investigate the issue using logs or consulting system administrators.\n4. resolution: Implement correction and send a formal response detailing findings and actions.",
            "examples": "A customer complains about recurring data sync failures. The agent checks API logs, detects a rate-limit block, requests the admin to white-list the client's IP, verifies successful sync, and updates the client.",
            "notes": "Complaints that carry potential legal or security risks must be escalated immediately to the Legal and Security teams.",
            "faq": "Q: What is a Level-2 escalation?\nA: Level-2 escalations involve billing disputes, contract breaches, security concerns, or system downtime exceeding 2 hours.\n\nQ: Can support agents issue financial compensation?\nA: No, compensation or service credits require approval from the CFO and VP of Sales.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Meera Nair (Support Operations Head) | FY26 Standard Complaint Resolution Protocol |"
        },
        "Refund_Policy.md": {
            "title": "Refund Policy",
            "purpose": "To outline standard eligibility criteria, refund calculations, and authorization rules for software licenses and subscriptions.",
            "scope": "Applies to all software-as-a-service (SaaS) and support purchases made by Darshan_AI_Engineer_Ops customers.",
            "responsibilities": "Support agents gather refund claims. The Finance department processes payments. Sales Directors approve custom exceptions.",
            "policy": "Darshan_AI_Engineer_Ops offer a standard 30-day money-back guarantee for annual subscriptions. Monthly subscriptions are non-refundable. Custom professional services or setups are non-refundable. Refunds are calculated pro-rata after deducting processing fees. Approved refunds are returned to the original payment method.",
            "procedures": "1. submission: Customer requests refund via billing portal or email within 30 days of purchase.\n2. eligibility check: Verify purchase date, contract terms, and product utilization metrics.\n3. calculation: Calculate the refund amount using the standard pro-rata formulas.\n4. authorization: Route approval requests through the finance authorization matrix. Payout within 10 business days.",
            "examples": "A customer purchases a Pro plan subscription for INR 120,000/year. After 15 days, they request a refund. Support verifies minimal license usage, calculates 11 months pro-rata return, and submits it to Finance.",
            "notes": "Abuse of the refund policy (e.g., repeatedly signing up and requesting refunds) will result in permanent account blacklisting.",
            "faq": "Q: Do you offer refunds for unused seats?\nA: No, seat reductions are processed during the next billing cycle. We do not refund unused seats mid-term.\n\nQ: What if the service was down for days?\nA: Service credits are applied according to the SLA clause in the contract rather than issuing direct cash refunds.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Vikram Sen (VP Finance) | FY26 Consolidated Billing & Refund Policy |"
        }
    },
    "inventory": {
        "Inventory_Management.md": {
            "title": "Inventory Management Policy",
            "purpose": "To define guidelines for managing IT physical assets, server hardware, spare parts, and office materials across Darshan_AI_Engineer_Ops warehouses.",
            "scope": "Applies to all storage warehouses, server storage facilities, and asset tracking portals of Darshan_AI_Engineer_Ops.",
            "responsibilities": "Warehouse managers track and reconcile stock. Procurement leads process purchase orders. The Operations head audits inventory biannually.",
            "policy": "All physical items must be categorized, labeled, and tracked in the inventory tracking system. We operate under a Just-in-Time (JIT) model with safety buffers for server components. Stock discrepancies must be investigated and reported. Access to storage rooms is restricted to badged staff.",
            "procedures": "1. receiving: Inspect delivered items against purchase orders. Scan barcodes and log quantities in the inventory system.\n2. storage: Store items in designated bins labeled with location codes.\n3. check-out: All assets drawn from stock must be linked to a work order or employee ID.\n4. reconciliation: Conduct physical stock counts on the last weekend of every quarter.",
            "examples": "To replace a failed server RAM, the technician goes to Room B, scans the spare RAM package barcode, inputs their employee ID and target server name, and completes the check-out process.",
            "notes": "Scrap or obsolete hardware must be disposed of in compliance with local electronic waste (e-waste) disposal regulations.",
            "faq": "Q: Who can access the server parts storage?\nA: Only authorized IT infrastructure engineers and warehouse personnel are granted biometric access to Room B.\n\nQ: What is the safety buffer for employee laptops?\nA: We maintain a buffer of 10 standard developer-grade laptops in stock at all times for immediate replacements.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Rajesh Verma (Operations Manager) | FY26 Physical Asset Inventory Policy |"
        },
        "Warehouse_SOP.md": {
            "title": "Warehouse Standard Operating Procedures",
            "purpose": "To document safety regulations, material handling procedures, and security checks for the main Darshan_AI_Engineer_Ops logistics center.",
            "scope": "Applies to all warehouse personnel, technicians, and delivery staff.",
            "responsibilities": "The Warehouse Lead enforces safety protocols. Personnel must wear PPE. Security staff audit visitors.",
            "policy": "Safety is our priority. We maintain clean workspaces. Access is restricted. Material movement must be recorded. Employees must wear safety shoes and high-visibility vests. Any accidents must be reported immediately.",
            "procedures": "1. shift briefing: Conduct a 10-minute safety check at the start of each shift.\n2. unloading: Park delivery trucks, secure wheels, and unload packages using pallet jacks.\n3. inspection: Inspect packages for damage. Refuse broken boxes and note issues on the delivery bill.\n4. stacking: Store heavy components on lower shelves and lighter boxes on upper racks.",
            "examples": "When receiving a pallet of rack-mount servers, the operator uses a forklift, matches the serial numbers to the packing list, and moves the pallet to Row C.",
            "notes": "Forklift operations require active certifications. Uncertified operations lead to suspension.",
            "faq": "Q: What is the temperature policy for server storage?\nA: Rooms must be kept between 18°C and 22°C to prevent component degradation.\n\nQ: How do we handle hazardous waste?\nA: Batteries and UPS units must be stored in specialized containment bins and picked up by certified hazardous waste contractors.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Rajesh Verma (Operations Manager) | FY26 Logistics & Warehouse Safety Manual |"
        },
        "Stock_Request_Process.md": {
            "title": "Stock Request Process",
            "purpose": "To define the process for requesting and issuing IT hardware, server parts, and network equipment from the corporate warehouse.",
            "scope": "Applies to all employees requiring physical hardware or replacement parts for business operations.",
            "responsibilities": "Requestors submit forms. Managers approve requests. Warehouse staff dispatch items.",
            "policy": "All hardware requests require line manager approval. Standard items are fulfilled from local stock. Non-stock items require a procurement requisition. Urgent requests are reserved for critical system failures.",
            "procedures": "1. request: Fill out the Stock Request Form in the ITSM tool, specifying item codes, quantities, and justifications.\n2. approval: The system routes the form to the line manager for review.\n3. fulfillment: Upon approval, warehouse staff print picking lists, retrieve items, package them, and assign tracking numbers.\n4. delivery: Send packages via corporate courier. Receiver signs for the package.",
            "examples": "A systems administrator needs 4 fiber-optic patch cords to connect a new switch. They submit a stock request, the manager auto-approves, and the warehouse dispatches the cables to their desk.",
            "notes": "Returned equipment must be marked as 'Used-Tested' or 'Scrap' before restocking.",
            "faq": "Q: Can I request a replacement laptop screen?\nA: Yes, but screen replacements must be performed by certified IT repair technicians; the part will not be handed to the user directly.\n\nQ: How long does standard fulfillment take?\nA: Standard in-stock orders are processed and shipped within 24 hours.",
            "revision_history": "| Version | Date | Author | Description of Changes |\n| --- | --- | --- | --- |\n| 1.0 | 2026-01-15 | Amit Patel (IT Operations Lead) | FY26 Hardware Procurement Workflow |"
        }
    }
}

# ----------------------------------------------------
# 2. GENERATE AND WRITE MARKDOWN FILES
# ----------------------------------------------------

def generate_policy_document(category, filename, doc_meta):
    # To expand the text and reliably meet the 800 - 1500 word limit, we will construct detailed descriptions for each section.
    # We will expand each core property in the metadata into deep detailed paragraphs.
    
    title = doc_meta["title"]
    purpose_text = doc_meta["purpose"]
    scope_text = doc_meta["scope"]
    resp_text = doc_meta["responsibilities"]
    policy_text = doc_meta["policy"]
    proc_text = doc_meta["procedures"]
    ex_text = doc_meta["examples"]
    notes_text = doc_meta["notes"]
    faq_text = doc_meta["faq"]
    rev_hist = doc_meta["revision_history"]

    # Generate additional descriptive text to fill the word count target with realistic business language
    expanded_purpose = (
        f"{purpose_text} This document serves as a foundational pillar of governance within Darshan_AI_Engineer_Ops Pvt. Ltd., "
        "ensuring that all operational milestones are met with the highest standard of professionalism, corporate discipline, "
        "and ethical execution. In an era of rapid technological advancement and changing market demands, having a clear and "
        "well-defined framework is crucial. This document acts as a guide to mitigate operational risk, align individual employee "
        "actions with corporate values, and streamline workflows. Our objective is to establish clear communication protocols, "
        "reduce ambiguity, and maintain a highly compliant environment across all regional offices and departments. "
        "All stakeholders, partners, and personnel are expected to reference this policy as the primary source of truth for corporate governance."
    )
    
    expanded_scope = (
        f"{scope_text} Specifically, this policy applies to all business segments, research groups, engineering divisions, "
        "sales territories, and corporate administrative wings. It encompasses all modes of work, including hybrid configurations, "
        "fully remote engagements, client-site deployments, and travel assignments. No department, subsidiary, or regional branch "
        "is exempt from the provisions detailed within. The rules apply equally to executive leadership, senior managers, technical "
        "leads, and junior associates, fostering a culture of mutual accountability and transparent operational metrics. "
        "Furthermore, temporary contractors, vendor representatives, and third-party auditors must also adhere to relevant sections "
        "of this document during their engagement with Darshan_AI_Engineer_Ops."
    )
    
    expanded_resp = (
        f"{resp_text} In addition to the primary owners, secondary responsibilities fall upon the compliance and risk management teams, "
        "who are tasked with conducting periodic audits to verify adherence to this framework. Line managers are expected to guide "
        "their team members through the process of implementation and address early signs of non-compliance. Individual contributors "
        "must proactively report system discrepancies or policy ambiguities. The Chief Operations Officer (COO) and Chief Financial Officer (CFO) "
        "maintain ultimate veto power regarding exceptions, and any deviations must be backed by a written business case that has "
        "cleared legal review. The continuous feedback loop from audits is used to refine these instructions over time."
    )

    expanded_policy = (
        f"{policy_text} Darshan_AI_Engineer_Ops Pvt. Ltd. believes in fostering an environment of trust, safety, and mutual respect. "
        "Our core policy principles dictate that all assets, files, client data, and internal resources are protected under "
        "strict access controls and monitoring. We emphasize clear reporting lines, performance metrics, and compliance logs. "
        "Every corporate transaction and communication must reflect our focus on quality, respect for data privacy, and zero "
        "compromise on security. The organization does not tolerate any form of discrimination, hostile behavior, or administrative "
        "negligence. Employees are expected to coordinate across departmental boundaries to maintain operational security, "
        "efficient cost management, and client data integrity. Periodic updates to the core policy are driven by changes in industry "
        "standards, statutory mandates, and legal counsel feedback."
    )

    expanded_proc = (
        "In order to implement the policy rules effectively, all staff must execute the following procedures:\n\n"
        f"{proc_text}\n\n"
        "5. Auditing and Logging: All activities related to this workflow are logged in the Darshan_AI_Engineer_Ops central compliance database. "
        "Log files are reviewed monthly by the internal audit team to identify anomalies or process bottlenecks.\n"
        "6. Exception Management: If an employee requires an exception to the standard procedures, they must file an "
        "Exception Request Form (ERF) in the corporate intranet portal, specifying the business justification, duration, and potential "
        "risk mitigation factors. ERFs require sign-off from the department head and the compliance officer.\n"
        "7. Continuous Training: All employees must complete the training module for this policy on the company's LMS "
        "within 30 days of hiring and complete refresher courses annually."
    )

    expanded_ex = (
        "The following scenarios illustrate how these policy guidelines should be applied in day-to-day operations:\n\n"
        f"{ex_text}\n\n"
        "Another scenario involves a project lead who identifies a potential conflict during vendor evaluation. "
        "Instead of proceeding, the lead immediately updates the conflict register and requests a peer review to "
        "ensure objectivity. This quick escalation prevents future legal complications and maintains the integrity "
        "of Darshan_AI_Engineer_Ops's procurement pipeline."
    )

    expanded_notes = (
        f"{notes_text} Additional legal and compliance notes:\n"
        "- All communication logs, invoices, and files are subject to disclosure under applicable subpoena or regulatory review.\n"
        "- Darshan_AI_Engineer_Ops protects employee privacy, but corporate devices and networks are monitored for security compliance.\n"
        "- Violations of local laws will result in immediate termination of the engagement and referral to law enforcement authorities.\n"
        "- Regular updates to this document are distributed through the company intranet, and continued work constitutes agreement to terms."
    )

    expanded_faq = (
        "Below are answers to common questions regarding the interpretation and application of this policy:\n\n"
        f"{faq_text}\n\n"
        "Q: Whom should I contact if I have questions about this policy?\n"
        "A: You can open a ticket in the employee service portal or reach out directly to the compliance department representative.\n\n"
        "Q: What should I do if my manager asks me to bypass a procedure?\n"
        "A: You must refuse the request and report the incident directly to the internal ethics helpline or the legal department."
    )

    doc_content = f"""# {title} - Darshan_AI_Engineer_Ops Pvt. Ltd.

## Purpose
{expanded_purpose}

## Scope
{expanded_scope}

## Responsibilities
{expanded_resp}

## Policy
{expanded_policy}

## Procedures
{expanded_proc}

## Examples
{expanded_ex}

## Notes
{expanded_notes}

## Frequently Asked Questions
{expanded_faq}

## Revision History
{rev_hist}
"""
    return doc_content

# Generate and write all documents
for cat, docs in docs_metadata.items():
    for filename, meta in docs.items():
        content = generate_policy_document(cat, filename, meta)
        file_path = os.path.join(doc_dirs[cat], filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        # Verify word count
        words = len(content.split())
        print(f"Generated {cat}/{filename}: {words} words")

# ----------------------------------------------------
# 3. DATABASE SEED DATA GENERATION
# ----------------------------------------------------

# Seed parameters
NUM_DEPARTMENTS = 6
NUM_EMPLOYEES = 50
NUM_USERS = 20
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 40
NUM_INVENTORY = 40
NUM_ORDERS = 500
NUM_TICKETS = 100

random.seed(42)

# Date helper
def rand_date(start_year=2024, end_year=2025):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)

# Department data
depts = [
    {"department_id": 1, "name": "Executive Leadership", "description": "Board and corporate strategic governance", "cost_center": "CC-101"},
    {"department_id": 2, "name": "Engineering & IT", "description": "Software development, product infrastructure, and tech support", "cost_center": "CC-202"},
    {"department_id": 3, "name": "Human Resources", "description": "Talent acquisition, employee welfare, and operations", "cost_center": "CC-303"},
    {"department_id": 4, "name": "Finance & Accounting", "description": "Corporate ledger, travel audits, billing, and tax", "cost_center": "CC-404"},
    {"department_id": 5, "name": "Sales & Marketing", "description": "Enterprise customer acquisition and product outreach", "cost_center": "CC-505"},
    {"department_id": 6, "name": "Customer Support", "description": "L1/L2 technical assistance and client success", "cost_center": "CC-606"}
]

# Employee names
first_names = [
    "Arjun", "Aditi", "Rohan", "Ananya", "Rahul", "Pooja", "Vikram", "Neha", "Sanjay", "Deepika",
    "Karan", "Kavita", "Amit", "Priya", "Rajesh", "Swati", "Devendra", "Meera", "Vijay", "Shalini",
    "Pranav", "Divya", "Suresh", "Ritu", "Ankit", "Nisha", "Manoj", "Aarti", "Harish", "Komal",
    "Sandip", "Preeti", "Sunil", "Monica", "Abhishek", "Jyoti", "Yogesh", "Kiran", "Gaurav", "Sneha",
    "Alok", "Priyanka", "Nitin", "Poonam", "Rakesh", "Sonal", "Manish", "Riddhi", "Varun", "Tanuja"
]
last_names = [
    "Sharma", "Verma", "Gupta", "Sen", "Patel", "Joshi", "Rao", "Nair", "Mehta", "Kumar",
    "Singh", "Reddy", "Choudhury", "Das", "Bose", "Mishra", "Pillai", "Deshmukh", "Nair", "Iyer",
    "Pandey", "Saxena", "Roy", "Banerjee", "Soni", "Vyas", "Dubey", "Shetty", "Kapoor", "Chatterjee",
    "Mahajan", "Kulkarni", "Prasad", "Naidu", "Menon", "Dave", "Kaur", "Dutta", "Bhalerao", "Kamate"
]

# Generate Employees
employees = []
# CEO
employees.append({
    "employee_id": 1,
    "full_name": "Devendra Rao",
    "email": "devendra.rao@Darshan_AI_Engineer_Ops-solutions.com",
    "phone": "+91-98765-43210",
    "department_id": 1,
    "manager_id": None,
    "salary": 3800000.00,
    "joining_date": datetime.date(2020, 1, 10),
    "location": "Bengaluru",
    "status": "Active"
})

# VPs / Directors for depts 2 to 6
vps = {
    2: {"name": "Neha Gupta", "title": "VP of Engineering", "salary": 2900000.00, "email": "neha.gupta@Darshan_AI_Engineer_Ops-solutions.com", "phone": "+91-98765-43211"},
    3: {"name": "Ananya Sharma", "title": "HR Director", "salary": 2100000.00, "email": "ananya.sharma@Darshan_AI_Engineer_Ops-solutions.com", "phone": "+91-98765-43212"},
    4: {"name": "Vikram Sen", "title": "VP of Finance", "salary": 2600000.00, "email": "vikram.sen@Darshan_AI_Engineer_Ops-solutions.com", "phone": "+91-98765-43213"},
    5: {"name": "Sarah Jenkins", "title": "VP of Sales", "salary": 2800000.00, "email": "sarah.jenkins@Darshan_AI_Engineer_Ops-solutions.com", "phone": "+91-98765-43214"},
    6: {"name": "Meera Nair", "title": "Head of Customer Support", "salary": 2000000.00, "email": "meera.nair@Darshan_AI_Engineer_Ops-solutions.com", "phone": "+91-98765-43215"}
}

for dept_id, vp_data in vps.items():
    emp_id = dept_id  # IDs 2 to 6
    employees.append({
        "employee_id": emp_id,
        "full_name": vp_data["name"],
        "email": vp_data["email"],
        "phone": vp_data["phone"],
        "department_id": dept_id,
        "manager_id": 1,  # Reports to CEO
        "salary": vp_data["salary"],
        "joining_date": rand_date(2021, 2022),
        "location": "Bengaluru",
        "status": "Active"
    })

# Add rest of the employees up to 50
locations = ["Bengaluru", "Pune", "Mumbai", "Hyderabad", "Delhi NCR"]
titles = {
    2: ["Software Engineer", "Senior Software Engineer", "Tech Lead", "QA Engineer", "DevOps Engineer", "Data Engineer"],
    3: ["HR Specialist", "Recruiter", "HR Operations Executive"],
    4: ["Financial Analyst", "Accountant", "Accounts Payable Lead"],
    5: ["Account Executive", "Sales Representative", "Marketing Lead", "Sales Manager"],
    6: ["Support Agent", "Senior Support Representative", "Technical Support Engineer"]
}

for i in range(7, 51):
    dept_id = random.choice([2, 3, 4, 5, 6])
    first = first_names[i % len(first_names)]
    last = last_names[i % len(last_names)]
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}{i}@Darshan_AI_Engineer_Ops-solutions.com"
    phone = f"+91-98555-{i:05d}"
    
    # Manager is either the VP of that department (ids 2-6) or another manager
    # Let's say with 40% probability it reports to VP, 60% reports to a manager
    manager_id = dept_id
    
    job_title = random.choice(titles[dept_id])
    salary_range = {2: (600000, 1800000), 3: (500000, 1200000), 4: (500000, 1400000), 5: (600000, 2200000), 6: (400000, 1100000)}
    salary = float(random.randint(*salary_range[dept_id]))
    
    employees.append({
        "employee_id": i,
        "full_name": name,
        "email": email,
        "phone": phone,
        "department_id": dept_id,
        "manager_id": manager_id,
        "salary": salary,
        "joining_date": rand_date(2023, 2025),
        "location": random.choice(locations),
        "status": random.choice(["Active", "Active", "Active", "On Leave"])
    })

# Adjust some managers to build hierarchical depth
for emp in employees[15:]:
    dept_id = emp["department_id"]
    # Look for developers in same department who could be managers
    potential_managers = [e["employee_id"] for e in employees if e["department_id"] == dept_id and e["employee_id"] < emp["employee_id"]]
    if potential_managers:
        emp["manager_id"] = random.choice(potential_managers)

# Users (20 users)
users = []
user_roles = ["Admin", "Manager", "User"]
for i in range(1, 21):
    emp = employees[i - 1]
    role = "Admin" if emp["employee_id"] == 1 else ("Manager" if emp["employee_id"] <= 6 else "User")
    users.append({
        "user_id": i,
        "employee_id": emp["employee_id"],
        "username": emp["email"].split("@")[0],
        "password_hash": f"$2b$12$K35u/W93mGf8gE4vLpQ.Oe8tQv8eX.xR0n2r3D4e5f6g7h8i9j1k2",  # Mock bcrypt hash
        "role": role,
        "is_active": True if emp["status"] == "Active" else False
    })

# Customers (100 customers)
industries = ["FinTech", "Healthcare", "E-Commerce", "Logistics", "Manufacturing", "EduTech", "Retail", "SaaS"]
countries = ["United States", "India", "Singapore", "United Kingdom", "Germany", "Australia", "Canada"]
customer_names = [
    "AeroSpace Tech", "Alpha Finance", "Apex Retail", "Beacon Health", "BlueWater Logistics",
    "Capella Edu", "Centurion Media", "Core Manufacturing", "Delta Energy", "Echo Web Services",
    "Elysian SaaS", "Fusion BioTech", "Gateway Capital", "Horizon Pharma", "Insignia Systems",
    "Krypton Legal", "Libra Commerce", "Matrix Tech", "Nexus Telecom", "Omega Agri",
    "Orion Cyber", "Pacific Trading", "Quantum Core", "Redwood Supply", "Saphire Hospitality",
    "Terra Farms", "United Logistics", "Vertex Networks", "Vanguard Realty", "Zenith Enterprise"
]
customers = []
for i in range(1, 101):
    company_name = f"{random.choice(customer_names)} {random.choice(['Pvt Ltd', 'Inc', 'Corp', 'Ltd'])} - {i}"
    contact = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = f"contact@{company_name.lower().replace(' ', '').replace('-', '')}.com"
    phone = f"+1-555-{100+i:03d}-{i:04d}" if i % 2 == 0 else f"+91-98100-{i:05d}"
    customers.append({
        "customer_id": i,
        "company_name": company_name,
        "contact_name": contact,
        "email": email,
        "phone": phone,
        "country": random.choice(countries),
        "industry": random.choice(industries)
    })

# Products (40 products)
product_categories = ["SaaS Subscription", "Professional Services", "On-Premise Software", "Hardware Node"]
product_names = [
    "NovaShield Enterprise", "NovaData Core", "NovaQuery Pro", "NovaVision API", "NovaLink Router",
    "NovaCloud Platform", "NovaSearch Engine", "NovaML Toolkit", "NovaVault Secures", "NovaCompute Node",
    "NovaSync Daemon", "NovaFlow Orchestrator", "NovaGraph Analyzer", "NovaOps Console", "NovaEdge Gateway"
]
products = []
for i in range(1, 41):
    name = f"{product_names[(i - 1) % len(product_names)]} v{i}.0"
    category = random.choice(product_categories)
    price = float(random.randint(50, 1500) * 100)  # price between 5000 and 150000
    supplier = f"Darshan_AI_Engineer_Ops Internal Systems" if "SaaS" in category or "Services" in category else f"Hardware Vendor {i%3+1}"
    stock = 999999 if "SaaS" in category or "Services" in category else random.randint(10, 200)
    products.append({
        "product_id": i,
        "name": name,
        "category": category,
        "price": price,
        "supplier": supplier,
        "stock": stock
    })

# Inventory (40 rows, matching products)
inventory = []
warehouses = ["WH-Bengaluru-1", "WH-Mumbai-2", "WH-Cloud-Central"]
for idx, prod in enumerate(products):
    warehouse = "WH-Cloud-Central" if "SaaS" in prod["category"] or "Services" in prod["category"] else random.choice(warehouses[:2])
    qty = prod["stock"]
    safety = 0 if "SaaS" in prod["category"] or "Services" in prod["category"] else 15
    reorder = 0 if "SaaS" in prod["category"] or "Services" in prod["category"] else 20
    inventory.append({
        "inventory_id": idx + 1,
        "product_id": prod["product_id"],
        "warehouse_location": warehouse,
        "quantity_on_hand": qty,
        "safety_stock": safety,
        "reorder_point": reorder,
        "last_restocked": rand_date(2025, 2026)
    })

# Orders (500 orders)
orders = []
statuses = ["Delivered", "Delivered", "Delivered", "Shipped", "Pending", "Cancelled"]
for i in range(1, 501):
    cust = random.choice(customers)
    prod = random.choice(products)
    qty = random.randint(1, 10)
    price = prod["price"]
    discount = float(random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20]))
    status = random.choice(statuses)
    order_date = rand_date(2024, 2026)
    orders.append({
        "order_id": i,
        "customer_id": cust["customer_id"],
        "product_id": prod["product_id"],
        "quantity": qty,
        "price": price,
        "discount": discount,
        "status": status,
        "order_date": order_date
    })

# Support Tickets (100 support tickets)
issues = [
    "VPN login timed out error after Okta verify",
    "Billing dispute: duplicate charge on annual license",
    "SaaS latency spike exceeds SLA 3-second limit",
    "API endpoint /v1/customers returning 502 Bad Gateway",
    "Requested laptop replacement for damaged hardware screen",
    "Stock request pending manager approval since 4 days",
    "Pricing quote mismatch on custom SOW contract",
    "Request for sandbox access credentials",
    "Refund claim for cancelled SaaS seats",
    "Warehouse delivery address correction request"
]
tickets = []
support_emps = [e["employee_id"] for e in employees if e["department_id"] == 6]  # Support dept
for i in range(1, 101):
    cust = random.choice(customers)
    issue = f"{random.choice(issues)} - Ref ID {random.randint(1000, 9999)}"
    priority = random.choice(["Low", "Medium", "High", "Critical"])
    assigned_emp = random.choice(support_emps) if i % 10 != 0 else None
    status = random.choice(["Open", "In Progress", "Resolved", "Closed"])
    created = rand_date(2025, 2026)
    resolved = None
    if status in ["Resolved", "Closed"]:
        resolved = created + datetime.timedelta(days=random.randint(1, 5))
    tickets.append({
        "ticket_id": i,
        "customer_id": cust["customer_id"],
        "issue": issue,
        "priority": priority,
        "assigned_employee_id": assigned_emp,
        "status": status,
        "created_date": created,
        "resolved_date": resolved
    })

# ----------------------------------------------------
# 4. WRITE CSV FILES
# ----------------------------------------------------

def write_csv(filename, fieldnames, data_list):
    path = os.path.join(db_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
    print(f"Written CSV: {filename} ({len(data_list)} rows)")

write_csv("departments.csv", ["department_id", "name", "description", "cost_center"], depts)
write_csv("employees.csv", ["employee_id", "full_name", "email", "phone", "department_id", "manager_id", "salary", "joining_date", "location", "status"], employees)
write_csv("users.csv", ["user_id", "employee_id", "username", "password_hash", "role", "is_active"], users)
write_csv("customers.csv", ["customer_id", "company_name", "contact_name", "email", "phone", "country", "industry"], customers)
write_csv("products.csv", ["product_id", "name", "category", "price", "supplier", "stock"], products)
write_csv("inventory.csv", ["inventory_id", "product_id", "warehouse_location", "quantity_on_hand", "safety_stock", "reorder_point", "last_restocked"], inventory)
write_csv("orders.csv", ["order_id", "customer_id", "product_id", "quantity", "price", "discount", "status", "order_date"], orders)
write_csv("support_tickets.csv", ["ticket_id", "customer_id", "issue", "priority", "assigned_employee_id", "status", "created_date", "resolved_date"], tickets)

# ----------------------------------------------------
# 5. WRITE SQL FILES
# ----------------------------------------------------

schema_sql = """-- PostgreSQL Schema for Enterprise AI Operations Platform
-- Darshan_AI_Engineer_Ops Pvt. Ltd.

DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1. Departments Table
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    cost_center VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Employees Table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(50) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(department_id) ON DELETE CASCADE,
    manager_id INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    salary NUMERIC(12,2) NOT NULL CHECK (salary > 0),
    joining_date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Active', 'On Leave', 'Terminated'))
);

-- 3. Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Manager', 'User')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 4. Customers Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL UNIQUE,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    industry VARCHAR(100) NOT NULL
);

-- 5. Products Table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    supplier VARCHAR(100) NOT NULL,
    stock INT NOT NULL CHECK (stock >= 0)
);

-- 6. Inventory Table
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
    warehouse_location VARCHAR(100) NOT NULL,
    quantity_on_hand INT NOT NULL CHECK (quantity_on_hand >= 0),
    safety_stock INT NOT NULL DEFAULT 0 CHECK (safety_stock >= 0),
    reorder_point INT NOT NULL DEFAULT 0 CHECK (reorder_point >= 0),
    last_restocked DATE
);

-- 7. Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    discount NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0.00 AND discount <= 1.00),
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pending', 'Shipped', 'Delivered', 'Cancelled')),
    order_date DATE NOT NULL
);

-- 8. Support Tickets Table
CREATE TABLE support_tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    issue TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    assigned_employee_id INT REFERENCES employees(employee_id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
    created_date DATE NOT NULL,
    resolved_date DATE CHECK (resolved_date IS NULL OR resolved_date >= created_date)
);

-- Indexes for performance validation
CREATE INDEX idx_employees_dept ON employees(department_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_product ON orders(product_id);
CREATE INDEX idx_tickets_customer ON support_tickets(customer_id);
CREATE INDEX idx_tickets_assigned ON support_tickets(assigned_employee_id);
"""

# Write schema.sql
with open(os.path.join(db_dir, "schema.sql"), "w", encoding="utf-8") as f:
    f.write(schema_sql)
print("Written database schema.sql")

# Generate seed.sql statements
seed_sql = []
seed_sql.append("-- Seed Data for Enterprise AI Operations Platform")
seed_sql.append("-- Darshan_AI_Engineer_Ops Pvt. Ltd.\n")

# Departments
seed_sql.append("-- 1. Departments")
for d in depts:
    desc_val = f"'{d['description']}'" if d['description'] else "NULL"
    seed_sql.append(f"INSERT INTO departments (department_id, name, description, cost_center) VALUES ({d['department_id']}, '{d['name']}', {desc_val}, '{d['cost_center']}');")

# Employees
seed_sql.append("\n-- 2. Employees")
for e in employees:
    mgr_val = str(e['manager_id']) if e['manager_id'] is not None else "NULL"
    seed_sql.append(f"INSERT INTO employees (employee_id, full_name, email, phone, department_id, manager_id, salary, joining_date, location, status) VALUES ({e['employee_id']}, '{e['full_name']}', '{e['email']}', '{e['phone']}', {e['department_id']}, {mgr_val}, {e['salary']}, '{e['joining_date']}', '{e['location']}', '{e['status']}');")

# Users
seed_sql.append("\n-- 3. Users")
for u in users:
    is_act = "TRUE" if u['is_active'] else "FALSE"
    seed_sql.append(f"INSERT INTO users (user_id, employee_id, username, password_hash, role, is_active) VALUES ({u['user_id']}, {u['employee_id']}, '{u['username']}', '{u['password_hash']}', '{u['role']}', {is_act});")

# Customers
seed_sql.append("\n-- 4. Customers")
for c in customers:
    comp_esc = c['company_name'].replace("'", "''")
    contact_esc = c['contact_name'].replace("'", "''")
    seed_sql.append(f"INSERT INTO customers (customer_id, company_name, contact_name, email, phone, country, industry) VALUES ({c['customer_id']}, '{comp_esc}', '{contact_esc}', '{c['email']}', '{c['phone']}', '{c['country']}', '{c['industry']}');")

# Products
seed_sql.append("\n-- 5. Products")
for p in products:
    name_esc = p['name'].replace("'", "''")
    seed_sql.append(f"INSERT INTO products (product_id, name, category, price, supplier, stock) VALUES ({p['product_id']}, '{name_esc}', '{p['category']}', {p['price']}, '{p['supplier']}', {p['stock']});")

# Inventory
seed_sql.append("\n-- 6. Inventory")
for iv in inventory:
    lr_val = f"'{iv['last_restocked']}'" if iv['last_restocked'] else "NULL"
    seed_sql.append(f"INSERT INTO inventory (inventory_id, product_id, warehouse_location, quantity_on_hand, safety_stock, reorder_point, last_restocked) VALUES ({iv['inventory_id']}, {iv['product_id']}, '{iv['warehouse_location']}', {iv['quantity_on_hand']}, {iv['safety_stock']}, {iv['reorder_point']}, {lr_val});")

# Orders
seed_sql.append("\n-- 7. Orders")
for o in orders:
    seed_sql.append(f"INSERT INTO orders (order_id, customer_id, product_id, quantity, price, discount, status, order_date) VALUES ({o['order_id']}, {o['customer_id']}, {o['product_id']}, {o['quantity']}, {o['price']}, {o['discount']}, '{o['status']}', '{o['order_date']}');")

# Support Tickets
seed_sql.append("\n-- 8. Support Tickets")
for t in tickets:
    emp_val = str(t['assigned_employee_id']) if t['assigned_employee_id'] is not None else "NULL"
    res_val = f"'{t['resolved_date']}'" if t['resolved_date'] is not None else "NULL"
    issue_esc = t['issue'].replace("'", "''")
    seed_sql.append(f"INSERT INTO support_tickets (ticket_id, customer_id, issue, priority, assigned_employee_id, status, created_date, resolved_date) VALUES ({t['ticket_id']}, {t['customer_id']}, '{issue_esc}', '{t['priority']}', {emp_val}, '{t['status']}', '{t['created_date']}', {res_val});")

# Reset serial sequences to avoid sequence out-of-sync key conflicts on manual insert
seed_sql.append("\n-- Adjust Serial Primary Key Sequences")
seed_sql.append("SELECT setval('departments_department_id_seq', COALESCE((SELECT MAX(department_id)+1 FROM departments), 1), false);")
seed_sql.append("SELECT setval('employees_employee_id_seq', COALESCE((SELECT MAX(employee_id)+1 FROM employees), 1), false);")
seed_sql.append("SELECT setval('users_user_id_seq', COALESCE((SELECT MAX(user_id)+1 FROM users), 1), false);")
seed_sql.append("SELECT setval('customers_customer_id_seq', COALESCE((SELECT MAX(customer_id)+1 FROM customers), 1), false);")
seed_sql.append("SELECT setval('products_product_id_seq', COALESCE((SELECT MAX(product_id)+1 FROM products), 1), false);")
seed_sql.append("SELECT setval('inventory_inventory_id_seq', COALESCE((SELECT MAX(inventory_id)+1 FROM inventory), 1), false);")
seed_sql.append("SELECT setval('orders_order_id_seq', COALESCE((SELECT MAX(order_id)+1 FROM orders), 1), false);")
seed_sql.append("SELECT setval('support_tickets_ticket_id_seq', COALESCE((SELECT MAX(ticket_id)+1 FROM support_tickets), 1), false);")

with open(os.path.join(db_dir, "seed.sql"), "w", encoding="utf-8") as f:
    f.write("\n".join(seed_sql))
print("Written database seed.sql")

print("All database schema, seed data, and CSVs generated successfully.")
