import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FluentMeet AI — Enterprise Meeting English Coaching",
  description: "Real-time speech analysis, grammar correction, and fluency coaching for international remote professionals.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-blue-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}

