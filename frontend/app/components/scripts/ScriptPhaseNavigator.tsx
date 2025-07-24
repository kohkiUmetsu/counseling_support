'use client';

import { cn } from '@/app/utils/cn';

interface Phase {
  id: string;
  label: string;
  description: string;
}

interface ScriptPhaseNavigatorProps {
  phases: readonly Phase[];
  activePhase: string;
  onPhaseChange: (phase: string) => void;
}

export function ScriptPhaseNavigator({ 
  phases, 
  activePhase, 
  onPhaseChange 
}: ScriptPhaseNavigatorProps) {
  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4">
        <nav className="flex space-x-1" aria-label="スクリプトフェーズ">
          {phases.map((phase, index) => {
            const isActive = activePhase === phase.id;
            const isCompleted = false; // TODO: 完了状態の管理
            
            return (
              <button
                key={phase.id}
                onClick={() => onPhaseChange(phase.id)}
                className={cn(
                  'flex-1 px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  {
                    'bg-blue-600 text-white shadow-sm': isActive,
                    'text-gray-600 hover:text-gray-900 hover:bg-gray-50': !isActive,
                  }
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <div className="flex items-center justify-center space-x-2">
                  {/* フェーズ番号 */}
                  <span className={cn(
                    'flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold',
                    {
                      'bg-white text-blue-600': isActive,
                      'bg-gray-200 text-gray-600': !isActive,
                    }
                  )}>
                    {index + 1}
                  </span>
                  
                  {/* フェーズ名 */}
                  <span className="hidden sm:inline">{phase.label}</span>
                </div>
                
                {/* 説明文（アクティブ時のみ表示） */}
                {isActive && (
                  <div className="mt-1 text-xs text-blue-100 hidden md:block">
                    {phase.description}
                  </div>
                )}
              </button>
            );
          })}
        </nav>
        
        {/* モバイル用の説明文 */}
        <div className="mt-3 md:hidden">
          {phases.map((phase) => (
            activePhase === phase.id && (
              <p key={phase.id} className="text-sm text-gray-600 text-center">
                {phase.description}
              </p>
            )
          ))}
        </div>
      </div>
    </div>
  );
}