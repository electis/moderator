import re
from threading import Timer

from environs import Env
import telebot

env = Env()
env.read_env()

bot = telebot.TeleBot(env('bot_token'))
restricted: set = set(env.list('restricted', default=['url', 'tag', 'photo', 'document', 'voice']))
greeting_text = env('greeting_text')
greeting_video = env('greeting_video', default=None)
greeting_timeout = env.int('greeting_timeout', default=60)

tag_regex = "@[a-zA-Z]"
url_regex = r"\b((?:https?://)?(?:(?:www\.)?" \
            r"(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" \
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|" \
            r"(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}" \
            r"(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|" \
            r"(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}" \
            r"(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:" \
            r"(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::" \
            r"(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}" \
            r"(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:" \
            r"(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))" \
            r"(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"


@bot.message_handler(content_types=['left_chat_member'])
def delete_leave_message(m):
    if m.left_chat_member.id != bot.get_me().id:
        try:
            # удаляем сообщение о выходе
            bot.delete_message(m.chat.id, m.message_id)
        except:
            bot.send_message(m.chat.id, "Please make me an admin")


@bot.message_handler(content_types=['new_chat_members'])
def delete_join_message(message):
    """Новый пользователь в группе"""
    greeting = greeting_text.format(username=message.from_user.full_name)
    chat_id = message.chat.id
    try:
        # удаляем сообщение о вступлении
        bot.delete_message(chat_id, message.message_id)
        if greeting_video:
            msg = bot.send_video(chat_id, greeting_video, caption=greeting)
        else:
            msg = bot.send_message(chat_id, text=greeting)
        t = Timer(greeting_timeout, bot.delete_message, args=[msg.chat.id, msg.message_id])
        t.start()
    except Exception as exc:
        print(exc)


def is_admin(message):
    return bot.get_chat_member(message.chat.id, message.from_user.id).status in ['administrator', 'creator']

"""
content_types:
text, audio, document, photo, sticker, video, video_note, voice, location, contact, new_chat_members, 
left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created, supergroup_chat_created, 
channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message
"""
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                               'text', 'location', 'contact', 'sticker'])
def message(message):
    if is_admin(message):
        return
    # print(message.content_type)
    if (
            'url' in restricted and message.text and re.search(url_regex, message.text)
            or 'tag' in restricted and message.text and re.search(tag_regex, message.text)
            or message.content_type in restricted - {'url', 'tag'}
    ):
        bot.delete_message(message.chat.id, message.message_id)


if __name__ == '__main__':
    bot.infinity_polling()
