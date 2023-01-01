import random
import jaconv
import textwrap
import random
from typing import Iterable, List, Union
from telegram.constants import MAX_MESSAGE_LENGTH
from peewee import fn

import config
import shiritori
from db import Chat, Word, Game, Play, ImageCache, UnknownWord

from telegram.ext.filters import Filters, MessageFilter
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.defaults import Defaults
from telegram.ext import CommandHandler, Updater
from telegram.message import Message
from telegram.update import Update
from telegram import ParseMode

ellipsis = type(...)


error_messages = {
    "n": [
        "「ん」じゃダメよ！",
        "ブーブー❌「ん」で終わっちゃダメですよ～",
    ],
    "initial": [
        "「{0}」じゃなくて、「{1}」だ。",
        "「{0}」からじゃなくて「{1}」なの！",
    ],
    "length": [
        "{0} 文字じゃだめ、{1} が欲しいんだ。",
        "{0} 文字なんてルール違反ですよん～ {1} 文字にしてくださいな",
    ],
    "unknown": [
        "「{0}」なんて聞いたことない！",
        "「{0}」なんて初耳です",
        "「{0}」ってなーに？知らなかった",
        "「{0}」私は日本語食べません",
        "「{0}」ぐぬぬ……語彙量が",
    ],
    "used_up": [
        "「{0}}」はどれでももう使われた！",
        "「{0}」もう使いきったよ～",
        "「{0}」はいはい～既出乙",
    ],
}


def choose_random_message(key, *args):
    return random.choice(error_messages[key]).format(*args)


def paginate_text(text: str) -> Iterable[str]:
    if len(text) < MAX_MESSAGE_LENGTH:
        return [text]

    page_length = MAX_MESSAGE_LENGTH - 10
    parts = [text[i:i + page_length] for i in range(0, len(text), page_length)]
    # we are reserving 8 characters for adding the page number in
    # the following format: [01/10]

    parts = [f"[{i + 1}/{len(parts)}]\n{part}" for i, part in enumerate(parts)]
    return parts


def build_history_message(count: int, plays: List[Union["Play", ellipsis]]) -> str:
    index = 1
    message = ""
    for play in plays:
        if play is ...:
            message += f"... →\n"
            index = count - 2
        else:
            word_rep = f"{play.word.word} [{play.word.lemma}]"
            if play.word.word == jaconv.kata2hira(play.word.lemma):
                word_rep = play.word.lemma
            message += f"{index}: {word_rep} →\n"
            index += 1
    return message[:-3]


def build_game_status_message(game: Game) -> str:
    plays = game.get_recent_plays()
    next_char = shiritori.get_last_char(plays[-1].word.word)
    length = game.next_length
    if length == 8:
        length = "8+"
    count = game.plays.count()
    message = build_history_message(count, plays)
    message += f"\n\n<b>{next_char} ({length})</b>"
    return message


def send_status_message(update: Update, game: Game, prefix: str = ""):
    text = build_game_status_message(game)
    length = game.next_length
    next_char = shiritori.get_last_char(game.get_last_play().word.word)
    file_name = f"{next_char}_{length}.webp"
    cache = ImageCache.get_or_none(file_name=file_name)
    text = prefix + "\n" + text
    msg = update.effective_message
    if game.send_sticker:
        if cache:
            msg = msg.reply_sticker(
                sticker=cache.file_id,
            )
        else:
            with open("./cards/" + file_name, "rb") as f:
                msg = msg.reply_sticker(
                    sticker=f,
                )
            ImageCache.create(file_name=file_name, file_id=msg.sticker.file_id)

    msg.reply_text(text=text, quote=False)

    if game.send_sticker:
        if game.last_sticker_id:
            try:
                msg.bot.delete_message(
                    chat_id=msg.chat_id,
                    message_id=game.last_sticker_id
                )
            except:
                pass

        game.last_sticker_id = msg.message_id
        game.save()


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat: Chat = Chat.get_or_create(chat_id=chat_id)[0]
    game = chat.new_game()
    send_status_message(update, game, prefix=f"新しいゲームを始めます！ No. {game.id}")


