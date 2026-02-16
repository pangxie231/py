import requests
from urllib.parse import urlparse

def parse_repo(url):
  parts = urlparse(url).path.strip("/").split("/")
  return parts[0], parts[1]

def get_repo_tree(owner, repo):
  api = f"https://api.github.com/repos/{owner}/{repo}/contents"
  res = requests.get(api)
  return res.json()

url = input("请输入Github仓库地址：\n")
owner, repo = parse_repo(url)

files = get_repo_tree(owner, repo)

for f in files:
  print(f["type"], f["name"])


def format_tree(files):
  lines = []
  for f in files:
    lines.append(f"-{f['type']}: {f['name']}")
  return "\n".join(lines)

def call_llm(prompt):
  res = requests.post(
    "http://localhost:11434/api/generate",
    json={
      "model": "qwen2.5:latest",
      "prompt": prompt,
      "stream": False
    }
  )
  return res.json()["response"]

tree_text = format_tree(files)

prompt = f"""
你是一个高级软件架构师，请分析以下Github 项目结构:

项目：{owner}/{repo}

文件结构：
{tree_text}

请输出：
1.项目简介
2.项目结构分析
3.技术栈推测
4.优点
5.风险点
6.改进简易

用Markdown输出。
"""

result = call_llm(prompt)

with open("analysis.md", "w", encoding="utf-8") as f:
    f.write(result)

print("分析完成：analysis.md")
