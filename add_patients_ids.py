import pandas as pd

# Load EEG data
df = pd.read_csv("rewire_clean_eeg_sample.csv")

# Determine number of rows
num_rows = len(df)
n_patients = 10

# Repeat patient IDs exactly to match dataset length
patient_ids = [f"RW-{str(i+1).zfill(3)}" for i in range(n_patients)]
df["patient_id"] = (patient_ids * (num_rows // n_patients + 1))[:num_rows]

# Save back to file
df.to_csv("rewire_clean_eeg_sample.csv", index=False)
print(f"✅ Added patient_id column for {num_rows} rows.")
