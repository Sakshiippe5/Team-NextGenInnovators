import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/explore",
  "/starter",
  "/roadmap(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/health",
  "/api/webhook(.*)",
  "/api/og/(.*)",
  "/api/v1/roadmap(.*)",
  "/api/v1/details(.*)",
  "/api/v1/roadmaps(.*)",
  "/api/v1/orilley(.*)",
]);

const clerkAuth = clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export default function middleware(
  ...args: Parameters<typeof clerkAuth>
) {
  if (
    !process.env.CLERK_SECRET_KEY?.trim() ||
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim()
  ) {
    return NextResponse.next();
  }
  return clerkAuth(...args);
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
