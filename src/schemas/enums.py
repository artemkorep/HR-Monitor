from enum import Enum


class StageEnum(Enum):
    open = "open"
    reviewed = "reviewed"
    interview = "interview"
    passed_interview = "passed_interview"
    tech_interview = "tech_interview"
    passed_tech_interview = "passed_tech_interview"
    offer = "offer"


class ResumesSourceEnum(str, Enum):
    LinkedIn = "LinkedIn"
    Email = "Email"
    JobBoard = "JobBoard"
    Referral = "Referral"


class UserRoleEnum(str, Enum):
    hr = "HR"
    team_lead = "HR Team Lead"

    @classmethod
    def _missing_(cls, value):
        """Позволяет принимать нижний регистр."""
        value = value.upper().replace("_", " ")
        for member in cls:
            if member.value == value:
                return member
