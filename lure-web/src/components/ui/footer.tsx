import { Box, Text } from "@radix-ui/themes";
import Link from "next/link";

export function Footer() {
  return (
    <Box className="w-full border-t border-border/20 py-3.5 px-4 bg-background/30 backdrop-blur-md">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <Text size="1" color="gray">
          © {new Date().getFullYear()} Tempt. All rights reserved.
        </Text>
        <div className="flex items-center gap-4">
          <Text asChild size="1" color="gray">
            <Link
              href="/privacy"
              className="hover:text-foreground transition-colors"
            >
              Privacy Policy
            </Link>
          </Text>
          <Text asChild size="1" color="gray">
            <Link
              href="/terms"
              className="hover:text-foreground transition-colors"
            >
              Terms of Service
            </Link>
          </Text>
        </div>
      </div>
    </Box>
  );
}
