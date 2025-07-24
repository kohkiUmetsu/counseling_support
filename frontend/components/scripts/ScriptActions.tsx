'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { 
  Printer, 
  Share2, 
  Download, 
  MoreVertical, 
  FileText, 
  FileSpreadsheet, 
  Eye,
  Archive,
  Copy,
  Edit
} from 'lucide-react';

interface ScriptActionsProps {
  onPrint: () => void;
  onShare: () => void;
  script: {
    id: string;
    version: string;
    status: string;
    title?: string;
  };
}

export function ScriptActions({ onPrint, onShare, script }: ScriptActionsProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportMarkdown = async () => {
    setIsExporting(true);
    try {
      // TODO: APIからMarkdown形式でエクスポート
      const response = await fetch(`/api/v1/scripts/${script.id}/export/markdown`);
      const blob = await response.blob();
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `script_v${script.version}_${new Date().toISOString().split('T')[0]}.md`;
      link.click();
      
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      // TODO: エラートーストを表示
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      // TODO: APIからPDF形式でエクスポート
      const response = await fetch(`/api/v1/scripts/${script.id}/export/pdf`);
      const blob = await response.blob();
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `script_report_v${script.version}_${new Date().toISOString().split('T')[0]}.pdf`;
      link.click();
      
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      // TODO: エラートーストを表示
    } finally {
      setIsExporting(false);
    }
  };

  const handleDuplicateScript = async () => {
    try {
      // TODO: スクリプトの複製API呼び出し
      const response = await fetch(`/api/v1/scripts/${script.id}/duplicate`, {
        method: 'POST',
      });
      const newScript = await response.json();
      
      // 新しいスクリプトページに遷移
      window.location.href = `/scripts/${newScript.id}`;
    } catch (error) {
      console.error('Duplicate failed:', error);
      // TODO: エラートーストを表示
    }
  };

  const handleArchiveScript = async () => {
    if (!confirm('このスクリプトをアーカイブしますか？')) return;
    
    try {
      // TODO: アーカイブAPI呼び出し
      await fetch(`/api/v1/scripts/${script.id}/archive`, {
        method: 'POST',
      });
      
      // ページリロード
      window.location.reload();
    } catch (error) {
      console.error('Archive failed:', error);
      // TODO: エラートーストを表示
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">アクション</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* 基本アクション */}
        <div className="grid grid-cols-2 gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onPrint}
            className="w-full"
          >
            <Printer className="h-4 w-4 mr-2" />
            印刷
          </Button>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onShare}
            className="w-full"
          >
            <Share2 className="h-4 w-4 mr-2" />
            共有
          </Button>
        </div>

        {/* エクスポート */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">エクスポート</h4>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleExportMarkdown}
            disabled={isExporting}
            className="w-full"
          >
            <FileText className="h-4 w-4 mr-2" />
            Markdown形式
          </Button>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleExportPDF}
            disabled={isExporting}
            className="w-full"
          >
            <Download className="h-4 w-4 mr-2" />
            PDFレポート
          </Button>
        </div>

        {/* その他のアクション */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">管理</h4>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="w-full">
                <MoreVertical className="h-4 w-4 mr-2" />
                その他
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => window.open(`/scripts/${script.id}/history`, '_blank')}>
                <Eye className="h-4 w-4 mr-2" />
                履歴を表示
              </DropdownMenuItem>
              
              <DropdownMenuItem onClick={handleDuplicateScript}>
                <Copy className="h-4 w-4 mr-2" />
                複製
              </DropdownMenuItem>
              
              <DropdownMenuItem onClick={() => window.open(`/scripts/${script.id}/edit`, '_blank')}>
                <Edit className="h-4 w-4 mr-2" />
                編集
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              {script.status !== 'archived' && (
                <DropdownMenuItem 
                  onClick={handleArchiveScript}
                  className="text-orange-600"
                >
                  <Archive className="h-4 w-4 mr-2" />
                  アーカイブ
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* スクリプト情報 */}
        <div className="pt-3 border-t">
          <h4 className="text-sm font-medium text-gray-700 mb-2">スクリプト情報</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div>ID: {script.id}</div>
            <div>バージョン: {script.version}</div>
            <div>ステータス: {script.status}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}