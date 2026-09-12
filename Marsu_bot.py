'''
This is bot utilised for Inkubios credits system. 
Bot saves the amount of money user have into csv file after buying treats or adding money.

Token got from BotFather should be saved in config.txt file. The program parses the TOKEN 
automaticly form config.txt file 
'''

import reader_writer
import configparser
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Chat
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

CHOOSE, TREATS, CREDITS, CHECK_USER, LANGUAGE= range(5)


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Choose user language
    '''
    id = update.message.from_user.id
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Choose your languge:",
            reply_markup=main_menu_keyboard(id)
        )
    return LANGUAGE

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message =  update.message.text
    id = update.message.from_user.id
    name = update.message.from_user.first_name

    if message == "suomi":
        reader_writer.set_language(id, "FIN")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Valitsit kielen suomi!",
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=main_menu_text(id).format(name=name),
            reply_markup=main_menu_keyboard(id)
        )
        return CHOOSE
    
    elif message == "English":
        reader_writer.set_language(id, "ENG")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"You chose English!",
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=main_menu_text(id).format(name=name),
            reply_markup=main_menu_keyboard(id)
        )
        return CHOOSE

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Check if user id exists in csv. If not ask password. After correct password,
    check if there is assigned credits for user. Upadate credits it true.
    '''
    message =  update.message.text
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    id = update.message.from_user.id

    config = configparser.ConfigParser()
    config.read('config.txt')
    PASSWORD = config["PASSWORD"]["bot_password"]

    if message == PASSWORD:
        if not reader_writer.add_old_credits(username, id):
            reader_writer.add_user(username, id)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= main_menu_text(id).format(name=name),
            reply_markup=main_menu_keyboard(id)
        )

        return CHOOSE
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Wrong password",
        )
        return ConversationHandler.END


