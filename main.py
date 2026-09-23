import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import yt_dlp
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Render Web Service faolligini ushlab turuvchi veb-server
async def handle(request):
    return web.Response(text="YouTube Downloader Bot ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

def download_youtube_video(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        # YouTube IP blokirovkalarini aylanib o'tish
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'mweb', 'web_embedded'],
                'skip': ['hls', 'dash']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "Menga **YouTube** video yoki **Shorts** havolasini yuboring, men uni sizga yuklab beraman! 🎬",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    
    if not any(domain in url.lower() for domain in ["youtube.com", "youtu.be"]):
        await message.answer("⚠️ Iltimos, faqat **YouTube** yoki **YouTube Shorts** havolasini yuboring.")
        return

    status_msg = await message.answer("⏳ YouTube'dan video yuklanmoqda...")
    file_path = f"yt_{message.from_user.id}.mp4"
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download_youtube_video, url, file_path)
        
        await status_msg.edit_text("📤 Telegram'ga yuborilmoqda...")
        
        video_file = types.FSInputFile(file_path)
        await message.answer_video(
            video=video_file,
            caption="✅ **Videongiz tayyor!**",
            parse_mode="Markdown"
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("❌ Videoni yuklab bo'lmadi. Havolani tekshirib qayta yuboring.")
        print(f"Xato: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    print("YouTube Bot ishga tushdi...")
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
