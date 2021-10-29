import re

from environs import Env
import telebot

env = Env()
env.read_env()
bot = telebot.TeleBot(env('bot_token'))
admins = env.list('admins')


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        return bot.get_chat_member(message.chat.id, message.from_user.id).status in ['administrator', 'creator']


bot.add_custom_filter(IsAdmin())


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


@bot.message_handler(content_types=['left_chat_member'])
def delete_leave_message(m):
    """Пользователь покинул группу"""
    print('delete_leave_message')
    if m.left_chat_member.id != bot.get_me().id:
        try:
            bot.delete_message(m.chat.id, m.message_id)
        except:
            bot.send_message(m.chat.id, "Please make me an admin")


@bot.message_handler(content_types=['new_chat_members'])
def delete_join_message(m):
    """Новый пользователь в группе"""
    print('delete_join_message')
    try:
        bot.delete_message(m.chat.id, m.message_id)
    except:
        if m.new_chat_member.id != bot.get_me().id:
            bot.send_message(m.chat.id, "Please make me an admin")
        else:
            bot.send_message(m.chat.id, "Hi! I am your trusty GroupSilencer Bot!")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def text_message(message):
    """Текстовое сообщение"""
    """
    if message.chat.type == "private":
	# private chat message

if message.chat.type == "group":
	# group chat message

if message.chat.type == "supergroup":
	# supergroup chat message

if message.chat.type == "channel":
	# channel message
    """
    print('text_message')
    regex = r"\b((?:https?://)?(?:(?:www\.)?" \
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
    text = message.text
    if re.search(regex, text):
        bot.delete_message(message.chat.id, message.message_id)
        # bot.send_message(message.chat.id, "Ссылки запрещены!")


@bot.channel_post_handler(is_admin=False)
def channel_message(message):
    """Сообщение в канале"""
    print('channel_message')
    text = message.text
    bot.reply_to(message, message.text)


@bot.message_handler()
def chat_message(message):
    """Сообщение в группе"""
    print('chat_message')
    text = message.text
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    """Start bot"""
    bot.infinity_polling()
