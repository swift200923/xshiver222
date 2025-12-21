import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Xshiver – Video Explorer",
  description: "Minimal video discovery site with search and categories."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-50 antialiased">
        {children}
      </body>
    </html>
  );
}
