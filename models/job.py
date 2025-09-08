from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    """
    Dataclass to represent a standardized job listing.
    """

    title: str
    company_name: str
    location: str
    url: str
    email: Optional[str] = None
    job_description: Optional[str] = None
