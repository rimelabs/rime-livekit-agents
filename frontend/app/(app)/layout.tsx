import { headers } from 'next/headers';
import Image from 'next/image';
import { getAppConfig } from '@/lib/utils';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default async function AppLayout({ children }: AppLayoutProps) {
  const hdrs = await headers();
  const { companyName, logo, logoDark } = await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row justify-between p-6 md:flex">
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://livekit.io"
          className="scale-100 transition-transform duration-300 hover:scale-110"
        >
          <Image
            width={100}
            height={100}
            src={logo}
            alt={`${companyName} Logo`}
            className="block0 dark:hidden"
          />
          <Image
            width={140}
            height={140}
            src={logoDark ?? logo}
            alt={`${companyName} Logo`}
            className="hidden h-6 dark:block"
          />
        </a>
      </header>
      {children}
    </>
  );
}
