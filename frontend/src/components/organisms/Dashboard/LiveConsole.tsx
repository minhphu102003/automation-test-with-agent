'use client';

import React from 'react';
import { Card, Timeline, Typography, Badge, Empty } from 'antd';
import { SyncOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

const LiveConsole = () => {
  const [logs, setLogs] = React.useState([
    { content: 'System: Environment initialized', color: 'gray', time: '14:20:01' },
    { content: 'Agent: Starting session for TC-001', color: 'blue', time: '14:20:05' },
    { content: 'Playwright: Navigating to https://saucedemo.com', color: 'blue', time: '14:20:10' },
    { content: 'Agent: Analyzing page structure...', icon: <LoadingOutlined />, color: 'blue', time: '14:20:15' },
  ]);

  return (
    <Card 
      className="glass-card border-white/10 h-full flex flex-col" 
      title={
        <div className="flex justify-between items-center w-full">
          <span className="text-white outfit text-lg">2. Live Agent Console</span>
          <Badge status="processing" text={<span className="text-blue-400 text-xs">AGENT ACTIVE</span>} />
        </div>
      }
    >
      <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar">
        <Timeline
          mode="start"
          items={logs.map(log => ({
            ...log,
            title: <span className="text-gray-600 text-[10px]">{log.time}</span>,
            content: <span className="text-gray-300 text-sm">{log.content}</span>
          }))}
        />
        {logs.length === 0 && <Empty description="No logs yet. Launch an agent to see live status." />}
      </div>
    </Card>
  );
};

export default LiveConsole;
