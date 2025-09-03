from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Literal, Optional
from uuid import UUID, uuid4

# === For Goal Planning ===
class FinancialGoal(BaseModel):
    goal_id: UUID = Field(default_factory=uuid4)
    title: str
    target_date: date
    current_amount: float
    target_amount: float

class FinancialGoalUpdate(BaseModel):
    title: Optional[str] = None
    target_date: Optional[date] = None
    current_amount: Optional[float] = None
    target_amount: Optional[float] = None


# === For Subscription Analysis ===
class Subscription(BaseModel):
    name: str
    last_paid_date: date
    estimated_monthly_cost: float
    transaction_count: int
    status: Literal["active", "potentially_unused"]


class SubscriptionInfo(BaseModel):
    total_monthly_cost: float
    potential_savings: float
    subscriptions: List[Subscription]