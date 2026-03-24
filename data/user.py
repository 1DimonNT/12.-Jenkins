from dataclasses import dataclass
from enum import Enum


class Gender(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'


class Hobby(Enum):
    SPORTS = 'Sports'
    READING = 'Reading'
    MUSIC = 'Music'


@dataclass
class User:
    first_name: str
    last_name: str
    email: str
    gender: Gender
    mobile: str
    birth_day: int
    birth_month: str
    birth_year: int
    subjects: list
    hobbies: list
    picture: str
    address: str
    state: str
    city: str

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
