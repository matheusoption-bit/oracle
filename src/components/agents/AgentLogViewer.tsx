'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

interface LogEntry {
  timestamp: string;
  phase: string;
  message: string;
  type: 'info' | 'error' | 'success';
}

export function AgentLogViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    // Simular SSE (implementar depois com Vercel AI SDK)
    const interval = setInterval(() => {
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          phase: 'executing',
          message: `Step ${prev.length + 1} executado`,
          type: 'info',
        },
      ]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Logs (Real-time)</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {logs.map((log, i) => (
            <div
              key={i}
              className={`p-2 mb-2 rounded ${
                log.type === 'error'
                  ? 'bg-red-100'
                  : log.type === 'success'
                    ? 'bg-green-100'
                    : 'bg-blue-50'
              }`}
            >
              <span className="text-xs text-gray-500">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className="ml-2 font-mono text-sm">[{log.phase}]</span>
              <p className="mt-1">{log.message}</p>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
