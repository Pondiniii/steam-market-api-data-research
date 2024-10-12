from telegram import Bot
import asyncio
from secrets import bot_token, chat_id

async def send_telegram_message(chat_id, message):
    try:
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        return sent_message
    except TelegramError as e:
        print(f"Błąd podczas wysyłania wiadomości: {e}")
        return None


async def edit_telegram_message(chat_id, message_id, new_text):
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=new_text,
        parse_mode='Markdown',
        disable_web_page_preview=False
    )


async def main():
    await send_telegram_message(chat_id=chat_id, message=message)


if __name__ == "__main__":
    bot = Bot(token=bot_token)
    message = "*Hello!* This is a test message with _Markdown_ format."
    asyncio.run(main())

