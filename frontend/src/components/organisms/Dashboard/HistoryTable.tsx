'use client';

import React from 'react';
import { Table, Tag, Typography, Button } from 'antd';
import { EyeOutlined, FilePdfOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

const HistoryTable = () => {
  const data = [
    { key: '1', id: 'TC-001', title: 'Login Validation', status: 'Pass', cost: '$0.0012', time: '2024-03-24 10:30' },
    { key: '2', id: 'TC-002', title: 'Checkout Flow', status: 'Fail', cost: '$0.0025', time: '2024-03-24 10:35' },
    { key: '3', id: 'TC-003', title: 'User Profile Update', status: 'Pass', cost: '$0.0008', time: '2024-03-24 10:40' },
  ];

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', render: (text: string) => <span className="font-bold text-blue-400">{text}</span> },
    { title: 'Title', dataIndex: 'title', key: 'title', render: (text: string) => <span className="text-gray-300">{text}</span> },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'Pass' ? 'success' : 'error'} className="rounded-full px-3">{status}</Tag>
      )
    },
    { title: 'Cost', dataIndex: 'cost', key: 'cost', render: (text: string) => <span className="text-gray-400">{text}</span> },
    { title: 'Time', dataIndex: 'time', key: 'time', render: (text: string) => <span className="text-gray-500 text-xs">{text}</span> },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <div className="flex gap-2">
          <Button size="small" ghost icon={<EyeOutlined />} className="border-white/10 text-white" />
          <Button size="small" ghost icon={<FilePdfOutlined />} className="border-white/10 text-white" />
        </div>
      ),
    },
  ];

  return (
    <div className="mt-8">
      <Title level={4} className="text-white outfit mb-6">Execution History</Title>
      <Table 
        dataSource={data} 
        columns={columns} 
        pagination={false} 
        className="glass-card-table"
        rowClassName="bg-transparent hover:bg-white/5"
      />
    </div>
  );
};

export default HistoryTable;
