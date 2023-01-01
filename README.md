# Database-based Genkai Shiritori Bot on Telegram

A Genkai Shiritori bot on Telegram, using PostgreSQL as database, based on the work of mkpoli.

## Config

`bot.env`:

```env
TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKabcdefghijk12345678"
DATABASE_PASSWORD="imadake398yen"
# Optional, if you want to setup webhook
WEBHOOK_URL="https://example.com/shiritori_bot/1234567890:ABCDEFGHIJKabcdefghijk12345678"
```

`database.env`:

```env
POSTGRES_PASSWORD="imadake398yen"
```


## Start

Download dictionary file from releases to `./dicts/`.

```sh
# Start the bot
docker-compose up -d
# Setup dictionary, only need to run once
docker-compose exec bot sh populate_words.sh
```

## Add words

### CSV

**Requirement:** first row must be `word,lemma` or `lemma,word`, where `word` is the word in hiragana, and `lemma` is the word in its proper form.

1. Copy the file to `./dicts/`
2. Run `docker-compose exec bot python3 add_words.py -c ./dicts/your_file.csv`

### Manually

Run `docker-compose exec bot python3 add_words.py -w LEMMA WORD -w LEMMA WORD`.
