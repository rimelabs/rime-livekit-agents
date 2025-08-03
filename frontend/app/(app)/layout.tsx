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
      {/* */}
      {children}
    </>
  );
}
