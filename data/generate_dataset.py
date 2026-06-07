import pandas as pd
import random
from datetime import datetime, timedelta

NUM_ROWS = 50000

channels = [
    "Google Ads",
    "Facebook",
    "Email",
    "Organic",
    "Direct"
]

campaigns = [
    "Summer Sale",
    "Retargeting",
    "Black Friday",
    "Brand Awareness",
    "New Customers"
]

devices = [
    "Mobile",
    "Desktop",
    "Tablet"
]

events = [
    "page_view",
    "product_view",
    "add_to_cart",
    "purchase"
]

rows = []

start_date = datetime(2025, 1, 1)

for i in range(NUM_ROWS):

    customer_id = random.randint(1000, 9999)

    date = start_date + timedelta(
        days=random.randint(0, 500)
    )

    channel = random.choice(channels)

    campaign = random.choice(campaigns)

    device = random.choice(devices)

    event = random.choices(
        events,
        weights=[40, 30, 20, 10]
    )[0]

    revenue = 0

    if event == "purchase":
        revenue = round(
            random.uniform(20, 500),
            2
        )

    rows.append(
        [
            customer_id,
            date,
            channel,
            campaign,
            device,
            event,
            revenue
        ]
    )

df = pd.DataFrame(
    rows,
    columns=[
        "customer_id",
        "event_date",
        "channel",
        "campaign",
        "device",
        "event_type",
        "revenue"
    ]
)

df.to_csv(
    "customer_journey.csv",
    index=False
)

print("Dataset created.")
print(df.head())
