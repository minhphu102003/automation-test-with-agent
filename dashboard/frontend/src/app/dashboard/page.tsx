'use client';

import React from 'react';
import { Layout, Row, Col, Typography, Badge, ConfigProvider, theme } from 'antd';
import Sidebar from '@/components/organisms/Dashboard/Sidebar';
import TestSetup from '@/components/organisms/Dashboard/TestSetup';
import LiveConsole from '@/components/organisms/Dashboard/LiveConsole';
import HistoryTable from '@/components/organisms/Dashboard/HistoryTable';

const { Content } = Layout;
const { Title, Text } = Typography;

export default function DashboardPage() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
      }}
    >
      <Layout className="min-h-screen bg-[#0b0e14]">
      <Sidebar />
      <Layout className="bg-transparent">
        <header className="py-8 px-12 border-b border-white/5 flex justify-between items-center">
          <div>
            <Title level={2} className="text-white outfit m-0">Mission Control</Title>
            <Text className="text-gray-500">Orchestrate your AI Agents and monitor results in real-time.</Text>
          </div>
          <div className="flex gap-10">
            <div className="text-right">
              <div className="text-gray-500 text-xs uppercase tracking-wider mb-1">Engine Status</div>
              <Badge status="processing" text={<span className="text-green-400 font-bold outfit">V2 ENGINE READY</span>} />
            </div>
          </div>
        </header>

        <Content className="p-12">
          <Row gutter={[32, 32]}>
            <Col span={24} lg={10}>
              <TestSetup />
            </Col>
            <Col span={24} lg={14}>
              <LiveConsole />
            </Col>
            <Col span={24}>
              <HistoryTable />
            </Col>
          </Row>
        </Content>
      </Layout>
    </Layout>
    </ConfigProvider>
  );
}
