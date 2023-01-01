from typing import List, Optional, Text, Type, Union
import config
import random
import shiritori
from peewee import BooleanField, ForeignKeyField, IntegerField, ModelSelect, PostgresqlDatabase, Model, TextField, fn

ellipsis = type(...)

db = PostgresqlDatabase(
    config.DATABASE_NAME,
    user=config.DATABASE_USER,
    password=config.DATABASE_PASSWORD,
    host=config.DATABASE_HOST,
    port=config.DATABASE_PORT,
)

class BaseModel(Model):
    class Meta:
        database = db


class Word(BaseModel):
    lemma = TextField()
    word = TextField(index=True)

    plays: ModelSelect

    class Meta:
        table_name = "words"
        indexes = (
            (('lemma', 'word'), True),
        )

    @classmethod
    def get_random_word(cls):
        count = cls.select().count()
        offset = random.randint(0, count)
        return cls.select().offset(offset).limit(1)[0]

    @classmethod
    def group_by_length(cls):
        l = Word.select(
            fn.length(Word.word).alias("length"), 
            fn.Count(1).alias("times")
        ).group_by(fn.length(Word.word)).execute()
        return sorted((int(x.length), x.times) for x in l)

    @classmethod
    def group_by_head(cls):
        l = Word.select(
            fn.left(Word.word, 1).alias("word"), 
            fn.Count(1).alias("times")
        ).group_by(fn.left(Word.word, 1)).execute()
        return sorted((x.times, x.word) for x in l)

    @classmethod
    def group_by_tail(cls):
        l = Word.select(
            fn.right(Word.word, 1).alias("word"), 
            fn.Count(1).alias("times")
        ).group_by(fn.right(Word.word, 1)).execute()
        return sorted((x.times, x.word) for x in l)


class Game(BaseModel):
    next_length = IntegerField()
    last_sticker_id = IntegerField(null=True)
    send_sticker = BooleanField(default=True)

    plays: ModelSelect
    _last_play: Optional["Play"] = None

    class Meta:
        table_name = "games"

    def get_recent_plays(self) -> List[Union["Play", ellipsis]]:
        count = self.plays.count()
        if count <= 3:
            return self.plays.select(Play, Word).join(Word).order_by(Play.id.desc()).limit(3)[::-1]
        elif count == 4:
            return self.plays.select(Play, Word).join(Word).order_by(Play.id.desc()).limit(4)[::-1]
        else:
            first = self.plays.select(Play, Word).join(Word).first()
            last3 = self.plays.select(Play, Word).join(Word).order_by(Play.id.desc()).limit(3)[::-1]
            return [first, ...] + last3

    def get_last_play(self) -> "Play":
        if self._last_play is None:
            self._last_play = self.plays.order_by(Play.id.desc()).limit(1)[0]
        return self._last_play

    def play(self, word: str):
        words = list(Word.select().where(Word.word == word))
        if not words:
            raise KeyError(f"{word} is not in the dictionary.")
        self.play_word_objects(words)

    def play_word_objects(self, words: List[Word]):
        random.shuffle(words)
        w = None
        for word in words:
            if self.plays.where(Play.word_id == word.id).count() == 0:
                w = word
                break

        if w is None:
            raise ValueError(f"{words and words[0].word} has already been played.")
        
        self.next_length = shiritori.random_length()
        self.save()

        play = Play.create(word=word, game=self)
        self._last_play = play


class Chat(BaseModel):
    chat_id = IntegerField(index=True, primary_key=True)
    game = ForeignKeyField(Game, backref='chats', on_delete='SET NULL', on_update='CASCADE', null=True)

    class Meta:
        table_name = "chats"

    def new_game(self) -> Game:
        game = Game.create(next_length=shiritori.random_length())
        self.game = game
        self.save()
        word = Word.get_random_word()
        Play.create(word=word, game=game)
        return game


class Play(BaseModel):
    game = ForeignKeyField(Game, backref='plays', on_delete='CASCADE', on_update='CASCADE')
    word = ForeignKeyField(Word, backref='plays', on_delete='CASCADE', on_update='CASCADE')

    chats: ModelSelect

    class Meta:
        table_name = "plays"
        indexes = (
            (('game', 'id'), False),
            (('game', 'word'), True),
        )


class ImageCache(BaseModel):
    file_name = TextField(primary_key=True)
    file_id = TextField()


class UnknownWord(BaseModel):
    word = TextField(primary_key=True)
    times = IntegerField(default=0)

    @classmethod
    def bump_word(cls, word: str):
        entry = cls.get_or_create(word=word)[0]
        entry.times += 1
        entry.save()
