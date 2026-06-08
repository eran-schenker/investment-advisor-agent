from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

from services.market_data import get_market_data_and_detect_anomalies

# US/Eastern timezone (important for market hours)
tz = pytz.timezone("US/Eastern")


def job():
    now = datetime.now(tz)

    # 🧠 Business day check (Mon–Fri)
    if now.weekday() >= 5:
        print("Weekend — skipping run")
        return

    # 🧠 Market hours check (9:30–16:00 ET)
    if not (9 <= now.hour < 16):
        print("Outside market hours — skipping run")
        return

    print(f"Running anomaly job at {now}")
    results, flagged = get_market_data_and_detect_anomalies()

    print(f"Done. Flagged: {len(flagged)}")


scheduler = BlockingScheduler(timezone=tz)

# every hour
scheduler.add_job(job, "interval", hours=1)

if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()