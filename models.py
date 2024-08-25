from pydantic import BaseModel
from typing import List


class UserInformations(BaseModel):

    user_id: int
    phone_number: str
    balance: int
    referral: list
