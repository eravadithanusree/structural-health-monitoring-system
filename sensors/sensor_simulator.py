"""
Simulates a live sensor feed for a structure.

Standalone mode (python sensors/sensor_simulator.py):
    Writes directly to the database in a loop, useful for populating
    history without needing the Flask server running.

Occasionally injects a "damage event" so the dashboard/history has
realistic Healthy -> Damaged transitions to visualize.
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from database import database as db
from ml import predict as predictor


class SensorSimulator:
    def __init__(self, structure_id="default"):
        self.structure_id = structure_id
        self.damage_mode = False
        self.damage_ticks_remaining = 0

    def _maybe_toggle_damage(self):
        if self.damage_mode:
            self.damage_ticks_remaining -= 1
            if self.damage_ticks_remaining <= 0:
                self.damage_mode = False
        else:
            if random.random() < 0.08:  # ~8% chance to start a damage event
                self.damage_mode = True
                self.damage_ticks_remaining = random.randint(4, 10)

    def read(self):
        """Generate one simulated (vibration, strain, temperature) reading."""
        self._maybe_toggle_damage()
        if self.damage_mode:
            vibration = max(0, random.gauss(5.3, 1.2))
            strain = max(0, random.gauss(215, 40))
            temperature = random.gauss(39, 8)
        else:
            vibration = max(0, random.gauss(1.8, 0.6))
            strain = max(0, random.gauss(90, 25))
            temperature = random.gauss(27, 5)

        return round(vibration, 2), round(strain, 1), round(temperature, 1)

    def tick_and_store(self):
        vibration, strain, temperature = self.read()
        status, confidence = predictor.predict(vibration, strain, temperature)
        db.insert_reading(vibration, strain, temperature, status, confidence, self.structure_id)
        return {
            "vibration": vibration,
            "strain": strain,
            "temperature": temperature,
            "status": status,
            "confidence": confidence,
        }


def run_forever():
    db.init_db()
    sim = SensorSimulator()
    print("Sensor simulator running. Press Ctrl+C to stop.")
    try:
        while True:
            reading = sim.tick_and_store()
            print(reading)
            time.sleep(Config.SIMULATOR_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    run_forever()
