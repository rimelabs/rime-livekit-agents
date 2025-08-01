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
          href="https://www.rime.ai/"
          className="scale-100 transition-transform duration-300 hover:scale-110"
        >
          <Image
            width={90}
            height={90}
            src={logo}
            alt={`${companyName} Logo`}
            className="block h-auto max-h-[30px] w-auto dark:hidden"
          />
          <Image
            width={90}
            height={90}
            src={logoDark ?? logo}
            alt={`${companyName} Logo`}
            className="hidden h-auto max-h-[32px] w-auto dark:block"
          />
        </a>
      </header>
      {children}
    </>
  );
}
