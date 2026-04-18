import random
from typing import Optional
from prompt_data import PROMPT_DATA

# Categories whose style keywords force a specific camera pool.
# "photographic" categories use real lens descriptions.
# "compositional" categories use angle/framing descriptions.
STYLE_FORCES_CAMERA_POOL = {
    # Any style containing these words must use the named category's camera pool
    "painting": "fantasy",
    "illustration": "fantasy",
    "concept art": "fantasy",
    "grimdark": "fantasy",
    "watercolor": "fantasy",
    "romanticism": "fantasy",
    "oil painting": "fantasy",
    "ukiyo-e": "mythology_legends",
    "woodblock": "mythology_legends",
}

# Same logic for lighting pool
STYLE_FORCES_LIGHTING_POOL = {
    "painting": "fantasy",
    "illustration": "fantasy",
    "concept art": "fantasy",
    "grimdark": "fantasy",
    "oil painting": "fantasy",
}


def _resolve_pool(style: str, rules: dict, default_category: str) -> str:
    """Return the category whose pool to use, based on style keywords."""
    style_lower = style.lower()
    for keyword, pool in rules.items():
        if keyword in style_lower:
            return pool
    return default_category


class PromptEngine:
    def __init__(self):
        self.history: list[str] = []
        self.blacklist: set[str] = set()
        self.max_history = 50

    def generate(self, category: str) -> Optional[str]:
        data = PROMPT_DATA.get(category)
        if not data:
            return None

        for _ in range(10):
            prompt = self._build(category, data)
            if prompt not in self.blacklist:
                self._add_to_history(prompt)
                return prompt

        return None  # All attempts blacklisted — extremely unlikely

    def _build(self, category: str, data: dict) -> str:
        subject = random.choice(data["subjects"])
        style = random.choice(data["styles"])
        mood = random.choice(data["moods"])
        setting = random.choice(data["settings"])
        detail = random.choice(data["details"])
        params = random.choice(data["parameters"])

        camera_type = data.get("camera_type", "photographic")

        # For compositional categories, always use own camera/lighting pool.
        # For photographic categories, check if the selected style overrides.
        if camera_type == "compositional":
            camera_pool = category
            lighting_pool = category
        else:
            camera_pool = _resolve_pool(style, STYLE_FORCES_CAMERA_POOL, category)
            lighting_pool = _resolve_pool(style, STYLE_FORCES_LIGHTING_POOL, category)

        camera = random.choice(PROMPT_DATA[camera_pool]["cameras"])
        lighting = random.choice(PROMPT_DATA[lighting_pool]["lighting"])

        return (
            f"{subject}, {style}, {setting}, "
            f"{camera}, {lighting}, "
            f"{mood} mood, {detail} "
            f"{params}"
        )

    def _add_to_history(self, prompt: str):
        self.history.insert(0, prompt)
        self.history = self.history[:self.max_history]

    def add_to_blacklist(self, prompt: str):
        self.blacklist.add(prompt)

    def remove_from_blacklist(self, prompt: str):
        self.blacklist.discard(prompt)

    def clear_history(self):
        self.history.clear()
