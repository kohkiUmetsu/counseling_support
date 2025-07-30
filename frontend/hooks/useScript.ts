'use client';

import { useState, useEffect } from 'react';

interface Script {
  id: string;
  title: string;
  version: string;
  status: 'draft' | 'active' | 'archived';
  created_at: string;
  updated_at: string;
  content: {
    opening?: string;
    needs_assessment?: string;
    solution_proposal?: string;
    closing?: string;
    success_factors_analysis?: string;
    improvement_points?: string;
    practical_improvements?: string;
    expected_effects?: string;
  };
  success_factors?: string[];
  improvement_points?: string[];
  quality_metrics?: {
    overall_quality: number;
    coverage?: {
      coverage_percentage: number;
      covered_patterns: string[];
      missing_patterns: string[];
      coverage_score: number;
    };
    novelty?: {
      novelty_score: number;
      unique_elements: string[];
      innovation_areas: string[];
    };
    reliability?: {
      confidence_score: number;
      data_quality_score: number;
      recommendation_strength: string;
    };
    success_matching?: {
      matching_rate: number;
      matched_elements: string[];
      missing_elements: string[];
    };
  };
  generation_metadata?: {
    total_success_conversations: number;
    clusters_identified: number;
    representatives_selected: number;
    generation_time: number;
    cost: number;
  };
}

interface UseScriptResult {
  data: Script | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useScript(scriptId: string): UseScriptResult {
  const [data, setData] = useState<Script | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchScript = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/v1/scripts/${scriptId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('スクリプトが見つかりません');
        }
        throw new Error(`サーバーエラー: ${response.status}`);
      }

      const scriptData = await response.json();
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
  const [data, setData] = useState<Script[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchScripts = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('/api/v1/scripts');
      
      if (!response.ok) {
        throw new Error(`サーバーエラー: ${response.status}`);
      }

      const scriptsData = await response.json();
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