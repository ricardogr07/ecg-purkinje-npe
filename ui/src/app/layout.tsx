import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Conduction Lens: Calibrated Identifiability of Purkinje Conduction",
  description:
    "Which Purkinje conduction parameters the surface ECG can and cannot pin down, with calibrated uncertainty. Amortized Neural Posterior Estimation on a public heart mesh.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-indigo-500 focus:text-white focus:rounded-lg focus:text-sm focus:font-semibold"
        >
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
