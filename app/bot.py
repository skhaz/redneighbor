# -*- coding: utf-8 -*-
import os
import logging
import random
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from google.appengine.api import app_identity

from flask import Blueprint, request

from emoji import emojize
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

blueprint = Blueprint('bot', __name__)

token = os.environ['TELEGRAM_TOKEN']
bot = Bot(token)
dispatcher = None

THUMBS_UP = emojize(":thumbs_up_sign:")
THUMBS_DOWN = emojize(":thumbs_down_sign:")


def moderate(key, args):
    lat = args.get('lat', '0.0')
    lon = args.get('lon', '0.0')
    url = args.get('url', '')
    city = args.get('city', 'N/A')
    email = args.get('email', '')
    caption = "%s (%s, %s)\n%s" % (city.capitalize(), lat, lon, email)

    keyboard = [[InlineKeyboardButton(THUMBS_UP, callback_data=u'%s-%s' % (THUMBS_UP, key)),
                 InlineKeyboardButton(THUMBS_DOWN, callback_data=u'%s-%s' % (THUMBS_DOWN, key))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendPhoto(chat_id=147441483, caption=caption, photo=url, reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    action, key = query.data.split('-')
    keyboard = [[InlineKeyboardButton(THUMBS_UP, callback_data=u'%s-%s' % (THUMBS_UP, key)),
                 InlineKeyboardButton(THUMBS_DOWN, callback_data=u'%s-%s' % (THUMBS_DOWN, key))]]

    from app.models import Nude
    nude = ndb.Key(urlsafe=key).get()
    nude.public = True if action == THUMBS_UP else False
    nude.put()

    bot.editMessageCaption(
        caption="%s" % action,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=InlineKeyboardMarkup(keyboard))


def echo(bot, update):
    quotes = [
        "Meu direito é ficar calado, não quero falar com bandeirantes.",
        "Eu gosto da câmera, o microfone pra mim é tudo",
        "Ah morre, DIABO!",
        "To falanu, num to falanu!? Não quero falar com você! Não interessa, isso é problema meu Eu quero é que você se foda seu filho duma puta!",
        "Não é a mamãe!!!",
    ]

    update.message.reply_text(random.choice(quotes))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


@blueprint.before_app_first_request
def setup_webhook():
    global dispatcher

    dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_error_handler(error)

    hostname = app_identity.get_default_version_hostname()
    bot.setWebhook(webhook_url='%s/telegram/%s' % (hostname, token))


@blueprint.route('/telegram/' + token, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)

    return ('', 204)
