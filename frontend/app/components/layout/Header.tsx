'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/app/utils/cn';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Home,
  FileText,
  Upload,
  Menu,
  ChevronDown,
  Zap,
  Target,
  Mic
} from 'lucide-react';

const navigation = [
  {
    name: 'ホーム',
    href: '/',
    icon: Home,
  },
  {
    name: 'データ管理',
    icon: Upload,
    children: [
      { name: 'アップロード', href: '/upload', icon: Upload },
      { name: '録音', href: '/recording', icon: Mic },
      { name: 'ラベリング', href: '/labeling', icon: Target },
    ],
  },
  {
    name: 'スクリプト',
    icon: FileText,
    children: [
      { name: 'スクリプト生成', href: '/scripts/generate', icon: Zap },
      { name: 'スクリプト一覧', href: '/scripts', icon: FileText },
    ],
  },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActivePath = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  const NavItem = ({ item }: { item: typeof navigation[0] }) => {
    if (item.children) {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="ghost" 
              className={cn(
                'flex items-center space-x-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100',
                item.children.some(child => isActivePath(child.href)) && 'text-blue-600 bg-blue-50'
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.name}</span>
              <ChevronDown className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            {item.children.map((child) => (
              <DropdownMenuItem key={child.href} asChild>
                <Link 
                  href={child.href}
                  className={cn(
                    'flex items-center space-x-2 w-full',
                    isActivePath(child.href) && 'bg-blue-50 text-blue-600'
                  )}
                >
                  <child.icon className="h-4 w-4" />
                  <span>{child.name}</span>
                </Link>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      );
    }

    return (
      <Link href={item.href}>
        <Button 
          variant="ghost" 
          className={cn(
            'flex items-center space-x-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100',
            isActivePath(item.href) && 'text-blue-600 bg-blue-50'
          )}
        >
          <item.icon className="h-4 w-4" />
          <span>{item.name}</span>
        </Button>
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* ロゴ */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold">
              CS
            </div>
            <span className="text-xl font-bold text-gray-900">
              Counseling Support
            </span>
          </Link>

          {/* デスクトップナビゲーション */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => (
              <NavItem key={item.name} item={item} />
            ))}
          </nav>


          {/* モバイルメニューボタン */}
          <div className="md:hidden">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu className="h-5 w-5" />
              <span className="sr-only">メニューを開く</span>
            </Button>
          </div>
        </div>
      </div>

      {/* モバイルメニュー */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t shadow-lg">
            {navigation.map((item) => {
              if (item.children) {
                return (
                  <div key={item.name} className="space-y-1">
                    <div className="flex items-center space-x-2 px-3 py-2 text-gray-900 font-medium">
                      <item.icon className="h-5 w-5" />
                      <span>{item.name}</span>
                    </div>
                    <div className="pl-8 space-y-1">
                      {item.children.map((child) => (
                        <Link
                          key={child.href}
                          href={child.href}
                          onClick={() => setMobileMenuOpen(false)}
                          className={cn(
                            'flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md',
                            isActivePath(child.href) && 'text-blue-600 bg-blue-50'
                          )}
                        >
                          <child.icon className="h-4 w-4" />
                          <span>{child.name}</span>
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              }

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md',
                    isActivePath(item.href) && 'text-blue-600 bg-blue-50'
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
}