def clear(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    chat: Chat = Chat.get_or_create(chat_id=chat_id)[0]
    game = chat.game
    if game:
        # A game is running
        chat.game = None
        chat.save()
        count = game.plays.count()
        update.message.reply_text(
            f"<b>ゲームセット！</b>\n\n"
            f"ただいま、ゲーム No. {game.id} は終了しました。"
            f"計 {count} 個の単語が使われました。",
        )
        context.bot.send_message(
            update.effective_chat.id,
            build_history_message(count, game.plays)
        )


def unknown(update: Update, context: CallbackContext):
    words: Iterable[UnknownWord] = UnknownWord.select().order_by(UnknownWord.times.desc()).limit(10).execute()
    update.effective_message.reply_text(
        "最も使われた未登録単語（10 コまで）：\n" +
        "\n".join(f"{word.word} ({word.times})" for word in words)
    )


def play(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat: Chat = Chat.get_or_none(chat_id=chat_id)
    if not chat:
        return
    game = chat.game
    if not game:
        return

    last_play = game.get_last_play()
    next_initial = shiritori.get_last_char(last_play.word.word)
    next_length = game.next_length

    curr_word = shiritori.preprocess_input(update.message.text)
    curr_question = f"{next_initial} {'8+' if next_length == 8 else next_length}"

    if shiritori.get_last_char(curr_word).endswith("ん"):
        error = choose_random_message("n")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>{error}</b>\n\n再試行：\n{curr_question}",
            reply_to_message_id=update.message.message_id
        )
    elif not curr_word.startswith(next_initial):
        error = choose_random_message("initial", curr_word[0], next_initial)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>{error}</b>\n\n再試行：\n{curr_question}",
            reply_to_message_id=update.message.message_id
        )
    elif not (len(curr_word) >= 8 if next_length == 8 else len(curr_word) == next_length):
        error = choose_random_message("length", len(curr_word), next_length)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>{error}</b>\n\n再試行：\n{curr_question}",
            reply_to_message_id=update.message.message_id
        )
    else:
        # Database queries
        try:
            game.play(curr_word)
            next_length = game.next_length
            curr_question = f"{next_initial} {'8+' if next_length == 8 else next_length}"
            send_status_message(update, game, prefix=f"<b>ゲーム No. {game.id}</b>")
        except KeyError:
            UnknownWord.bump_word(curr_word)
            error = choose_random_message("unknown", curr_word)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<b>{error}</b>\n\n再試行：\n{curr_question}",
                reply_to_message_id=update.message.message_id
            )
        except ValueError:
            error = choose_random_message("used_up", curr_word)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<b>{error}</b>\n\n再試行：\n{curr_question}",
                reply_to_message_id=update.message.message_id
            )


