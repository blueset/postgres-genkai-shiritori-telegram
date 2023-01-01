import asyncio
from pyppeteer import launch

template = open("./template.html").read()

GOJUON_INITIAL = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'さ', 'し', 'す', 'せ', 'そ',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'た', 'ち', 'つ', 'て', 'と',
    'だ',             'で', 'ど',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ま', 'み', 'む', 'め', 'も',    
    'や',       'ゆ',       'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'ゔ',
]
CHOICES = (2, 3, 4, 5, 6, 7, "8<sup>+</sup>")

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto("file://" + __file__.replace("generate.py", "template.html"))
    await page.setContent(template)
    elm = await page.querySelector("main")
    for w in GOJUON_INITIAL:
        for c in CHOICES:
            print(w, c, "...")
            await page.evaluate(f'document.querySelector("#word span").innerHTML = "{w}"; document.querySelector("#count span").innerHTML = "{c}";')
            await elm.screenshot({'path': f'{w}_{str(c)[0]}.png', "omitBackground": True,})
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())