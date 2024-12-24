import enum


# Перечисления стадий резюме
class StageEnum(enum.Enum):
    open = "open"
    reviewed = "reviewed"
    interview = "interview"
    passed_interview = "passed_interview"
    tech_interview = "tech_interview"
    passed_tech_interview = "passed_tech_interview"
    offer = "offer"


# Перечисления источников резюме
class ResumesSourceEnum(enum.Enum):
    LinkedIn = "LinkedIn"
    Email = "Email"
    JobBoard = "JobBoard"
    Referral = "Referral"


class UserRoleEnum(str, enum.Enum):
    hr = "HR"
    team_lead = "HR Team Lead"

    @classmethod
    def _missing_(cls, value):
        """Позволяет принимать нижний регистр."""
        value = value.upper().replace("_", " ")
        for member in cls:
            if member.value == value:
                return member
