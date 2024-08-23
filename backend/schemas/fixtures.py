from pydantic import BaseModel
from typing import List

class Stat(BaseModel):
    identifier: str
    a: List[dict]
    h: List[dict]

class Fixture(BaseModel):
    code: int
    event: int
    finished: bool
    finished_provisional: bool
    id: int
    kickoff_time: str
    minutes: int
    provisional_start_time: bool
    started: bool
    team_a: int
    team_a_score: int
    team_h: int
    team_h_score: int
    stats: List[Stat]
    team_h_difficulty: int
    team_a_difficulty: int
    pulse_id: int

