'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/app/utils/cn';

const navigation = [
  { name: 'ダッシュボード', href: '/' },
  { name: 'セッション管理', href: '/sessions' },
  { name: '音声録音', href: '/recording' },
  { name: '音声アップロード', href: '/upload' },
  { name: '設定', href: '/settings' },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="bg-white shadow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between">
          <div className="flex">
            <div className="flex flex-shrink-0 items-center">
              <h1 className="text-xl font-bold text-gray-900">
                カウンセリング支援ツール
              </h1>
            </div>
            <nav className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    pathname === item.href
                      ? 'border-indigo-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                    'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium'
                  )}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
}