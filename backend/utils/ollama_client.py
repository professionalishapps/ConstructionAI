import requests
import os

class OllamaClient:
    def __init__(self, base_url=None, default_model=None):
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.default_model = default_model or 'mistral:latest'

    def generate(self, prompt, model=None, stream=False):
        model = model or self.default_model
        url = f"{self.base_url}/api/generate"
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': stream,
            'options': {
                'temperature': 0.7,
                'top_p': 0.9,
                'max_tokens': 500,
            }
        }
        # Use streaming to support chunked NDJSON responses from Ollama
        r = requests.post(url, json=payload, stream=True, timeout=(3, 20))
        r.raise_for_status()
        collected = []
        try:
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = None
                    import json as _json
                    obj = _json.loads(line)
                    if isinstance(obj, dict) and 'response' in obj:
                        collected.append(obj.get('response') or '')
                except Exception:
                    # ignore non-json lines
                    continue
        finally:
            try:
                r.close()
            except Exception:
                pass

        return ''.join(collected).strip()

    def embed(self, text, model=None):
        model = model or self.default_model
        url = f"{self.base_url}/api/embeddings"
        payload = {'model': model, 'prompt': text}
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json().get('embedding')
