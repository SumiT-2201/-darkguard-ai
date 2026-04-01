import pandas as pd
import os

def get_dataset():
    """
    Loads the dark pattern dataset from the root CSV file.
    Includes samples for urgency, confirmshaming, hidden costs, 
    forced action, social proof, auto-renewal, and safe UI.
    """
    # Path to the CSV in the root directory
    # Structure: backend/app/ml/dataset.py -> ml -> app -> backend -> root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    csv_path = os.path.join(base_dir, 'dark_patterns_dataset.csv')
    
    if os.path.exists(csv_path):
        print(f"Loading dataset from {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        # Debug: Print where we looked
        print(f"⚠️ Dataset CSV not found at {csv_path}")
        # Secondary fallback: try the backend directory itself
        alt_path = os.path.join(os.path.dirname(base_dir), 'dark_patterns_dataset.csv')
        if os.path.exists(alt_path):
             print(f"Loading from alternative path: {alt_path}")
             df = pd.read_csv(alt_path)
        else:
            print("Falling back to legacy hardcoded data.")
            data = [
                ("Only 2 items left in stock!", "urgency"),
                ("Hurry, deal ends in 05:00 minutes.", "urgency"),
                ("No thanks, I prefer to pay full price.", "confirmshaming"),
                ("Add to cart", "safe")
            ]
            df = pd.DataFrame(data, columns=["text", "label"])
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df
