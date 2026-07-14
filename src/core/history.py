import os
import pandas as pd
from datetime import datetime

HISTORY_FILE = "data/prompt_history.csv"


def initialize_history():
    """
    Create history CSV if it doesn't exist.
    """
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=[
            "timestamp",
            "original_prompt",
            "optimized_prompt",
            "task_type",
            "tone",
            "detail_level",
            "favorite"
        ])
        df.to_csv(HISTORY_FILE, index=False)


def save_prompt(original, optimized, task, tone, detail):
    """
    Save prompt to CSV.
    """
    initialize_history()

    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_prompt": original,
        "optimized_prompt": optimized,
        "task_type": task,
        "tone": tone,
        "detail_level": detail,
        "favorite": False
    }

    df = pd.read_csv(HISTORY_FILE)

    df.loc[len(df)] = new_row

    df.to_csv(HISTORY_FILE, index=False)


def load_history():
    """
    Load prompt history.
    """
    initialize_history()
    df = pd.read_csv(HISTORY_FILE)
    if "favorite" not in df.columns:
        df["favorite"] = False
        df.to_csv(HISTORY_FILE, index=False)
    return df


def clear_history():
    """
    Delete all history.
    """
    initialize_history()

    df = pd.DataFrame(columns=[
        "timestamp",
        "original_prompt",
        "optimized_prompt",
        "task_type",
        "tone",
        "detail_level",
        "favorite"
    ])

    df.to_csv(HISTORY_FILE, index=False)

def toggle_favorite(timestamp):
    """
    Toggle the favorite status of a prompt history item.
    """
    df = load_history()
    if timestamp in df["timestamp"].values:
        current_status = df.loc[df["timestamp"] == timestamp, "favorite"].values[0]
        df.loc[df["timestamp"] == timestamp, "favorite"] = not current_status
        df.to_csv(HISTORY_FILE, index=False)