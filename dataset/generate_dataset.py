"""
Generates a synthetic-but-realistic structural sensor dataset for training.

Real deployments would replace this with actual logged sensor history.
Physical reasoning behind the ranges:
- Vibration (mm/s): healthy structures show low-amplitude ambient vibration;
  damage (cracking, loosened joints) raises amplitude and variance.
- Strain (microstrain, µɛ): elevated/sustained strain indicates load
  redistribution around a defect.
- Temperature (°C): mostly environmental, but included since thermal
  expansion affects strain readings and extreme heat is a contributing
  stressor for some materials.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

N_HEALTHY = 900
N_DAMAGED = 600

# Healthy structures: low vibration, moderate strain, normal temperature
healthy = pd.DataFrame({
    "vibration": np.clip(np.random.normal(1.8, 0.7, N_HEALTHY), 0, None),
    "strain": np.clip(np.random.normal(90, 30, N_HEALTHY), 0, None),
    "temperature": np.random.normal(27, 6, N_HEALTHY),
})
healthy["status"] = "Healthy"

# Damaged structures: higher vibration amplitude, elevated strain,
# sometimes higher operating temperature under stress
damaged = pd.DataFrame({
    "vibration": np.clip(np.random.normal(5.2, 1.4, N_DAMAGED), 0, None),
    "strain": np.clip(np.random.normal(210, 45, N_DAMAGED), 0, None),
    "temperature": np.random.normal(38, 10, N_DAMAGED),
})
damaged["status"] = "Damaged"

df = pd.concat([healthy, damaged], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

df["vibration"] = df["vibration"].round(2)
df["strain"] = df["strain"].round(1)
df["temperature"] = df["temperature"].round(1)

out_path = os.path.join(os.path.dirname(__file__), "structural_data.csv")
df.to_csv(out_path, index=False)
print(f"Wrote {len(df)} rows to {out_path}")
print(df["status"].value_counts())
