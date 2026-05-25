import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Berkeley Transfer Search",
  description: "Search Berkeley course articulation agreements by community college.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
