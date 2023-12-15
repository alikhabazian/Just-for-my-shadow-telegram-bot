from constant import *
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext,CallbackQueryHandler
from dotenv import load_dotenv
from functions import *

load_dotenv()
BOT_TOKEN=bot_token = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    mainCommandHandler=CommandHandler("start", start)
    preorederConversationHandler=ConversationHandler(
        entry_points=[CommandHandler("preorder", preorderChoose)],
        states={
            PREORDER_CHOOSE:[
                CallbackQueryHandler(waitingRecipt,pattern='^Rial$'),
                CallbackQueryHandler(waitingRecipt,pattern='^Paypal'),
                # MessageHandler(filters=filters.Regex(r'^[\s\S]*$'), user_charge_acc_inputed),
            ],
            PREORDER_STATE: [
                MessageHandler(filters=filters.Regex(r'^[\s\S]*$'), callback=userTextRecipt),
                # MessageHandler(filters=filters.PHOTO, callback=userImageRecipt),
                # MessageHandler(filters=filters.Document.ALL, userDocRecipt),
            ],
        },
        fallbacks=[CommandHandler("cancel", preorder_cancel)],
    )
    application.add_handler(mainCommandHandler)
    application.add_handler(preorederConversationHandler)
    application.run_polling()
