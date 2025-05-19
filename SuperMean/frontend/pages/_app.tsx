import '../styles/globals.css';
import type { AppProps } from 'next/app';
import Navbar from '../components/Navbar';
import ThemeSwitcher from '../components/ThemeSwitcher';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Navbar />
      <div className="fixed top-4 right-4 z-50">
        <ThemeSwitcher />
      </div>
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;