def play_with_kanji(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat: Chat = Chat.get_or_none(chat_id=chat_id)
    if not chat:
        return
    game = chat.game
    if not game:
        return

    last_play = game.get_last_play()
    next_initial = shiritori.get_last_char(last_play.word.word)
    next_length = game.next_length

    curr_word = update.message.text
    matching_words = list(Word.select().where(Word.lemma == curr_word))
    random.shuffle(matching_words)
    matching_words = [
        word for word in matching_words
        if 
        not shiritori.get_last_char(word.word).endswith("ん") and
        word.word.startswith(next_initial) and
        (len(word.word) >= 8 if next_length == 8 else len(word.word) == next_length)
    ]
    try:
        game.play_word_objects(matching_words)
        next_length = game.next_length
        curr_question = f"{next_initial} {'8+' if next_length == 8 else next_length}"
        send_status_message(update, game, prefix=f"<b>ゲーム No. {game.id}</b>")
    except KeyError:
        pass
    except ValueError:
        pass


def history(update: Update, context: CallbackContext):
    args = update.effective_message.text.split()[1:]
    if args and args[0].isdigit():
        game_id = int(args[0])
        game = Game.get_or_none(id=game_id)
        if not game:
            update.effective_message.reply_text(f"ゲーム No. {game_id} が見つかりませんでした。")
            return
        history_rows = game.plays.select(Play, Word).join(Word).order_by(Play.id).execute()
        history = build_history_message(len(history_rows), history_rows)
        for page in paginate_text(f"<b>ゲーム No. {game.id}</b>\n\n" + history):
            update.effective_message.reply_text(page)
    else:
        chat_id = update.effective_message.chat_id
        chat: Chat = Chat.get_or_none(chat_id=chat_id)
        if not chat:
            update.effective_message.reply_text("まだゲーム始まってないよ！")
            return
        game = chat.game
        if not game:
            update.effective_message.reply_text("まだゲーム始まってないよ！")
            return

        history_rows = game.plays.select(Play, Word).join(Word).order_by(Play.id).execute()
        history = build_history_message(len(history_rows), history_rows)
        for page in paginate_text(f"<b>ゲーム No. {game.id}</b>\n\n" + history):
            update.effective_message.reply_text(page)


def stats(update: Update, context: CallbackContext):
    total_words = Word.select().count()
    total_plays = Play.select().count()
    total_games = Game.select().count()

    heads = [i for i in Word.group_by_head() if shiritori.kana_only(i[1])]
    tails = [i for i in Word.group_by_tail() if shiritori.kana_only(i[1])]

    heads_rank = (
        "\n".join(f"{i[1]} ({i[0]})" for i in heads[:10]) + 
        "\n...\n" + 
        "\n".join(f"{i[1]} ({i[0]})" for i in heads[-10:]) 
    )
    tails_rank = (
        "\n".join(f"{i[1]} ({i[0]})" for i in tails[:10]) +
        "\n...\n" +
        "\n".join(f"{i[1]} ({i[0]})" for i in tails[-10:])
    
    )
    
    lengths = Word.group_by_length()
    length8 = sum(v for l, v in lengths if l >= 8)
    lengths_table = "\n".join(
        f"{l}: {v}" for l, v in lengths if 2 <= l < 8
    ) + f"\n8+: {length8}"

    message = (
        f"総単語数：{total_words}\n"
        f"総ゲーム数：{total_games}\n"
        f"総プレイ数：{total_plays}\n\n"
        f"長さ別の単語数：\n{lengths_table}\n\n"
        f"始まるカナランキング：\n{heads_rank}\n\n"
        f"終わるカナランキング：\n{tails_rank}"
    )

    update.effective_message.reply_text(message)


def sticker(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat: Chat = Chat.get_or_none(chat_id=chat_id)
    if not chat:
        update.effective_message.reply_text("まだゲーム始まってないよ！")
    game = chat.game
    if not game:
        update.effective_message.reply_text("まだゲーム始まってないよ！")
    game.send_sticker = not game.send_sticker
    game.save()
    if game.send_sticker:
        update.effective_message.reply_text("このゲームで、これからはカートを送るようになります。")
    else:
        update.effective_message.reply_text("このゲームで、これからはカートを送らないようになります。")
    
def lookup(update: Update, context: CallbackContext):
    query = ' '.join(update.effective_message.text.split()[1:])
    words = Word.select().where((Word.word == jaconv.kata2hira(query)) | (Word.lemma == query)) \
        .limit(100)
    
    text = "\n".join(f"{i.word} [{i.lemma}]" for i in words) or "[]"
    update.effective_message.reply_text(text)


def help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(textwrap.dedent("""
        /start - ゲームを始める
        /clear - ゲームを終了する
        /unknown - 使われた未登録単語ランキングを表示する
        /history - 履歴を表示する
        /stats - 統計を表示する
        /sticker - カートを送るかどうかを切り替える
        /help - このメッセージを表示する
        """
    ))


class ReplyToBot(MessageFilter):
    __slots__ = ()
    name = 'Filters.ReplyToBot'
    bot_id: int

    def __init__(self, bot_id: int) -> None:
        super().__init__()
        self.bot_id = bot_id

    def filter(self, message: Message) -> bool:
        return bool(message.reply_to_message.from_user.id == self.bot_id)


def run(updater: Updater):
    if config.WEBHOOK_URL:
        url = config.WEBHOOK_URL
        port = 8000

        print(f'Setting up webhook to {url} and port {port}...')
        updater.start_webhook(
            webhook_url=url,
            listen="0.0.0.0",
            port=port
        )
        print(f'Listening on port {port}...')
    else:
        updater.start_polling()


def main():
    updater = Updater(
        defaults=Defaults(parse_mode=ParseMode.HTML,
                          disable_notification=True,
                          disable_web_page_preview=True),
        token=config.TELEGRAM_BOT_TOKEN
    )
    dispatcher = updater.dispatcher
    bot_user = updater.bot.get_me()

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("clear", clear))
    dispatcher.add_handler(CommandHandler("unknown", unknown))
    dispatcher.add_handler(CommandHandler("history", history))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("sticker", sticker))
    dispatcher.add_handler(CommandHandler("lookup", lookup))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(
        Filters.text &
        ~ Filters.update.edited_message &
        Filters.regex(shiritori.kana_pattern) &
        (~ Filters.reply | ReplyToBot(bot_user.id)),
        play))
    dispatcher.add_handler(MessageHandler(
        Filters.text &
        ~ Filters.update.edited_message &
        (~ Filters.reply | ReplyToBot(bot_user.id)),
        play_with_kanji))

    run(updater)


if __name__ == "__main__":
    main()
