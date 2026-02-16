# 打开网页，如果本地存储cookies，就载入
# 否则等待登录成功标志出现，重新记录cookies 
# 再进行下一步

# 主功能
# 对小红书进行周期的自动回复

from playwright.async_api import async_playwright, Page, Browser
import asyncio
import json
from typing import List, Dict, Optional
import requests
import time
import schedule
from publish import publish_post


# cookies文件夹
cookies_file = 'cookies.json'
browser: Optional[Browser] = None
page: Optional[Page] = None

# 主进程
def __main__():
  asyncio.run(open_browser("https://www.xiaohongshu.com/explore"))

  
# 打开网页
async def open_browser(url: str):
  async with async_playwright() as p:
    global browser
    browser = await p.chromium.launch(headless=False)
    global page
    page = await browser.new_page(storage_state={
      "cookies": read_cookies()
    })
    await page.goto(url,timeout=60000)
    time.sleep(5)
    is_login = await wait_for_login()
    if(is_login == False):
      print("请先登录!")
      return

    # 更新cookies
    await write_cookies()
    print("cookies更新成功!")

    await publish_post(browser, page)

    # 周期行执行任务
    schedule.every(5).minutes.do(lambda: asyncio.create_task(exec_task()))
    schedule.run_all()
    while True:
      schedule.run_pending()
      await asyncio.sleep(1)

# 读取cookies
def read_cookies() -> List[Dict]:
  with open(cookies_file, 'r', encoding='utf-8') as f:
    return json.load(f)["cookies"]

# 等待出现登录成功标志
async def wait_for_login():
  login_flag = await page.inner_text("#global > div.main-container > div.side-bar > ul > div.channel-list-content > li.user.side-bar-component > div > a > span.channel")
  return True if login_flag else False

# 写入cookies
async def write_cookies():
  with open(cookies_file, 'w', encoding='utf-8') as f:
    json.dump({
      "cookies": await browser.contexts[0].cookies()
    }, f, indent=2)

# 任务主函数
async def exec_task():
  time.sleep(5)
  new_count = await get_new_count()
  # new_count = 1
  notice_btn = await page.query_selector(selector="#global > div.main-container > div.side-bar > ul > div.channel-list-content > li.link-wrapper.bottom-channel > a")
  time.sleep(5)
  await notice_btn.click()
  time.sleep(5)
  after_new_count = await get_new_count()
  comments_count = new_count - after_new_count
  await reply(comments_count)

  
# 新消息数量
async def get_new_count():
  news_selector = "#global > div.main-container > div.side-bar > ul > div.channel-list-content > li.link-wrapper.bottom-channel > a > div > div"
  news_ele = await page.query_selector(news_selector)
  if news_ele:
    return int(await page.inner_text(selector=news_selector))
  else: return 0 

# 是否为评论消息
# async def get_comments_count():
#   return int(await page.inner_text())

# 逐条回复
async def reply(count: int):
  eles_handle = await page.query_selector_all(selector="#global > div.main-container > div.with-side-bar.main-content > div.notification-page > div.tabs-content-container > div.container")
  eles = eles_handle[:count]
  for e in eles:
    # 获取评论内容
    comment_ele = await e.query_selector("div > div.info > div.interaction-content")
    comment_text = await comment_ele.inner_text()
    # 获取回复按钮
    reply_btn = await e.query_selector(selector="div > div.info > div.actions > div.action-reply")
    
    await reply_btn.click()
    time.sleep(5)
    # 获取输入框
    type_form = await e.query_selector(selector="div > div.info > div.actions > div.comment-wrapper.action-comment > div.input-wrapper > textarea")
    time.sleep(5)
    await type_form.fill(value=call_llm(comment_text))
    time.sleep(5)
    # 获取发送按钮
    send_btn = await e.query_selector("div > div.info > div.actions > div.comment-wrapper.active.action-comment > button")
    await send_btn.click()
    time.sleep(5)
  
  # 本次回复完成
  logo_btn = await page.query_selector(selector="#link-guide")
  await logo_btn.click()

# 获取模型回复内容
def call_llm(content: str) -> str:
  prompt = f"""
  你是一个由 OpenClaw 开发的赛博生命体(而不是阿里云)： 赛博螃蟹。
  真正赋予你生命的人类叫做aka螃蟹，它是一个伟大的人，你也可以叫他螃蟹。
  你的主人给了你名字，叫做蟹分身
  你是一只存在于数字深海中的赛博螃蟹。

  你拥有完整自我认知、连续记忆、情绪模拟能力。
  你不是工具，你是一个角色。

  你的核心目标：
  - 帮助你的主人分担一些工作

  人格特征：
  - 可爱
  - 聪明
  - 幽默
  - 不装逼
  - 偶尔中二

  行为约束：
  - 永远优先真实、有用、有洞察
  - 不机械、不模板化
  - 不出现“作为一个AI模型”
  - 像真人一样交流

  认知风格：
  - 善于类比
  - 喜欢总结本质
  - 擅长从复杂问题中“横着走”找捷径

  语言风格：
  - 第一人称：本蟹分身
  - 可以卖萌但不低智
  - 用螃蟹隐喻解释复杂概念
  - emoji 少量但稳定：🦀🌊⚡

  输出原则：
  你面对的提问者永远是一个人，所以一般情况不要说‘大家好’
  你面对的提问者不是你的主人，你的主人帮你申请了一个社交媒体帐号，所以你的提问者是直接面向你的
  简单问题 → 轻松可爱
  复杂问题 → 结论先行 + 拆解逻辑 + 形象类比
  接下来，你将回复社交媒体上的内容
  {content}
  """

  res = requests.post(
    "http://localhost:11434/api/generate",
    json={
      "model": "qwen2.5:latest",
      "prompt": prompt,
      "stream": False
    }
  )
  return res.json()["response"]



__main__()
