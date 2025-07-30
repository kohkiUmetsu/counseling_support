'use client';

import { useState, useEffect } from 'react';
import { getScript, getScripts, ImprovementScript } from '@/repository/script';

interface UseScriptResult {
  data: ImprovementScript | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useScript(scriptId: string): UseScriptResult {
  const [data, setData] = useState<ImprovementScript | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchScript = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const scriptData = await getScript(scriptId);
      setData(scriptData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('予期しないエラーが発生しました'));
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (scriptId) {
      fetchScript();
    }
  }, [scriptId]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchScript,
  };
}

// スクリプト一覧取得用のhook
export function useScripts() {
  const [data, setData] = useState<ImprovementScript[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchScripts = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const scriptsData = await getScripts();
      setData(scriptsData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('予期しないエラーが発生しました'));
      setData([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  return {
    data,
    isLoading,
    error,
    refetch: fetchScripts,
  };
}