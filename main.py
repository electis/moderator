import re
import json
from threading import Timer

from environs import Env
import telebot

env = Env()
env.read_env()

settings = {
    '-1001749011309': dict(greeting_text="Здравствуй {username}, очень рады тебя приветствовать в нашем чате.",
                           greeting_video='https://telegra.ph/file/4a150e0856f8c20ca65ea.mp4',
                           greeting_timeout=10),
}
default = dict(
    greeting_text=env('greeting_text'),
    greeting_video=env('greeting_video', default=None),
    greeting_timeout=env.int('greeting_timeout', default=60),
)
restricted: set = set(env.list('restricted', default=['url', 'tag', 'photo', 'document', 'voice']))
bot = telebot.TeleBot(env('bot_token'))

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


def reload_settings():
    global settings
    with open('settings.json') as file:
        settings = json.loads(file.read())


def save_settings():
    with open('settings.json', 'w') as file:
        file.write(json.dumps(settings))


@bot.message_handler(content_types=['left_chat_member'])
def delete_leave_message(m):
    if m.left_chat_member.id != bot.get_me().id:
        try:
            # удаляем сообщение о выходе
            bot.delete_message(m.chat.id, m.message_id)
        except Exception as exc:
            print("Please make me an admin", exc)


@bot.message_handler(content_types=['new_chat_members'])
def delete_join_message(message):
    """Новый пользователь в группе"""
    chat_id = message.chat.id
    greeting = settings.get(str(chat_id)) or default
    greeting_text = greeting['greeting_text'].format(username=message.from_user.full_name)
    greeting_video = greeting.get('greeting_video')
    greeting_timeout = greeting.get('greeting_timeout') or default['greeting_timeout']
    try:
        # удаляем сообщение о вступлении
        bot.delete_message(chat_id, message.message_id)
        if greeting_video:
            msg = bot.send_video(chat_id, greeting_video, caption=greeting_text)
        else:
            msg = bot.send_message(chat_id, text=greeting_text)
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
    print(message.chat.id)
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
    reload_settings()
    bot.infinity_polling()
