import NavItems from "@/components/app/nav-items";
import { Badge } from "@/components/ui/badge";
import { SignInButton, UserButton } from "@clerk/nextjs";
import { currentUser } from "@clerk/nextjs/server";
import { Coins } from "lucide-react";
import { Link } from "next-view-transitions";

import { getUserCredits } from "@/actions/users";
import { isClerkConfigured } from "@/lib/clerk-config";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import MobileDrawer from "@/components/app/mobile-drawer";
import NeobrutalismButton from "@/components/ui/neobrutalism-button";

async function AppBar() {
  if (!isClerkConfigured()) {
    return (
      <div className="mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center gap-2 p-2">
          <Link href="/">
            <NeobrutalismButton>
              <span className="text-lg font-bold">RoadmapAI</span>
            </NeobrutalismButton>
          </Link>
          <NavItems />
          <p className="ml-auto max-w-[min(100%,22rem)] text-xs text-muted-foreground sm:text-sm">
            Set{" "}
            <code className="rounded bg-muted px-1">NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>{" "}
            and <code className="rounded bg-muted px-1">CLERK_SECRET_KEY</code> for
            sign-in.
          </p>
        </div>
      </div>
    );
  }

  const user = await currentUser();
  const userCredits = await getUserCredits();

  if (!user) {
    return (
      <div className="mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="p-2 flex gap-2 items-center">
          <Link href="/">
            <NeobrutalismButton>
              <span className="font-bold text-lg">RoadmapAI</span>
            </NeobrutalismButton>
          </Link>
          <div className="ml-auto items-center">
            <SignInButton mode="modal">
              <NeobrutalismButton>
                <span className="font-medium">Sign in</span>
              </NeobrutalismButton>
            </SignInButton>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div className="p-2 flex gap-2 items-center">
        <span className="md:hidden ml-2">
          <MobileDrawer />
        </span>
        <Link href="/">
          <NeobrutalismButton>
            <span className="font-semibold text-lg">RoadmapAI</span>
          </NeobrutalismButton>
        </Link>
        <NavItems />
        <div className="ml-auto flex items-center">
          <div className="flex gap-2 items-center">
            <div className="gap-2">
              <TooltipProvider>
                <Tooltip delayDuration={250}>
                  <TooltipTrigger asChild>
                    <Badge
                      className="cursor-default"
                      variant={
                        userCredits && userCredits > 0
                          ? "outline"
                          : "destructive"
                      }
                    >
                      {userCredits} <Coins size={16} />
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>Credits Remaining</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
        </div>
        <span>
          <UserButton />
        </span>
      </div>
    </div>
  );
}

export default AppBar;
