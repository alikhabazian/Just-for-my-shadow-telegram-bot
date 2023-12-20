from constant import *
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, CallbackQueryHandler, PicklePersistence
from functions import *

# TODO cleaning code
load_dotenv()
BOTTOKEN = os.getenv("BOTTOKEN")


if __name__ == "__main__":
    persistence = PicklePersistence(filepath="conversationbot")
    application = ApplicationBuilder().token(BOTTOKEN).arbitrary_callback_data(
        True).persistence(persistence).build()
    mainCommandHandler = CommandHandler("start", start)
    preorderConversationHandler = ConversationHandler(
        entry_points=[CommandHandler("preorder", preorderChoose)],
        states={
            PREORDER_CHOOSE: [
                CallbackQueryHandler(waitingRecipt, pattern='^Rial$|^Paypal$'),
                # CallbackQueryHandler(waitingRecipt,pattern='^Paypal$'),
                # MessageHandler(filters=filters.Regex(r'^[\s\S]*$'), user_charge_acc_inputed),
            ],
            PREORDER_STATE: [
                MessageHandler(filters=filters.COMMAND,
                               callback=preorder_wrong_inputed),
                MessageHandler(filters=filters.Regex(
                    r'^[\s\S]*$'), callback=userTextRecipt),
                MessageHandler(filters=filters.PHOTO,
                               callback=userImageRecipt),
                MessageHandler(filters=filters.Document.ALL,
                               callback=userDocRecipt),
            ],
        },
        fallbacks=[CommandHandler("cancel", preorder_cancel), CallbackQueryHandler(
            preorder_cancel, pattern='^Cancel$')],
    )
    acceptQueryHandler = CallbackQueryHandler(
        acceptHandeling, pattern='^Accept$')
    rejectQueryHandler = CallbackQueryHandler(
        rejectHandeling, pattern='^Reject$')

    application.add_handler(mainCommandHandler)
    application.add_handler(preorderConversationHandler)
    application.add_handler(acceptQueryHandler)
    application.add_handler(rejectQueryHandler)
    application.run_polling()
