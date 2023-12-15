from constant import *
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext,CallbackQueryHandler
from functions import *

# TODO cleaning code
load_dotenv()
BOT_TOKEN= os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    mainCommandHandler=CommandHandler("start", start)
    preorderConversationHandler=ConversationHandler(
        entry_points=[CommandHandler("preorder", preorderChoose)],
        states={
            PREORDER_CHOOSE:[
                CallbackQueryHandler(waitingRecipt,pattern='^Rial$'),
                CallbackQueryHandler(waitingRecipt,pattern='^Paypal$'),
                # MessageHandler(filters=filters.Regex(r'^[\s\S]*$'), user_charge_acc_inputed),
            ],
            PREORDER_STATE: [
                MessageHandler(filters=filters.Regex(r'^[\s\S]*$'), callback=userTextRecipt),
                MessageHandler(filters=filters.PHOTO, callback=userImageRecipt),
                MessageHandler(filters=filters.Document.ALL, callback=userDocRecipt),
            ],
        },
        fallbacks=[CommandHandler("cancel", preorder_cancel)],
    )
    acceptQueryHandler = CallbackQueryHandler(acceptHandeling,pattern='^Accept$')
    rejectQueryHandler = CallbackQueryHandler(acceptHandeling,pattern='^Reject$')


    application.add_handler(mainCommandHandler)
    application.add_handler(preorderConversationHandler)
    application.add_handler(acceptQueryHandler)
    application.add_handler(rejectQueryHandler)
    application.run_polling()
