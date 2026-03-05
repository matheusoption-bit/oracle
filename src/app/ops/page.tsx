'use client';

import { useState } from 'react';
import { AgentLogViewer } from '@/components/agents/AgentLogViewer';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function OpsPage() {
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);

    const res = await fetch('/api/ops', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task }),
    });

    const data = await res.json();
    console.log(data);

    setLoading(false);
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">oracle</h1>

      <div className="grid grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Nova Task</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Descreva o que deseja criar..."
              value={task}
              onChange={(e) => setTask(e.target.value)}
              className="mb-4 min-h-[200px]"
            />
            <Button onClick={handleSubmit} disabled={loading || !task} className="w-full">
              {loading ? 'Executando...' : 'Executar'}
            </Button>
          </CardContent>
        </Card>

        <AgentLogViewer />
      </div>
    </div>
  );
}
