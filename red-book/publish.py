# 发布帖子

# 点击发布按钮，跳转新页面
# #global > div.main-container > div.side-bar > ul > div.channel-list-content > li:nth-child(2) > a
# 发布页url https://creator.xiaohongshu.com/publish/publish?source=official
# 点击上传图文 
#web > div > div > div > div.header > div.header-tabs > div.creator-tab
# 点击文字配图
# #web > div > div > div > div.upload-content.hasBannerHeight > div.upload-wrapper > div > div > div > button.d-button.d-button-default.d-button-with-content.--color-static.bold.--color-bg-fill.--color-text-paragraph.custom-button.white.upload-button.text2image-button

# 选中内容输入框
#web > div > div > div.card-editor-container > div > div.edit-text-item-container > div > div.swiper-wrapper > div.swiper-slide.swiper-slide-active.text-editor-slide.focused

# 点击生成图片
#web > div > div > div.card-editor-container > div > div.edit-text-button-container > div


# 点击换配色
#web > div > div > div.image-editor-container > div.image-overview > div.right-container > div.cover-list-container-wrapper > div > div:nth-child(1) > div.cover-item > div

# 点击下一步
#web > div > div > div.image-editor-container > div.overview-footer > button


# 话题选择
#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.bottom > div > div > span:nth-child(1)

# 再次点击发布按钮
#web > div > div > div.publish-page-container > div.publish-page-publish-btn > button.d-button.d-button-default.d-button-with-content.--color-static.bold.--color-bg-fill.--color-text-paragraph.custom-button.bg-red

from playwright.async_api import Browser, Page
import time
import random
from generate import post_content_generate

async def publish_post(browser: Browser, page: Page):
  # 回到首页
  if page.url != "https://www.xiaohongshu.com/explore":
    await page.goto("https://www.xiaohongshu.com/explore")
    time.sleep(5)

  async with browser.contexts[0] .expect_event("page") as event_info:
    # 发布按钮
    # 点击之后跳转新页面，我们需要从contexts中查找到发布的page
    await page.click(selector="#global > div.main-container > div.side-bar > ul > div.channel-list-content > li:nth-child(2) > a")

  publish_page: Page = await event_info.value
  await publish_page.wait_for_load_state("domcontentloaded")
  time.sleep(5)

  tabs = await publish_page.query_selector_all("#web > div > div > div > div.header > div.header-tabs > div")
  print(tabs)
  for tab in tabs:
    text = await tab.inner_text()
    # style = await tab.get_attribute("style")
    if text == "上传图文":
      try:
        await tab.click()
      except Exception as e:
        print(f"发生未知错误：{e}")

  # time.sleep(6000)
  # await publish_page.click(selector="#web > div > div > div > div.header > div.header-tabs > div:nth-child(3)", timeout=60000)
  time.sleep(5)

  # time.sleep(60000)
  await publish_page.click(selector="#web > div > div > div > div.upload-content > div.upload-wrapper > div > div > div > button.text2image-button")
  time.sleep(5)

  await publish_page.click(selector="#web > div > div > div.card-editor-container > div > div.edit-text-item-container > div > div.swiper-wrapper > div.swiper-slide.text-editor-slide")
  time.sleep(5)

  # 输入文字
  post_info = post_content_generate()
  await publish_page.fill(selector="#web > div > div > div.card-editor-container > div > div.edit-text-item-container > div > div.swiper-wrapper > div.swiper-slide.text-editor-slide> div > div.editor-content.content-mode > div > div", value=post_info["content"])

  # 点击生成
  await publish_page.click(selector="#web > div > div > div.card-editor-container > div > div.edit-text-button-container > div")
  time.sleep(5)

  # 点击配色
  for i in range(0, random.randint(1, 6)):
    await publish_page.click(selector="#web > div > div > div.image-editor-container > div.image-overview > div.right-container > div.cover-list-container-wrapper > div > div:nth-child(1) > div.cover-item > div")
    time.sleep(5)
  
  await publish_page.click(selector="#web > div > div > div.image-editor-container > div.overview-footer > button")

  # 选择推荐的前5个话题
  # for i in range(0,5):
  #   await publish_page.click(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.bottom > div > div > span:nth-child(1)")
  #   time.sleep(5)

  # 填充标题
  # 先清空
  await publish_page.fill(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div", value="")
  time.sleep(3)
  await publish_page.type(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div", text=post_info["title"])
  time.sleep(5)

  # 填充标签
  for tag in post_info["tags"]:
    
    # await publish_page.type(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div", text="#")
    # time.sleep(5)
    await publish_page.type(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div", text=tag)
    time.sleep(3)
    await publish_page.press(selector="#web > div > div > div.publish-page-container > div.style-override-container.red-theme-override-container > div > div.publish-page-content > div.publish-page-content-base > div > div.editor-container > div.editor-content > div > div", key="Enter")
    time.sleep(3)
  
  # 发布
  # await publish_page.click(selector="#web > div > div > div.publish-page-container > div.publish-page-publish-btn > button.d-button.d-button-default.d-button-with-content.--color-static.bold.--color-bg-fill.--color-text-paragraph.custom-button")
  time.sleep(5)

  # await publish_page.close()

  

  
