import requests
from typing import Optional

class TectChatLLM():
  def __init__(self, model_name: str, base_url: str, api_key: Optional[str] = None, ):
    self.api_key = api_key
    self.model_name = model_name
    self.base_url = base_url
  def generate(self, prompt: str):
    res = requests.post(self.base_url, json= {
      "model": self.model_name,
      "prompt": prompt,
      "stream": False
    })
    return res.json()["response"]
    