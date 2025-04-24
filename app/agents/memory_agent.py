import os
import json
from pathlib import Path

MEMORY_DIR = "data/profiles"


class MemoryAgent:
    def __init__(self, base_dir=MEMORY_DIR):
        self.base_dir = base_dir
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)

    def _profile_path(self, customer_id: str) -> str:
        return os.path.join(self.base_dir, f"{customer_id}.json")

    def load_profile(self, customer_id: str) -> dict:
        path = self._profile_path(customer_id)
        if not os.path.exists(path):
            return self._create_empty_profile(customer_id)

        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[MemoryAgent] ❌ Error reading profile: {e}")
            return self._create_empty_profile(customer_id)

    def _create_empty_profile(self, customer_id: str) -> dict:
        empty = {
            "customer_id": customer_id,
            "history": [],
            "last_extracted_info": {},
            "known_preferences": {}
        }
        self.save_profile(customer_id, empty)
        return empty

    def save_profile(self, customer_id: str, profile_data: dict):
        try:
            with open(self._profile_path(customer_id), "w") as f:
                json.dump(profile_data, f, indent=2)
            print(f"[MemoryAgent] ✅ Saved profile for customer: {customer_id}")
        except Exception as e:
            print(f"[MemoryAgent] ❌ Failed to save profile: {e}")

    def update_extracted_info(self, customer_id: str, new_info: dict):
        profile = self.load_profile(customer_id)
        profile["last_extracted_info"] = new_info
        self.save_profile(customer_id, profile)

    def append_to_history(self, customer_id: str, message: str):
        profile = self.load_profile(customer_id)
        profile["history"].append(message)
        if len(profile["history"]) > 20:  # limit long-term log
            profile["history"] = profile["history"][-20:]
        self.save_profile(customer_id, profile)

    def get_last_extracted_info(self, customer_id: str) -> dict:
        profile = self.load_profile(customer_id)
        return profile.get("last_extracted_info", {})


# ✅ Singleton to import across app
memory_agent = MemoryAgent()
