from constant import *
from telegram import Update,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

PREORDER_STATE, PREORDER_CHOOSE, PREORDER_CONFIRMED_STATE, PREORDER_CANCEL_STATE = range(4)
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        text=WELCOME_MESSAGE,
        reply_markup=ReplyKeyboardMarkup([["/preorder"]],resize_keyboard=True)
    )

async def preorderChoose(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton('💴 Rial', callback_data='Rial'),
         InlineKeyboardButton('💳 Paypal', callback_data='Paypal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=WHICHTYPE,
        reply_markup=reply_markup,
    )
    return PREORDER_CHOOSE

async def waitingRecipt(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton('🚫 Cancel', callback_data='Cancel'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query.data == 'Rial':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=RIAL,
            reply_markup=reply_markup,
        )
    elif update.callback_query.data == 'Paypal':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PAYPAL,
            reply_markup=reply_markup,
        )
    context.user_data['payment_method'] = update.callback_query.data
    return PREORDER_STATE

async def userTextRecipt(update: Update, context: CallbackContext) -> int:
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
        # TODO
        chat_id=update.effective_chat.id,
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
    return ConversationHandler.END
async def preorderImage(update: Update, context: CallbackContext) -> int:
    print(3)
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
        chat_id=update.effective_chat.id,
        photo=update.message.photo[0].file_id,
        caption=
        f"Pre-order\n" +
        f"payment_method:{context.user_data['payment_method']}\n" +
        (f"username:@{context.user_data['username']}\n" if (context.user_data['username'] is not None) else "") +
        f"user_id:{context.user_data['user_id']}\nfull_name:{context.user_data['full_name']}\n",
        reply_markup=reply_markup
    )
    return ConversationHandler.END





async def preorder_cancel(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END