"""LLM Routing Layer — wraps Google Gemini for text and vision calls."""

import json
import re
import time
import threading
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import requests
from core.config import GEMINI_MODEL


class LLMRouter:
    """Thin wrapper around Gemini that every agent uses."""

    def __init__(self, api_key: str, model_name: str | None = None):
        genai.configure(api_key=api_key)
        self._model_name = model_name or GEMINI_MODEL
        self._model = genai.GenerativeModel(self._model_name)
        self._lock = threading.Lock()
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_calls = 0
        print(f"[LLMRouter] Initialized with model: {self._model_name}")

    # ── token tracking ───────────────────────────────────────────────
    def _track_usage(self, response, label: str):
        """Extract and accumulate token usage from a Gemini response."""
        prompt_tokens = 0
        completion_tokens = 0
        try:
            meta = response.usage_metadata
            prompt_tokens = getattr(meta, "prompt_token_count", 0) or 0
            completion_tokens = getattr(meta, "candidates_token_count", 0) or 0
        except Exception:
            pass

        with self._lock:
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_calls += 1
            call_num = self.total_calls

        total = prompt_tokens + completion_tokens
        print(
            f"[LLMRouter] Call #{call_num} ({label})  "
            f"prompt={prompt_tokens}  completion={completion_tokens}  "
            f"total_tokens={total}"
        )

    def get_usage_summary(self) -> dict:
        """Return cumulative token usage stats."""
        with self._lock:
            return {
                "total_calls": self.total_calls,
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            }

    # ── public helpers ──────────────────────────────────────────────
    def analyze_text(self, prompt: str, label: str = "text") -> str:
        """Send a text-only prompt and return the raw response text."""
        start = time.time()
        print(f"[LLMRouter] >> Sending text request ({label})…")
        response = self._model.generate_content(prompt)
        elapsed = round(time.time() - start, 2)
        self._track_usage(response, label)
        print(f"[LLMRouter] << Response received ({label}) in {elapsed}s")
        return response.text

    def analyze_image(self, image_url: str, prompt: str, label: str = "vision") -> str:
        """Download an image, send it with a prompt to the vision model."""
        img = self._download_image(image_url)
        if img is None:
            print(f"[LLMRouter] !! Failed to download image: {image_url}")
            return '{"error": "Could not download image"}'
        start = time.time()
        print(f"[LLMRouter] >> Sending image+text request ({label})…")
        response = self._model.generate_content([prompt, img])
        elapsed = round(time.time() - start, 2)
        self._track_usage(response, label)
        print(f"[LLMRouter] << Response received ({label}) in {elapsed}s")
        return response.text

    def analyze_images_batch(self, image_urls: list[str], prompt: str, label: str = "vision-batch") -> str:
        """Send multiple images with a single prompt."""
        parts: list = [prompt]
        for url in image_urls:
            img = self._download_image(url)
            if img:
                parts.append(img)
                print(f"[LLMRouter]    ✓ Downloaded image: {url[:80]}")
            else:
                print(f"[LLMRouter]    ✗ Failed to download: {url[:80]}")
        if len(parts) == 1:
            print(f"[LLMRouter] !! No images could be downloaded for batch")
            return '{"error": "No images could be downloaded"}'
        start = time.time()
        print(f"[LLMRouter] >> Sending {len(parts)-1} image(s) + text request ({label})…")
        response = self._model.generate_content(parts)
        elapsed = round(time.time() - start, 2)
        self._track_usage(response, label)
        print(f"[LLMRouter] << Response received ({label}) in {elapsed}s")
        return response.text

    # ── JSON extraction ─────────────────────────────────────────────
    @staticmethod
    def parse_json(text: str) -> dict | None:
        """Extract a JSON object from an LLM response (handles markdown wrapping)."""
        # Direct parse
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass
        # Markdown code-fence
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Bare object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    # ── private ─────────────────────────────────────────────────────
    @staticmethod
    def _download_image(url: str) -> Image.Image | None:
        try:
            resp = requests.get(url, timeout=10, stream=True)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception:
            return None
