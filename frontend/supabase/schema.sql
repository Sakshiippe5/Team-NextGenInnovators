-- Run this in Supabase: SQL Editor → New query → Paste → Run.
-- Matches Drizzle schema in src/db/schema.ts (Postgres, quoted identifiers).

-- Enum for roadmap visibility
DO $$ BEGIN
  CREATE TYPE "Visibility" AS ENUM ('PRIVATE', 'PUBLIC');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Users (Clerk user id = primary key)
CREATE TABLE IF NOT EXISTS "User" (
  "id" text PRIMARY KEY,
  "name" text NOT NULL,
  "email" text NOT NULL,
  "imageUrl" text,
  "credits" integer NOT NULL DEFAULT 5
);

CREATE UNIQUE INDEX IF NOT EXISTS "User_id_key" ON "User" ("id");

-- Roadmaps
CREATE TABLE IF NOT EXISTS "roadmap" (
  "id" text PRIMARY KEY,
  "title" text NOT NULL,
  "content" text NOT NULL,
  "userId" text NOT NULL REFERENCES "User" ("id") ON DELETE CASCADE,
  "createdAt" timestamp NOT NULL DEFAULT now(),
  "views" integer NOT NULL DEFAULT 0,
  "searchCount" integer NOT NULL DEFAULT 0,
  "visibility" "Visibility" NOT NULL DEFAULT 'PUBLIC'
);

CREATE UNIQUE INDEX IF NOT EXISTS "roadmap_title_key" ON "roadmap" ("title");
CREATE INDEX IF NOT EXISTS "Roadmap_title_idx" ON "roadmap" ("title");

-- Saved roadmaps (bookmark-style rows)
CREATE TABLE IF NOT EXISTS "SavedRoadmap" (
  "id" text PRIMARY KEY,
  "title" text NOT NULL,
  "roadmapId" text NOT NULL,
  "userId" text NOT NULL REFERENCES "User" ("id") ON DELETE CASCADE
);

-- Drawer / node detail cache per roadmap
CREATE TABLE IF NOT EXISTS "DrawerDetail" (
  "id" text PRIMARY KEY,
  "details" text NOT NULL,
  "youtubeVideoIds" text[] NOT NULL,
  "books" text NOT NULL,
  "nodeName" text NOT NULL,
  "roadmapId" text NOT NULL REFERENCES "roadmap" ("id") ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "DrawerDetail_nodeName_key" ON "DrawerDetail" ("nodeName");

-- Optional: let the Postgres role used by DATABASE_URL insert/update.
-- If you use RLS later, add policies; for server-side pooler connection this is usually enough.
