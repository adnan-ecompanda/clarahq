import random
from datetime import datetime, timedelta


def mock_eligibility_check(provider: str, member_id: str):
    statuses = ["active", "inactive", "pending"]
    plan_types = ["PPO", "HMO", "EPO", "POS"]

    return {
        "status": random.choice(statuses),
        "co_pay": random.choice([10, 20, 30, 40]),
        "deductible_remaining": random.randint(0, 1500),
        "out_of_pocket_max": random.choice([2000, 3000, 5000]),
        "effective_date": "2024-01-01",
        "expiration_date": "2024-12-31",
        "plan_type": random.choice(plan_types)
    }