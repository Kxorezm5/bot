import time
import logging
from telethon import TelegramClient, events, errors
from rich.console import Console
from rich.progress import Progress

# Log faylni sozlash
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rich konsol obyektini yaratish
console = Console()

# Telegram API ma'lumotlari
api_id = "29967745"
api_hash = "342ef8111de16d621ac725445c9c8296"

# Telegram klientini ishga tushirish
client = TelegramClient('userbot', api_id, api_hash)

async def forward_messages():
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Xabarlarni jo'natish...", total=None)

            # Istalgan chatlardan xabarlarni olish
            async for message in client.iter_messages("me", limit=None):
                try:
                    if message.text:
                        logger.info(f"Habarni jo'natish: {message.text[:50]}...")
                        await client.send_message("me", message.text)  # Saqlangan habarlarga jo'natish
                        progress.update(task, advance=1)
                except errors.FloodWaitError as exc:
                    wait_time = exc.seconds
                    logger.warning(f"Flood aniqlangan. {wait_time} soniya kutish...")
                    console.log(f"[yellow]Flood aniqlangan. {wait_time} soniya kutish...[/yellow]")
                    time.sleep(wait_time)
                time.sleep(1)  # Har bir xabar orasida kutish

            progress.remove_task(task)
            console.log("[green]Barcha xabarlar muvaffaqiyatli jo'natildi![/green]")

    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        console.log(f"[red]Xatolik yuz berdi: {e}[/red]")

# Terminal interfeysini yaxshilash uchun login qismi
async def main():
    console.log("[cyan]Telegram klientiga ulanmoqda...[/cyan]")
    try:
        await client.start()
        console.log("[green]Klient muvaffaqiyatli ishga tushdi![/green]")
        console.log("[yellow]Xabarlarni jo'natish jarayoni boshlanmoqda...[/yellow]")
        await forward_messages()
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        console.log(f"[red]Xatolik yuz berdi: {e}[/red]")
    finally:
        console.log("[cyan]Klientni yopmoqda...[/cyan]")
        await client.disconnect()

if __name__ == "__main__":
    with console.status("[bold cyan]Dastur ishga tushmoqda...[/bold cyan]") as status:
        client.loop.run_until_complete(main())
