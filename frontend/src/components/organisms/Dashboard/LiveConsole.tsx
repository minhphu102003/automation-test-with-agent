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
      styles={{ body: { padding: 0, display: 'flex', flexDirection: 'column', height: '100%' } }}
      title={
        <div className="flex justify-between items-center w-full">
          <span className="text-white outfit text-lg">2. Live Agent Console</span>
          <Badge status="processing" text={<span className="text-blue-400 text-xs">AGENT ACTIVE & STREAMING</span>} />
        </div>
      }
    >
      <div className="flex flex-col h-full bg-black/20 overflow-hidden">
        {/* Browser Window VNC View via Browserless */}
        <div className="flex-[3] border-b border-white/10 relative bg-black">
          <iframe 
            src="http://localhost:3002/" 
            className="w-full h-full border-none absolute inset-0"
            title="Browserless Live Session Viewer"
            allow="fullscreen"
          />
        </div>
        
        {/* Logs Timeline */}
        <div className="flex-[2] overflow-y-auto p-4 custom-scrollbar">
          <Timeline
            mode="left"
            items={logs.map(log => ({
              ...log,
              label: <span className="text-gray-500 text-xs">{log.time}</span>,
              children: <span className="text-gray-300 text-sm">{log.content}</span>
            }))}
          />
          {logs.length === 0 && <Empty description="No logs yet. Launch an agent to see live status." />}
        </div>
      </div>
    </Card>
  );
};

export default LiveConsole;
