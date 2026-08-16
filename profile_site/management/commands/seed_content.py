"""Load the firm profile content into the database.

Run once after migrating:   python manage.py seed_content
Safe to re-run - it updates records in place rather than duplicating them.
Everything it creates is editable afterwards in the admin.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from profile_site.models import (
    Client, FirmValue, IndustrySegment, KeyFigure, Office, PresenceCity, Service, TeamMember,
)

KEY_FIGURES = [
    ("2019", "Year the firm was incorporated"),
    ("20+", "Professionals across the practice"),
    ("9", "Cities, direct and through associates"),
    ("18+", "Years of combined partner experience"),
]

VALUES = [
    ("Quality", "Work that stands up to review, every time.", "quality"),
    ("Reliability", "Commitments held, deadlines met.", "reliability"),
    ("Responsiveness", "Answers within agreed timelines, no surprises.", "response"),
    ("Governance", "Regulatory and compliance frameworks taken seriously.", "governance"),
    ("Our people", "The right team on the right engagement.", "people"),
    ("Partnership", "We are here to help clients grow, not to audit and leave.", "partnership"),
]

SERVICES = [
    {
        "title": "Assurance & Audit",
        "icon": "audit",
        "is_featured": True,
        "summary": "Statutory audit, book finalisation and specialist audit support for listed companies, large corporates and multinationals.",
        "intro": (
            "Audit is where our partners built their careers. Between them they have led statutory "
            "audit engagements for listed entities, large Indian corporates and subsidiaries of "
            "multinational groups, and that experience shapes how we run every assurance engagement.\n\n"
            "We plan around the risks that actually matter to your business rather than working "
            "through a generic checklist, and we raise issues as we find them so nothing lands as a "
            "surprise at the closing meeting."
        ),
        "deliverables": (
            "Statutory audit under the Companies Act, 2013\n"
            "Book finalisation and year-end closing support\n"
            "Limited review for listed entities\n"
            "Group reporting packs for overseas parents\n"
            "Specialist and agreed-upon procedures\n"
            "Certification and attestation work"
        ),
    },
    {
        "title": "Taxation",
        "icon": "tax",
        "is_featured": True,
        "summary": "Direct tax, international taxation and GST compliance, from planning and advisory through to filing and representation.",
        "intro": (
            "Indian tax law changes constantly, and the cost of getting it wrong has risen with better "
            "data matching at the department's end. We cover direct tax, international taxation and "
            "GST under one roof so that positions taken in one area do not create exposure in another.\n\n"
            "Our work runs from routine compliance through to advisory on cross-border structures and "
            "representation where a position needs defending."
        ),
        "deliverables": (
            "Corporate income tax computation and return filing\n"
            "International taxation and treaty advisory\n"
            "Transfer pricing documentation and study\n"
            "GST registration, periodic returns and annual reconciliation\n"
            "Withholding tax advisory and TDS compliance\n"
            "Representation before assessing and appellate authorities"
        ),
    },
    {
        "title": "Risk Advisory, SOX & Internal Audit",
        "icon": "risk",
        "is_featured": True,
        "summary": "Risk-based internal audit, SOX compliance and IFC frameworks, built around how your processes actually run.",
        "intro": (
            "Our partners head the risk, process and technology practice and have run SOX compliance "
            "and governance workshops for government bodies, public sector undertakings and private "
            "companies.\n\n"
            "We do not believe in finding errors to list. We look for the root cause of a control "
            "failure and fix it at that point, working through discussions, case studies and practical "
            "workshops with the people who own the process."
        ),
        "deliverables": (
            "Risk-based internal audit planning and execution\n"
            "SOX 404 scoping, walkthroughs and testing\n"
            "IFC and IFCR documentation and testing\n"
            "Control gap identification and remediation support\n"
            "Standard operating procedure drafting\n"
            "Management and audit committee reporting"
        ),
    },
    {
        "title": "Governance, Risk & Compliance",
        "icon": "governance",
        "is_featured": True,
        "summary": "Corporate compliance calendars, regulatory framework reviews and governance advisory for boards and management.",
        "intro": (
            "Compliance obligations sit across company law, tax, labour and sector regulation, and they "
            "rarely fail all at once - they slip quietly, one filing at a time.\n\n"
            "We build a compliance calendar around your entity structure, track it, and flag what is "
            "coming before it becomes a penalty. Where a regulator has changed its position, we tell "
            "you what it means for your business rather than forwarding the circular."
        ),
        "deliverables": (
            "Corporate and secretarial compliance calendar\n"
            "RBI and FEMA reporting support\n"
            "Regulatory framework and readiness reviews\n"
            "Policy, process and SOP drafting\n"
            "Board and committee governance reviews\n"
            "Compliance health checks"
        ),
    },
    {
        "title": "Corporate Finance, M&A & Valuations",
        "icon": "finance",
        "is_featured": True,
        "summary": "Valuations, due diligence and transaction support for fundraises, acquisitions and internal restructuring.",
        "intro": (
            "Transactions turn on the quality of the numbers behind them. We work on both sides of a "
            "deal - preparing a business so it can be diligenced cleanly, or diligencing a target so "
            "our client knows what they are buying.\n\n"
            "Valuation work is documented to a standard that holds up with regulators, investors and "
            "auditors alike."
        ),
        "deliverables": (
            "Business and share valuation\n"
            "Financial and tax due diligence\n"
            "Deal structuring support\n"
            "Fundraise documentation and projections\n"
            "Purchase price allocation\n"
            "Post-transaction integration support"
        ),
    },
    {
        "title": "Outsourcing",
        "icon": "outsourcing",
        "is_featured": True,
        "summary": "Accounting, finance, payroll and reporting run as a managed service, so your team can stay on the business.",
        "intro": (
            "Not every company needs a full in-house finance function, and many that have one still "
            "want the routine work off their desk. We run accounting, payroll and reporting as a "
            "managed service with defined turnaround times.\n\n"
            "You get a monthly close you can rely on, and a single point of contact who knows your "
            "books rather than a rotating queue."
        ),
        "deliverables": (
            "Bookkeeping and general ledger maintenance\n"
            "Payroll processing and statutory deductions\n"
            "Accounts payable and receivable management\n"
            "Monthly MIS and management reporting\n"
            "Virtual CFO support\n"
            "Process documentation and handover"
        ),
    },
    {
        "title": "Technology Solutions & Data Analytics",
        "icon": "analytics",
        "summary": "Audit analytics on full data populations, finance automation and reporting built on what your systems already hold.",
        "intro": (
            "Sampling made sense when data had to be pulled by hand. It rarely does now. We run "
            "analytics across full populations to find the exceptions that a sample would miss, and "
            "automate the reconciliations that eat a finance team's month-end.\n\n"
            "Our partners bring functional knowledge of SAP, Tally and the GST and income tax "
            "toolchain, so the work sits on your actual systems rather than a parallel spreadsheet."
        ),
        "deliverables": (
            "Audit analytics across full data populations\n"
            "Finance process automation\n"
            "Reconciliation automation\n"
            "Dashboard and MIS build-out\n"
            "ERP data quality reviews\n"
            "Cost optimisation analysis"
        ),
    },
    {
        "title": "Digital & IT Advisory",
        "icon": "digital",
        "summary": "IT general controls, ERP implementation controls and technology risk reviews for finance environments.",
        "intro": (
            "Financial controls increasingly live inside systems rather than alongside them. If access "
            "rights, change management and segregation of duties are weak in the ERP, the control "
            "environment is weak regardless of what the policy document says.\n\n"
            "We review the technology layer that your financial reporting depends on, and work with "
            "IT and finance together rather than treating them as separate audits."
        ),
        "deliverables": (
            "IT general controls (ITGC) review\n"
            "ERP implementation and post-go-live controls\n"
            "System access and segregation of duties review\n"
            "Data governance advisory\n"
            "Technology risk assessment\n"
            "Digital transformation advisory for finance"
        ),
    },
]

SEGMENTS = [
    "Automobile", "Auto Ancillary", "Banking", "Chemicals & Fertilisers", "Consumer Durable",
    "Electricity & Transmission", "Infrastructure & Real Estate", "Insurance", "Manufacturing",
    "Power & Utility", "Information Technology", "Hotel Industry", "Cruise Industry", "Telecom Sector",
]

CITIES = ["Delhi", "Noida", "Gurugram", "Ghaziabad", "Chandigarh", "Amritsar", "Mumbai", "Pune",
          "Hyderabad", "Vijayawada"]

MAJOR_CLIENTS = [
    ("American Express", "NYSE, NASDAQ listed"),
    ("Life Insurance Corporation of India (LIC)", "BSE, NSE listed"),
    ("ITC Limited", "BSE, NSE listed"),
    ("IndiaMART InterMESH Limited", "BSE, NSE listed"),
    ("India Insurance", "BSE, NSE listed"),
    ("Central Warehousing Corporation (CWC)", "Government undertaking"),
    ("CarDekho.com", ""),
    ("Park Hotel", ""),
    ("Waterways Leisure Private Limited", ""),
    ("A G Industry Private Limited", ""),
    ("RTDS", "US based company"),
]

OTHER_CLIENTS = [
    "Amir Chand Jagdish Kumar (E) Ltd", "William Grant & Sons Private Limited",
    "Nearbuy India Private Limited", "hCentive Technology India Private Limited",
    "LifeCare - Corner Store Technology Private Limited", "MyBox Technologies Private Limited",
    "Core Logistics Private Limited", "Telenor (India) Communications Private Limited",
    "Starex Drycleaners Private Limited", "Remsons Industries Limited",
    "Maharaja Whiteline Industries Private Limited", "The Statesman Limited",
    "VIVO Healthcare Limited", "SMILE Multimedia Private Limited",
    "Tolexo Online Private Limited", "GMAX Auto Limited",
    "Insta Pizza - Insta Restaurants Private Limited",
]

OFFICES = [
    ("Noida", "14th Floor, 14112, Gaur City Mall\nNoida Extension\nNoida, Uttar Pradesh 201301", True),
    ("Ghaziabad", "1213, Sector 2\nWave City, NH 24\nGhaziabad, Uttar Pradesh", False),
    ("Delhi", "F-214, Gurunanak Nagar\nLaxmi Nagar, New Delhi", False),
]

COMMON_SECTORS = """Aviation
E-commerce & marketplace
FMCG
Technology & telecommunications
Diversified manufacturing
Hospitality & healthcare
Chemicals & fertilizers
Newspaper, electronic & print media
Automobile & auto ancillary
Government & not for profit"""

TEAM = [
    {
        "name": "CA Anuj Kumar",
        "designation": "Partner",
        "focus": "Statutory Audit, Direct Taxation & International Taxation",
        "experience_years": 10,
        "location": "Noida",
        "is_lead": True,
        "order": 1,
        "email": "caanujsarav@gmail.com",
        "phone": "+91 99909 41988",
        "static_photo": "site/img/team/anuj-kumar.jpg",
        "qualification": "Bachelor of Commerce · Chartered Accountant, The Institute of Chartered Accountants of India (ICAI)",
        "bio": (
            "With more than ten years of experience, Anuj leads the Risk, Process and Technology "
            "Services practice at KARS & Co. His domain expertise spans statutory audit, book "
            "finalisation, direct and international taxation, and business and process advisory "
            "with a focus on cost optimisation.\n\n"
            "He runs classroom trainings and workshops on SOX compliance and governance for "
            "government bodies, public sector undertakings and private companies. Prior to KARS & Co "
            "he worked with a top firm and with several multinational consulting firms.\n\n"
            "His engagement history covers listed companies, large Indian corporates and "
            "multinational corporations across a wide spread of industry segments."
        ),
        "key_skills": "Risk advisory\nInternal audit\nProcess consulting\nAutomation\nIFC & IFCR\nProcess outsourcing",
        "sectors": COMMON_SECTORS,
    },
    {
        "name": "CA Amit Kumar",
        "designation": "Partner",
        "focus": "Internal Audit, Risk, Advisory & Process Services",
        "experience_years": 7,
        "location": "Noida",
        "order": 2,
        "static_photo": "site/img/team/amit-kumar.jpg",
        "qualification": "Bachelor of Commerce · Chartered Accountant, The Institute of Chartered Accountants of India (ICAI)",
        "bio": (
            "With more than seven years of corporate experience, Amit heads Risk, Process and "
            "Technology Services as a partner at KARS & Co. He brings domain expertise in risk "
            "advisory and internal audit, alongside business and process advisory with cost "
            "optimisation.\n\n"
            "He delivers classroom trainings and workshops on SOX compliance and governance across "
            "government, public sector and private companies. Prior to KARS & Co he worked with a "
            "top firm and various multinational consulting firms."
        ),
        "key_skills": "Risk advisory\nInternal audit\nProcess consulting\nAutomation\nIFC & IFCR\nProcess outsourcing",
        "sectors": COMMON_SECTORS,
    },
    {
        "name": "Rohit Singh",
        "designation": "Practice Lead",
        "focus": "Corporate Compliance, GST & KPI Audit",
        "experience_years": 7,
        "location": "Noida",
        "order": 3,
        "static_photo": "site/img/team/rohit-singh.jpg",
        "qualification": "Bachelor of Commerce · Chartered Accountant, The Institute of Chartered Accountants of India (ICAI)",
        "bio": (
            "With more than seven years of experience across industries, Rohit covers corporate "
            "compliance, GST and KPI audit. Before joining KARS & Co he worked with major "
            "large-scale firms and several multinationals.\n\n"
            "He has hands-on functional knowledge of ERPs including SAP and Tally across workflow "
            "and accounting, and works fluently with GST and income tax tooling. His engagement "
            "history covers listed companies, large Indian corporates and multinationals."
        ),
        "key_skills": "Risk advisory\nInternal audit\nBusiness & process advisory\nIFC & SOX\nCompliance & governance",
        "sectors": (
            "E-commerce & marketplace internet companies\nTechnology & telecommunications\n"
            "Hospitality & healthcare\nSteel industry\nAutomobile & auto ancillary\n"
            "Banking & NBFCs\nGovernment & not for profit"
        ),
    },
]


class Command(BaseCommand):
    help = "Load the KARS & Co profile content into the database."

    @transaction.atomic
    def handle(self, *args, **options):
        for i, (value, label) in enumerate(KEY_FIGURES, start=1):
            KeyFigure.objects.update_or_create(value=value, defaults={"label": label, "order": i})

        for i, (name, desc, icon) in enumerate(VALUES, start=1):
            FirmValue.objects.update_or_create(
                name=name, defaults={"description": desc, "icon": icon, "order": i}
            )

        for i, data in enumerate(SERVICES, start=1):
            payload = dict(data)
            payload["order"] = i
            payload.setdefault("is_featured", False)
            Service.objects.update_or_create(
                slug=slugify(payload["title"])[:140], defaults=payload
            )

        for i, name in enumerate(SEGMENTS, start=1):
            IndustrySegment.objects.update_or_create(name=name, defaults={"order": i})

        for i, name in enumerate(CITIES, start=1):
            PresenceCity.objects.update_or_create(name=name, defaults={"order": i})

        for i, (name, listing) in enumerate(MAJOR_CLIENTS, start=1):
            Client.objects.update_or_create(
                name=name, defaults={"listing": listing, "tier": Client.Tier.MAJOR, "order": i}
            )

        for i, name in enumerate(OTHER_CLIENTS, start=1):
            Client.objects.update_or_create(name=name, defaults={"tier": Client.Tier.OTHER, "order": i})

        for i, (city, address, primary) in enumerate(OFFICES, start=1):
            Office.objects.update_or_create(
                city=city, defaults={"address": address, "is_primary": primary, "order": i}
            )

        for person in TEAM:
            payload = dict(person)
            name = payload.pop("name")
            payload["slug"] = slugify(name)[:140]
            TeamMember.objects.update_or_create(name=name, defaults=payload)

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {KeyFigure.objects.count()} figures, {FirmValue.objects.count()} values, "
            f"{Service.objects.count()} services, {IndustrySegment.objects.count()} segments, "
            f"{PresenceCity.objects.count()} cities, {Client.objects.count()} clients, "
            f"{TeamMember.objects.count()} team members and {Office.objects.count()} offices."
        ))
