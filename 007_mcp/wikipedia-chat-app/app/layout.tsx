import "./globals.css"
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Wikipedia Research Assistant',
  description: 'AI-powered Wikipedia research tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
