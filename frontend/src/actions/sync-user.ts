"use server";

import { currentUser } from "@clerk/nextjs/server";
import { eq } from "drizzle-orm";
import { cache } from "react";
import { db } from "@/lib/db";
import { users } from "@/db/schema";
import { isClerkConfigured } from "@/lib/clerk-config";
import {
  clerkUserToUpsertInput,
  type UpsertAppUserInput,
} from "@/lib/clerk-user-mapper";

/** Clerk `currentUser()` return type for persistence. */
type ClerkUser = NonNullable<Awaited<ReturnType<typeof currentUser>>>;

/** Insert or update `User` by Clerk id. Does not change `credits` on update. */
export async function upsertAppUser(input: UpsertAppUserInput) {
  await db
    .insert(users)
    .values({
      id: input.id,
      name: input.name,
      email: input.email,
      imageUrl: input.imageUrl ?? undefined,
    })
    .onConflictDoUpdate({
      target: users.id,
      set: {
        name: input.name,
        email: input.email,
        imageUrl: input.imageUrl ?? undefined,
      },
    });
}

/** Persist Clerk user to Supabase and return the row. */
export async function persistClerkUser(user: ClerkUser) {
  const input = clerkUserToUpsertInput(user);
  await upsertAppUser(input);
  const row = await db.query.users.findFirst({
    where: eq(users.id, user.id),
  });
  if (!row) {
    throw new Error(`User row missing after upsert: ${user.id}`);
  }
  return row;
}

/**
 * Keeps Postgres `User` in sync with the current Clerk session.
 * Cached once per request via React `cache`.
 */
export const syncClerkUserToDb = cache(async (): Promise<void> => {
  if (!isClerkConfigured()) return;
  if (!process.env.DATABASE_URL?.trim()) return;

  try {
    const user = await currentUser();
    if (!user) return;
    await persistClerkUser(user);
  } catch (e) {
    console.error("syncClerkUserToDb:", e);
  }
});
