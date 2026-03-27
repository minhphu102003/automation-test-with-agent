'use client';

import React, { useState } from 'react';
import { Card, Input, Button, Upload, Space, Typography, Tag, message } from 'antd';
import { InboxOutlined, RocketOutlined, GlobalOutlined, KeyOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;
const { Text } = Typography;

const TestSetup = () => {
  const [url, setUrl] = useState('');
  const [token, setToken] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const uploadProps: UploadProps = {
    onRemove: () => setFile(null),
    beforeUpload: (file) => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.type === 'text/csv';
      if (!isExcel) {
        message.error('You can only upload Excel or CSV files!');
        return Upload.LIST_IGNORE;
      }
      setFile(file);
      return false; // Prevent automatic upload
    },
    maxCount: 1,
  };

  const handleLaunch = async () => {
    if (!file) {
      message.error("Please upload an Excel test case file.");
      return;
    }
    if (!url) {
      message.error("Please provide a target URL.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("url", url);
    formData.append("access_token", token);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/automation/run_excel`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to launch agent");
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `test_results.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      message.success('Automation sequence completed! File downloaded successfully.');
    } catch (error) {
      console.error(error);
      message.error("Error launching automation sequence.");
    } finally {
      setLoading(false);
    }
  };

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
            placeholder="https://example.com" 
            size="large"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="bg-white/5 border-white/10 text-white h-12 rounded-xl"
          />
        </div>

        <div>
          <Text className="text-gray-400 block mb-2">Access Token (Optional - Bypass Login)</Text>
          <Input.Password
            prefix={<KeyOutlined className="text-blue-500" />} 
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI..." 
            size="large"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="bg-white/5 border-white/10 text-white h-12 rounded-xl"
          />
        </div>

        <div>
          <Text className="text-gray-400 block mb-2">Test Cases (Excel / CSV)</Text>
          <Dragger 
            {...uploadProps}
            className="bg-white/5 border-dashed border-white/20 rounded-2xl p-8 hover:border-blue-500 transition-colors"
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
          <Tag color="purple" className="rounded-full px-3">Model: GPT-4o-mini</Tag>
        </div>

        <Button 
          type="primary" 
          size="large" 
          block 
          loading={loading}
          onClick={handleLaunch}
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