async def awake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Starts the ConversationHandler.
    Returns the state CHOOSE, which activates the function choose
    '''
    name = update.message.from_user.first_name
    id = update.message.from_user.id

    if reader_writer.find_user(id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=main_menu_text(id).format(name=name),
            reply_markup=main_menu_keyboard(id)
        )

        return CHOOSE

    else:
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Password: ",
        )

        return CHECK_USER


async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Function checks if the user is in csv file. If not, user is added into the file.

    The function returns state based on the message sent to bot.
    '''
    message =  update.message.text 
    id = update.message.from_user.id

    if message == "Osta Herkkuja" or message == "Buy Snacks":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=buy_text(id),
            reply_markup=ReplyKeyboardRemove()
        )
        return TREATS

    elif message == "Lisää Rahaa" or message == "Add Money":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=add_text(id),
            reply_markup=ReplyKeyboardRemove()
        )
        return CREDITS

    elif message == "Tarkista Kreditit" or message == "Check Balance":
        amount = reader_writer.check_money(id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=check_text(id).format(amount=amount),
            reply_markup=main_menu_keyboard(id)
        )
    
    elif message == "END":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=sleep_text(id),
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    elif message == "Change Language":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose language:",
            reply_markup=language_keyboard()
        )
        return LANGUAGE

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    If the message is number between 0-20 with or without max 2 decimals (decimal 2 can only be 0 or 5),
    function is called.

    The amount user give is subtracted form their money in csv file. If the money would go negative,
    bot don't allow buying. 
    '''
    message =  update.message.text
    user = update.message.from_user.username
    id = update.message.from_user.id

    amount = reader_writer.use_money(user, id, message)
    if amount < 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= no_money_text(id).format(amount = -1*amount),
            reply_markup=main_menu_keyboard(id)
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= used_amount_text(id).format(message = message, amount = amount),
            reply_markup=main_menu_keyboard(id)
        )
    return CHOOSE

async def add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    If the message is number between 0-20 with or without max 2 decimals (decimal 2 can only be 0 or 5),
    function is called.

    The amount user give is added to their money in csv file.
    '''
    message =  update.message.text
    user = update.message.from_user.username
    id = update.message.from_user.id
    amount = reader_writer.add_money(user, id, message)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text= added_amount_text(id).format(message=message, amount=amount),
        reply_markup=main_menu_keyboard(id)
    )
    return CHOOSE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Function returns the state CHOOSE (main menu) if user send message
    which is not recognised by bot. 
    '''
    id = update.message.from_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = cancel_text(id),
        reply_markup=main_menu_keyboard(id)
    )
    return CHOOSE

async def lang_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Something went wrong. Try again to choose the language.",
        reply_markup=main_menu_keyboard(id)
    )
    return LANGUAGE

##########Messages##########

def menu_text(user_id, text):
    language = reader_writer.read_language(user_id)
    config = configparser.ConfigParser()
    config.read('languages_config.txt')

    if language == "ENG":
        return config['ENG'][text].encode('unicode_escape').decode('unicode_escape')

    return config['FIN'][text].encode('utf-16').decode('utf-16')

def main_menu_text(user_id):
    return menu_text(user_id, 'main_menu')

def buy_text(user_id):
    return menu_text(user_id, 'buy')

def add_text(user_id):
    return menu_text(user_id, 'add')
    
def check_text(user_id):
    return menu_text(user_id, 'check')

def cancel_text(user_id):
    return menu_text(user_id, 'cancel')

def sleep_text(user_id):
    return menu_text(user_id, 'sleep')

def no_money_text(user_id):
    return menu_text(user_id, 'no_money')

def used_amount_text(user_id):
    return menu_text(user_id, 'used_amount')

def added_amount_text(user_id):
    return menu_text(user_id, 'added_amount')


##########Keyboards##########

# The Keybord utlised for commanding the bot
def language_keyboard():
    keyboard = [[KeyboardButton('suomi')],
              [KeyboardButton('English')]]
    return ReplyKeyboardMarkup(keyboard)

def main_menu_keyboard(user_id):
    language = reader_writer.read_language(user_id)
    config = configparser.ConfigParser()
    config.read('languages_config.txt')
    if language == "FIN":
        LANG = "FIN"
    else:
        LANG = "ENG"
    keyboard = [[KeyboardButton(config[LANG]["commands_buy"])],
                [KeyboardButton(config[LANG]["commands_Add"])],
                [KeyboardButton(config[LANG]["commands_check"])],
                [KeyboardButton('Change Language')],
                [KeyboardButton('END')]]
    return ReplyKeyboardMarkup(keyboard)


##########MAIN############

def main():
    # Token got from BotFather should be saved in config.txt file 
    # The program parses the TOKEN automaticly form config.txt file 

    config = configparser.ConfigParser()
    config.read('config.txt')
    TOKEN = config["TOKEN"]["telegram_bot_token"]
    reader_writer.create_csv()

    money_filter = filters.Regex("^(?:([2][0])(?:\.0)?|[1][0-9](?:\.([0-9]|[0-9][0,5]))?|[1-9](?:\.([0-9]|[0-9][0,5]))?|0?\.([0-9]|[0-9][0,5]))$") 
    application = ApplicationBuilder().token(TOKEN).build()

    # Handler for the conversation 
    # Handler is activated with /start command
    # If the message is Osta Herkkuja or Lisää rahaa or Tarkista kreditit or END, then
    # the choose-function is called
    #
    # If END is called, the conversationHander is closed
    

    conv_handler = ConversationHandler( entry_points= [CommandHandler('start', awake)],
                                        states={CHOOSE: [MessageHandler(filters.Regex("^(Osta Herkkuja|Lisää Rahaa|Tarkista Kreditit|Change Language|END|Buy Snacks|Add Money|Check Balance)$"), choose)],
                                                TREATS: [MessageHandler(money_filter, buy)],
                                                CREDITS: [MessageHandler(money_filter, add_credits)],
                                                CHECK_USER: [MessageHandler(filters.TEXT, check_user)],
                                                LANGUAGE: [MessageHandler(filters.Regex("^(suomi|English)$"), change_language)]
                                        },
                                        fallbacks= [MessageHandler(filters.TEXT, cancel)]
                                    )   
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()