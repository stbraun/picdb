

-- Database: mypics

-- DROP DATABASE mypics;

CREATE DATABASE mypics
WITH OWNER = postgres
ENCODING = 'UTF8'
TABLESPACE = pg_default
LC_COLLATE = 'C'
LC_CTYPE = 'C'
CONNECTION LIMIT = -1;


-- Sequence: public.groups_id_seq

-- DROP SEQUENCE public.groups_id_seq;

CREATE SEQUENCE public.groups_id_seq
INCREMENT 1
MINVALUE 1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER TABLE public.groups_id_seq
  OWNER TO sb;

-- Sequence: public.pictures_id_seq

-- DROP SEQUENCE public.pictures_id_seq;

CREATE SEQUENCE public.pictures_id_seq
INCREMENT 1
MINVALUE 1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER TABLE public.pictures_id_seq
  OWNER TO sb;

-- Sequence: public.tags_id_seq

-- DROP SEQUENCE public.tags_id_seq;

CREATE SEQUENCE public.tags_id_seq
INCREMENT 1
MINVALUE 1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER TABLE public.tags_id_seq
  OWNER TO sb;


-- Table: public.tags

-- DROP TABLE public.tags;

CREATE TABLE public.tags
(
  id integer NOT NULL DEFAULT nextval('tags_id_seq'::regclass),
  identifier text NOT NULL,
  description text,
  parent integer,
  CONSTRAINT tags_primary_key PRIMARY KEY (id),
  CONSTRAINT tags_parent FOREIGN KEY (parent)
  REFERENCES public.groups (id) MATCH SIMPLE
  ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT tags_uq UNIQUE (identifier, parent)
)
  WITH (
  OIDS=FALSE
);
ALTER TABLE public.tags
OWNER TO sb;


-- Table: public.pictures

-- DROP TABLE public.pictures;

CREATE TABLE public.pictures
(
  id integer NOT NULL DEFAULT nextval('pictures_id_seq'::regclass),
  description text,
  identifier text NOT NULL,
  path text NOT NULL,
  CONSTRAINT pictures_primary_key PRIMARY KEY (id),
  CONSTRAINT pictures_uq UNIQUE (path)
)
  WITH (
  OIDS=FALSE
);
ALTER TABLE public.pictures
OWNER TO sb;


-- Table: public.groups

-- DROP TABLE public.groups;

CREATE TABLE public.groups
(
  id integer NOT NULL DEFAULT nextval('groups_id_seq'::regclass),
  identifier text NOT NULL,
  description text,
  parent integer,
  CONSTRAINT groups_primary_key PRIMARY KEY (id),
  CONSTRAINT groups_parent FOREIGN KEY (parent)
  REFERENCES public.groups (id) MATCH SIMPLE
  ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT groups_uq UNIQUE (identifier, parent)
)
  WITH (
  OIDS=FALSE
);
ALTER TABLE public.groups
OWNER TO sb;


-- Table: public.picture2group

-- DROP TABLE public.picture2group;

CREATE TABLE public.picture2group
(
  picture integer NOT NULL,
  "group" integer NOT NULL,
  CONSTRAINT p2g_primary_key PRIMARY KEY (picture, "group")
)
  WITH (
  OIDS=FALSE
);
ALTER TABLE public.picture2group
OWNER TO sb;


-- Table: public.picture2tag

-- DROP TABLE public.picture2tag;

CREATE TABLE public.picture2tag
(
  picture integer NOT NULL,
  tag integer NOT NULL,
  CONSTRAINT p2t_primary_key PRIMARY KEY (picture, tag)
)
  WITH (
  OIDS=FALSE
);
ALTER TABLE public.picture2tag
OWNER TO sb;
