--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4 (Debian 13.4-1.pgdg100+1)
-- Dumped by pg_dump version 13.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tsm_system_rows; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS tsm_system_rows WITH SCHEMA public;


--
-- Name: EXTENSION tsm_system_rows; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION tsm_system_rows IS 'TABLESAMPLE method which accepts number of rows as a limit';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chats (
    chat_id bigint NOT NULL,
    game_id bigint
);


ALTER TABLE public.chats OWNER TO postgres;

--
-- Name: games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.games (
    id bigint NOT NULL,
    next_length integer NOT NULL,
    last_sticker_id integer,
    send_sticker boolean DEFAULT true NOT NULL
);


ALTER TABLE public.games OWNER TO postgres;

--
-- Name: games_sampleid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.games_sampleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.games_sampleid_seq OWNER TO postgres;

--
-- Name: games_sampleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.games_sampleid_seq OWNED BY public.games.id;


--
-- Name: imagecache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.imagecache (
    file_name text NOT NULL,
    file_id text NOT NULL
);


ALTER TABLE public.imagecache OWNER TO postgres;

--
-- Name: plays; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plays (
    id bigint NOT NULL,
    game_id bigint NOT NULL,
    word_id bigint NOT NULL
);


ALTER TABLE public.plays OWNER TO postgres;

--
-- Name: plays_sampleid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.plays_sampleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.plays_sampleid_seq OWNER TO postgres;

--
-- Name: plays_sampleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.plays_sampleid_seq OWNED BY public.plays.id;


--
-- Name: unknownword; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.unknownword (
    word text NOT NULL,
    times integer NOT NULL
);


ALTER TABLE public.unknownword OWNER TO postgres;

--
-- Name: words; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.words (
    id bigint NOT NULL,
    lemma text NOT NULL,
    word text NOT NULL
);


ALTER TABLE public.words OWNER TO postgres;

--
-- Name: words_sampleid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.words_sampleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.words_sampleid_seq OWNER TO postgres;

--
-- Name: words_sampleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.words_sampleid_seq OWNED BY public.words.id;


--
-- Name: games id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_sampleid_seq'::regclass);


--
-- Name: plays id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plays ALTER COLUMN id SET DEFAULT nextval('public.plays_sampleid_seq'::regclass);


--
-- Name: words id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.words ALTER COLUMN id SET DEFAULT nextval('public.words_sampleid_seq'::regclass);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (chat_id);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: imagecache imagecache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagecache
    ADD CONSTRAINT imagecache_pkey PRIMARY KEY (file_name);


--
-- Name: plays plays_game_id_word_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plays
    ADD CONSTRAINT plays_game_id_word_id_key UNIQUE (game_id, word_id);


--
-- Name: plays plays_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plays
    ADD CONSTRAINT plays_pkey PRIMARY KEY (id);


--
-- Name: unknownword unknownword_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.unknownword
    ADD CONSTRAINT unknownword_pkey PRIMARY KEY (word);


--
-- Name: words words_lemma_word_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.words
    ADD CONSTRAINT words_lemma_word_key UNIQUE (lemma, word);


--
-- Name: words words_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.words
    ADD CONSTRAINT words_pkey PRIMARY KEY (id);


--
-- Name: plays_game_id_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX plays_game_id_id_index ON public.plays USING btree (game_id, id);


--
-- Name: words_word_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX words_word_index ON public.words USING hash (word);


--
-- Name: chats game_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT game_id FOREIGN KEY (game_id) REFERENCES public.games(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--