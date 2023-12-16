from constant import *
from telegram import Update,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os
from files import datas
import datetime
from db import connect_to_database
import uuid

load_dotenv()
RECEIVER=os.getenv("RECEIVER")
PREORDER_STATE, PREORDER_CHOOSE, PREORDER_CONFIRMED_STATE, PREORDER_CANCEL_STATE = range(4)

async def start(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    await update.message.reply_text(
        text=WELCOME_MESSAGE,
        # reply_markup=ReplyKeyboardMarkup([["/preorder"]],resize_keyboard=True)
    )

    try:
        user = db_client[os.getenv("DBNAME")].users.find_one({'user_id': update.effective_chat.id})
        if user:
            print("user is here")
            return
    except Exception as e:
        print(e)

    try:
        db_client[os.getenv("DBNAME")].users.insert_one({
            'user_id': update.message.from_user.id,
            'full_name': update.message.from_user.full_name,
            'username': update.message.from_user.username,
            'join_date': update.message.date,
        })
    except Exception as e:
        print("Error")
        print(e)

async def preorderChoose(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton('💴 ریال', callback_data='Rial'),
         InlineKeyboardButton('💳 Paypal', callback_data='Paypal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=WHICHTYPE,
        reply_markup=reply_markup,
    )
    return PREORDER_CHOOSE

async def waitingRecipt(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if update.callback_query.data == 'Rial':
        await query.edit_message_text(text=f"روش ریالی انتخاب شد")
    elif update.callback_query.data == 'Paypal':
        await query.edit_message_text(text=f"روش پیپال انتخاب شد")
    keyboard = [
        [InlineKeyboardButton('🚫 Cancel', callback_data='Cancel'),]
    ]
    context.user_data['payment_method'] = update.callback_query.data

    reply_markup = InlineKeyboardMarkup(keyboard)
    result=None
    if update.callback_query.data == 'Rial':
        result=await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=RIAL,
            reply_markup=reply_markup,
        )

    elif update.callback_query.data == 'Paypal':
        result=await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PAYPAL,
            reply_markup=reply_markup,
        )
    context.user_data['payment_method'] = update.callback_query.data
    context.user_data['removing_cancel'] = result.id
    print(result)
    print(result.id)

    return PREORDER_STATE


async def userTextRecipt(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    keyboard = [
        [InlineKeyboardButton('❌ Reject', callback_data='Reject'),
         InlineKeyboardButton('✅ Accept', callback_data='Accept')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['full_name'] = update.effective_chat.full_name
    context.user_data['username'] = update.effective_chat.username
    context.user_data['user_id'] = update.effective_chat.id
    context.user_data['payment_receipt'] = update.message.text
    await context.bot.send_message(
        chat_id=RECEIVER,
        text=
        f"Pre-order\n" +
        f"payment_method:{context.user_data['payment_method']}\n" +
        (f"username:@{context.user_data['username']}\n" if (context.user_data['username'] is not None) else "") +
        f"user_id:{context.user_data['user_id']}\nfull_name:{context.user_data['full_name']}\n"+
        "-------------------------\n" +
        context.user_data['payment_receipt']
    ,
        reply_markup=reply_markup
    )

    try:
        db_client[os.getenv("DBNAME")].payments.insert_one({
            'user_id': update.effective_chat.id,
            'payment_receipt': update.effective_message.photo[0].file_id,
            'payment_receipt_type': 'text',
            'payment_method': context.user_data['payment_method'],
            'date': datetime.datetime.now().isoformat(),
            'verified': False,
            'rejected': False
        })
    except:
        # ToDo:
        print("Error2-1")

    await update.message.reply_text(
        text=THANKFUL_MESSAGE,
    )
    await context.bot.editMessageReplyMarkup(message_id=context.user_data['removing_cancel'],chat_id=update.effective_chat.id)

    db_client.close()

    return ConversationHandler.END


async def userImageRecipt(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    keyboard = [
        [InlineKeyboardButton('❌ Reject', callback_data='Reject'),
         InlineKeyboardButton('✅ Accept', callback_data='Accept')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    context.user_data['full_name'] = update.effective_chat.full_name
    context.user_data['username'] = update.effective_chat.username
    context.user_data['user_id'] = update.effective_chat.id


    await context.bot.send_photo(
        # TODO
        chat_id=RECEIVER,
        photo=update.message.photo[0].file_id,
        caption=
        f"Pre-order\n" +
        f"payment_method:{context.user_data['payment_method']}\n" +
        (f"username:@{context.user_data['username']}\n" if (context.user_data['username'] is not None) else "") +
        f"user_id:{context.user_data['user_id']}\nfull_name:{context.user_data['full_name']}\n",
        reply_markup=reply_markup
    )

    try:
        db_client[os.getenv("DBNAME")].payments.insert_one({
            'user_id': update.effective_chat.id,
            'payment_receipt': update.effective_message.photo[0].file_id,
            'payment_receipt_type': 'image',
            'payment_method': context.user_data['payment_method'],
            'date': datetime.datetime.now().isoformat(),
            'verified': False,
            'rejected': False
        })
    except:
        # ToDo:
        print("Error2-2")

    await update.message.reply_text(
        text=THANKFUL_MESSAGE,
    )
    await context.bot.editMessageReplyMarkup(message_id=context.user_data['removing_cancel'],chat_id=update.effective_chat.id)

    db_client.close()

    return ConversationHandler.END

async def userDocRecipt(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    keyboard = [
        [InlineKeyboardButton('❌ Reject', callback_data='Reject'),
         InlineKeyboardButton('✅ Accept', callback_data='Accept')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    context.user_data['full_name'] = update.effective_chat.full_name
    context.user_data['username'] = update.effective_chat.username
    context.user_data['user_id'] = update.effective_chat.id
    await context.bot.send_document(
        chat_id=RECEIVER,
        document=update.message.document.file_id,
        caption=
        f"Pre-order\n" +
        f"payment_method:{context.user_data['payment_method']}\n" +
        (f"username:@{context.user_data['username']}\n" if (context.user_data['username'] is not None) else "") +
        f"user_id:{context.user_data['user_id']}\nfull_name:{context.user_data['full_name']}\n",
        reply_markup=reply_markup
    )

    try:
        db_client[os.getenv("DBNAME")].payments.insert_one({
            'user_id': update.effective_chat.id,
            'payment_receipt': update.effective_message.document.file_id,
            'payment_receipt_type': 'document',
            'payment_method': context.user_data['payment_method'],
            'date': datetime.datetime.now().isoformat(),
            'verified': False,
            'rejected': False
        })
    except:
        # ToDo:
        print("Error2-3")

    await update.message.reply_text(
        text=THANKFUL_MESSAGE,
    )
    await context.bot.editMessageReplyMarkup(message_id=context.user_data['removing_cancel'],chat_id=update.effective_chat.id)

    db_client.close()

    return ConversationHandler.END


#  ToDo name of def and vars
async def preorder_cancel(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Canceled\n برای پیش خرید /preorder را ارسال کنید")

    
    return ConversationHandler.END


async def acceptHandeling(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    credentials = get_user_credentials(update.effective_message)
    await context.bot.send_message(
        chat_id=credentials['user_id'],
        text=ACCEPTED
    )
    for data in datas:
        if data['type']=='mp3':
            await context.bot.send_audio(
                chat_id=credentials['user_id'],
                audio=data['file_id'],
            )
        elif data['type']=='photo':
            await context.bot.send_photo(
                chat_id=credentials['user_id'],
                document=data['file_id'],
            )
        elif data['type']=='pdf':
            await context.bot.send_document(
                chat_id=credentials['user_id'],
                document=data['file_id'],
            )
    if update.effective_message.text:
        await update.effective_message.edit_text(
            update.effective_message.text+
            "\n-------------------------"+
            "\nAdmin Accept : "+
            f"{update.callback_query.from_user.full_name}"
            )
    elif update.effective_message.caption:
        await update.effective_message.edit_caption(
            update.effective_message.caption+
            "\n-------------------------"+
            "\nAdmin Accept : "+
            f"{update.callback_query.from_user.full_name}"
            )

    db_client['DBNAME'].payments.update_one({'transaction_id': credentials['uuid']}, { "$set": {"verified": True}})

    return ConversationHandler.END


async def rejectHandeling(update: Update, context: CallbackContext) -> int:
    try: 
        db_client = connect_to_database(os.getenv("DBSTRING"))
    except Exception as e:
        print("Failed to connect to the database!")

    credentials = get_user_credentials(update.effective_message)
    await context.bot.send_message(
        chat_id=credentials['user_id'],
        text=REJECTED
    )
    if update.effective_message.text:
        await update.effective_message.edit_text(
            update.effective_message.text+
            "\n-------------------------"+
            "\nAdmin Reject : "+
            f"{update.callback_query.from_user.full_name}"
            )
    elif update.effective_message.caption:
        await update.effective_message.edit_caption(
            update.effective_message.caption+
            "\n-------------------------"+
            "\nAdmin Reject : "+
            f"{update.callback_query.from_user.full_name}"
            )

    db_client['DBNAME'].payments.update_one({'transaction_id': credentials['uuid']}, { "$set": {"rejected": True}})

    return ConversationHandler.END


def get_user_credentials(effective_message):
    lines = []
    payment_receipt = None
    credentials = {}
    if effective_message.text:
        payment_receipt = effective_message.text.split('-------------------------')[1]
        lines = effective_message.text.splitlines()  # Split the string into lines

    elif effective_message.caption:
        print(f"update.effective_message:{type(effective_message)}")

        if effective_message.document:
            payment_receipt = effective_message.document.file_id
        elif effective_message.photo:
            payment_receipt = effective_message.photo[0].file_id
        lines = effective_message.caption.splitlines()  # Split the string into lines
    credentials['payment_receipt'] = payment_receipt
    for line in lines:
        if 'user_id' in line:
            credentials['user_id'] = int(line.split(':')[1])
        elif 'payment_method' in line:
            credentials['payment_method'] = line.split(':')[1]
        elif 'uuid' in line:
            credentials['uuid'] = line.split(':')[1]
    return credentials

