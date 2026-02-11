import { Providers } from './providers';
import '../styles/globals.css';

export const metadata = {
  title: 'Beautiful Todo App',
  description: 'A premium, animated todo application with beautiful UI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`antialiased min-h-screen bg-background`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}