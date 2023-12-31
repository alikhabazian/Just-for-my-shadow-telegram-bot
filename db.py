import pymongo
import os
from dotenv import load_dotenv
import gettext

load_dotenv()


# Initialize gettext
def set_lang(locale, file):
    localedir = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'locales')
    translation = gettext.translation(file, localedir=localedir, languages=[locale], fallback=True
                                      #   , codeset='utf-8'
                                      )
    translation.install()
    return translation.gettext


def connect_to_database():
    db_con_string = os.getenv("DBSTRING")
    db_name = os.getenv("DBNAME")
    try:
        db_client = pymongo.MongoClient(db_con_string)
        # logging.info("Connected to the Database")
        return db_client[db_name]
    except Exception as e:
        # logging.error("Error Connecting to the Database!")
        # logging.error(str(e))
        raise e
