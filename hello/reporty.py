import requests
from datetime import date

def call_llm(prompt):
  url = 'http://localhost:11434/api/generate'
  res = requests.post(
    'http://localhost:11434/api/generate',
    json = {  
      "model": "qwen2.5:latest",
      "prompt": prompt,
      "stream": False
    }
  )
  # print(res.json())
  return res.json()["response"]

user_input = ""
with open("input.txt", "r", encoding="utf-8") as f:
  user_input = f.read()

today = date.today().isoformat()
prompt = f"""
今天日期是：{today}

你是一个专业的软件工程师，请帮我生成一份工作日报。

用户输入：
{user_input}

要求:
- 用中文
- 输出Markdown
- 包含：工作内容 + 总结
"""

result = call_llm(prompt)

with open("report.md", "w", encoding="utf-8") as f:
  f.write(result)

print("日报已生成：report.md")

