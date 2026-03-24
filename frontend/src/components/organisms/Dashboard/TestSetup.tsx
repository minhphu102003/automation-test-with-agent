'use client';

import React from 'react';
import { Card, Input, Button, Upload, Space, Typography, Tag } from 'antd';
import { InboxOutlined, RocketOutlined, GlobalOutlined } from '@ant-design/icons';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const TestSetup = () => {
  return (
    <Card 
      className="glass-card border-white/10" 
      title={<span className="text-white outfit text-lg">1. Configure Mission</span>}
    >
      <Space orientation="vertical" size="large" className="w-full">
        <div>
          <Text className="text-gray-400 block mb-2">Target Website URL</Text>
          <Input 
            prefix={<GlobalOutlined className="text-blue-500" />} 
            placeholder="https://example.com/login" 
            size="large"
            className="bg-white/5 border-white/10 text-white h-12 rounded-xl"
          />
        </div>

        <div>
          <Text className="text-gray-400 block mb-2">Test Cases (Excel / CSV)</Text>
          <Dragger 
            className="bg-white/5 border-dashed border-white/20 rounded-2xl p-8 hover:border-blue-500 transition-colors"
            multiple={false}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined className="text-4xl text-blue-500" />
            </p>
            <p className="ant-upload-text text-white font-medium">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint text-gray-500 text-xs">
              Support for single upload. Strictly prohibited from uploading company data or other banned files.
            </p>
          </Dragger>
        </div>

        <div className="flex gap-4">
          <Tag color="blue" className="rounded-full px-3">Browser: Playwright</Tag>
          <Tag color="purple" className="rounded-full px-3">Model: GPT-4o</Tag>
        </div>

        <Button 
          type="primary" 
          size="large" 
          block 
          icon={<RocketOutlined />}
          className="btn-primary h-14 text-lg mt-4"
        >
          Launch AI Agent
        </Button>
      </Space>
    </Card>
  );
};

export default TestSetup;
