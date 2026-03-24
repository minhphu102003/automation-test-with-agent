'use client';

import React from 'react';
import { Menu, Layout } from 'antd';
import { 
  DashboardOutlined, 
  HistoryOutlined, 
  SettingOutlined, 
  SafetyCertificateOutlined,
  CloudOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = () => {
  return (
    <Sider
      width={260}
      className="h-screen sticky top-0 border-r border-white/5 bg-[#0b0e14]"
      theme="dark"
    >
      <div className="p-8 flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center font-bold text-xl outfit text-white">A</div>
        <span className="text-xl font-bold outfit tracking-tight text-white line-clamp-1">Antigravity</span>
      </div>
      
      <Menu
        mode="inline"
        defaultSelectedKeys={['1']}
        className="bg-transparent border-none px-4"
        theme="dark"
        items={[
          { key: '1', icon: <DashboardOutlined />, label: 'Dashboard' },
          { key: '2', icon: <HistoryOutlined />, label: 'Executions' },
          { key: '3', icon: <CloudOutlined />, label: 'Storage' },
          { key: '4', icon: <SafetyCertificateOutlined />, label: 'Credentials' },
          { type: 'divider' },
          { key: '5', icon: <SettingOutlined />, label: 'Settings' },
        ]}
      />
    </Sider>
  );
};

export default Sidebar;
