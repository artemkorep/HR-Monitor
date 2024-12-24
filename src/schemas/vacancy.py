from pydantic import BaseModel


class VacancyCreate(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes = True
