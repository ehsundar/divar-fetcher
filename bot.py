import os

from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext

import post_storage
import storage
from fetcher import DivarFetcher


class TelegramBot:
    def __init__(self, conn):
        self.conn = conn
        self.user_manager = storage.UserManager(self.conn)
        self.post_manager = post_storage.PostManager(self.conn)

        self.application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

        start_handler = CommandHandler("start", self.start)
        self.application.add_handler(start_handler)

        self.application.job_queue.run_repeating(self.run_divar_fetcher, interval=30, first=0)

        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = self.user_manager.get(chat_id)
        if user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Already subscribed")
        else:
            _ = self.user_manager.create(
                storage.User(
                    chat_id=chat_id,
                ),
            )
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Subscribed!")

    async def run_divar_fetcher(self, context: CallbackContext):
        fetcher = DivarFetcher(self.conn, self.post_manager)
        saved_posts = await fetcher.fetch()
        for post in saved_posts:
            await self.send_post_to_users(context, post)

    @staticmethod
    def get_post_caption(post) -> str:
        caption = f"{post.to_persian_desc()}\n\nhttps://divar.ir/v/{post.token}"
        if post.phone:
            caption += f"\nPhone: {post.phone}"
        return caption

    async def send_post_to_users(self, context: CallbackContext, post: post_storage.Post):
        for user in self.user_manager.get_all():
            await self.send_post_to_user(context, post, user)
            user.last_notified = post.token
            self.user_manager.save(user)

    async def send_post_to_user(self, context: CallbackContext, post: post_storage.Post, user: storage.User):
        if post.image_count:
            media = []
            for i in range(post.image_count):
                if i == 0:
                    url = f"https://s101.divarcdn.com/static/pictures/{post.token}.jpg"
                    media.append(InputMediaPhoto(url, caption=self.get_post_caption(post)))
                else:
                    url = f"https://s101.divarcdn.com/static/pictures/{post.token}.{i}.jpg"
                    media.append(InputMediaPhoto(url))

            await context.bot.send_media_group(
                chat_id=user.chat_id,
                media=media,
            )
        else:
            await context.bot.send_message(chat_id=user.chat_id, text=self.get_post_caption(post))

        if post.phone:
            await context.bot.send_contact(chat_id=user.chat_id, phone_number=post.phone,
                                           first_name="بنگاه دیوار", last_name=post.token)
