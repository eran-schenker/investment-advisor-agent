from services.pipeline import run_pipeline
from services.market_data import get_unprocessed_anomalies_from_csv
from services.orchestrator import merge_anomalies, process_anomalies

if __name__ == "__main__":
    # Step 1: fetch live prices and detect new anomalies this run
    _, flagged = run_pipeline()

    # Step 2: also pick up older CSV anomaly_flag=True rows that never got a thesis
    backlog = get_unprocessed_anomalies_from_csv()
    to_process = merge_anomalies(flagged, backlog)

    print(f"Live anomalies this run: {len(flagged)}")
    print(f"CSV backlog (flagged but no thesis file yet): {len(backlog)}")
    print(to_process)

    # Step 3: sequentially fetch news + generate thesis JSON for each anomaly
    if to_process:
        written = process_anomalies(to_process)
        print(f"Theses written: {len(written)}")
        if written:
            print(f"Thesis folder: {written[0].rsplit('/', 1)[0]}")
    else:
        print("Nothing to process.")
