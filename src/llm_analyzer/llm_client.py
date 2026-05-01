import json
import os
import urllib.error
import urllib.request


class LLMClient:
    """
    Minimal OpenAI-compatible chat client using stdlib only.
    Configure with:
      IAAS_LLM_BASE_URL=https://api.openai.com/v1/chat/completions
      IAAS_LLM_API_KEY=...
      IAAS_LLM_MODEL=...
    """

    def __init__(self, base_url=None, api_key=None, model=None, timeout=120):
        self.base_url = base_url or os.environ.get("IAAS_LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
        self.api_key = api_key or os.environ.get("IAAS_LLM_API_KEY")
        self.model = model or os.environ.get("IAAS_LLM_MODEL", "gpt-4o-mini")
        self.timeout = timeout

    def complete_json(self, prompt):
        if not self.api_key:
            raise RuntimeError("IAAS_LLM_API_KEY no esta configurada. Use --mode stub o configure el proveedor.")

        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Responde solo JSON valido. No incluyas texto fuera del JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }
        request = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Fallo la llamada LLM: {exc}") from exc

        content = data["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"El LLM no devolvio JSON valido: {content[:500]}") from exc
