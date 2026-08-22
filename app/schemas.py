from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    city: str = Field(min_length=2, max_length=100)
    format: str = Field(pattern="^(online|offline)$")
    date: str
    deadline: str | None = None
    category: str = Field(pattern="^(robotics|startup|hackathon|gamedev|cybersecurity)$")
    description: str
    link: str


class EventCreate(EventBase):
    source: str = "api"


class EventRead(EventBase):
    id: int
    source: str
    model_config = ConfigDict(from_attributes=True)
