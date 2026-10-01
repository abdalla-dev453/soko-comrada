from app.models.user import User, UserType
from app.models.employer_profile import EmployerProfile, EmployerVerificationStatus
from app.models.student_profile import StudentProfile
from app.models.opportunity import (
    Opportunity,
    Gig,
    GigType,
    GigStatus,
    PriceType,
    OpportunityType,
    CompensationType,
    WorkArrangement,
)
from app.models.application import Application, ApplicationStatus
from app.models.review import Review
from app.models.payment import Payment, PaymentPurpose, PaymentStatus, PaymentMethod
from app.models.report import Report, ReportStatus
from app.models.verification_token import VerificationToken
from app.models.portfolio_image import PortfolioImage
from app.models.saved_opportunity import SavedOpportunity

# Alias for clarity in PRD context
OpportunityStatus = GigStatus

__all__ = [
    "User",
    "UserType",
    "EmployerProfile",
    "EmployerVerificationStatus",
    "StudentProfile",
    "Opportunity",
    "Gig",
    "GigType",
    "GigStatus",
    "OpportunityStatus",
    "PriceType",
    "OpportunityType",
    "CompensationType",
    "WorkArrangement",
    "Application",
    "ApplicationStatus",
    "Review",
    "Payment",
    "PaymentPurpose",
    "PaymentStatus",
    "PaymentMethod",
    "Report",
    "ReportStatus",
    "VerificationToken",
    "PortfolioImage",
    "SavedOpportunity",
]