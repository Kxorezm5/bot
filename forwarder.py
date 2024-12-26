from telethon import TelegramClient, events
import asyncio
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from datetime import datetime
import os
import sys
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

API_ID = 10953300
API_HASH = "9c24426e5d6fa1d441913e3906627f87"

client = TelegramClient('session_name', API_ID, API_HASH)

DELAY_BETWEEN_MESSAGES = 2

DELAY_BY_MEDIA = {
    'text': 1,
    'photo': 2,
    'document': 2,
}

console = Console()

class ForwardBot:
    def __init__(self, client, delay):
        self.client = client
        self.delay = delay

    async def forward_messages(self, source, target, start_message_id=None, max_messages=None):
        console.log("[bold green]Xabarlar yuborish boshlandi...[/bold green]")

        try:
            count = 0
            start_time = datetime.now()
            messages = []

            async for message in self.client.iter_messages(source, offset_id=start_message_id):
                messages.append(message)

            with Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("🔄 Xabarlarni yuborish", total=len(messages))

                for message in messages:
                    if max_messages is not None and count >= max_messages:
                        break

                    await self.client.forward_messages(target, message)

                    message_type = self._get_message_type(message)
                    await asyncio.sleep(DELAY_BY_MEDIA.get(message_type, self.delay))

                    count += 1
                    progress.update(task, advance=1)

                    if count % 5 == 0:
                        console.log("⏳ [bold yellow]Ko'p xabar yuborildi, 5 soniya kuting...[/bold yellow]")
                        await asyncio.sleep(5)

            console.log("[bold green]Barcha xabarlar yuborildi![/bold green]")

        except FloodWaitError as e:
            console.log(f"[bold red]FloodWaitError:[/bold red] {e.seconds} soniya kutish kerak.")
            await asyncio.sleep(e.seconds)
            await self.forward_messages(source, target, start_message_id, max_messages)
        except RPCError as e:
            console.log(f"[bold red]Tarmoq yoki boshqa xatolik yuz berdi:[/bold red] {e}")
            await asyncio.sleep(10)
            await self.forward_messages(source, target, start_message_id, max_messages)
        except Exception as e:
            console.log(f"[bold red]Xatolik yuz berdi:[/bold red] {e}")

    def _get_message_type(self, message):
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                return 'photo'
            elif isinstance(message.media, MessageMediaDocument):
                return 'document'
        return 'text'

    async def handle_dot1_command(self, event):
        try:
            console.log("📤 [bold cyan].1 buyrug'i qabul qilindi[/bold cyan]")

            # Saqlangan xabarlarni aniqlash
            target_chat = 'me'  # "Saqlangan xabarlar" uchun

            # Reply qilingan xabarni olish
            reply_msg = await event.get_reply_message()
            start_message_id = reply_msg.id if reply_msg else None

            if reply_msg:
                await event.reply(f"📤 {start_message_id}-xabaridan boshlab yuborilmoqda...")
            else:
                await event.reply("📤 Reply qilingan xabar topilmadi. Barcha xabarlar yuborilmoqda...")

            # Xabarlarni yuborishni boshlash
            source_chat = await event.get_chat()
            source_id = source_chat.id
            await self.forward_messages(source_id, target_chat, start_message_id, max_messages=None)
            await event.reply("✅ Barcha xabarlar yuborildi!")
        except Exception as e:
            await event.reply(f"❌ Xatolik yuz berdi: {e}")

if __name__ == '__main__':
    console.log("[bold green]Bot ishlamoqda. Buyruqlarni yuborishingiz mumkin![/bold green]")
    forward_bot = ForwardBot(client, DELAY_BETWEEN_MESSAGES)

    # ".1" komandasi uchun handler
    @client.on(events.NewMessage(pattern=r'^\.1$'))
    async def handler(event):
        await forward_bot.handle_dot1_command(event)

    while True:
        try:
            with client:
                client.run_until_disconnected()
        except KeyboardInterrupt:
            console.log("[bold red]Dastur to'xtatildi.[/bold red]")
            sys.exit(0)
        except Exception as e:
            console.log(f"[bold red]Dastur xatosi:[/bold red] {e}. Qayta urinish...")
            asyncio.sleep(5)
