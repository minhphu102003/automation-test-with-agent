'use client';

import React from 'react';
import { Button, Dropdown, MenuProps } from 'antd';
import { DownOutlined } from '@ant-design/icons';

const platformItems: MenuProps['items'] = [
  { key: '1', label: 'Automation Testing' },
  { key: '2', label: 'Manual Testing' },
  { key: '3', label: 'Cross Browser Testing' },
];

const Navbar = () => {
  return (
    <nav className="border-b border-gray-100 px-6 md:px-20 py-4 flex justify-between items-center bg-white sticky top-0 z-50">
      <div className="flex items-center gap-12">
        <div className="flex flex-col leading-tight cursor-pointer" onClick={() => window.location.href = '/'}>
          <span className="text-xl font-black tracking-tighter outfit text-black">TestMu AI</span>
          <span className="text-[9px] uppercase tracking-widest text-gray-400 font-bold">Formerly LambdaTest</span>
        </div>

        <div className="hidden lg:flex items-center gap-8">
          <Dropdown menu={{ items: platformItems }}>
            <a className="nav-link">Platform <DownOutlined className="text-[10px]" /></a>
          </Dropdown>
          <Dropdown menu={{ items: platformItems }}>
            <a className="nav-link">Solutions <DownOutlined className="text-[10px]" /></a>
          </Dropdown>
          <Dropdown menu={{ items: platformItems }}>
            <a className="nav-link">Resources <DownOutlined className="text-[10px]" /></a>
          </Dropdown>
          <Dropdown menu={{ items: platformItems }}>
            <a className="nav-link">AI Agents <DownOutlined className="text-[10px]" /></a>
          </Dropdown>
          <a className="nav-link">Pricing</a>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <a href="/dashboard" className="text-sm font-semibold hover:text-blue-600 transition-colors text-gray-700">Login</a>
        <Button className="btn-testmu-accent hidden md:flex items-center">Book a Demo</Button>
        <Button className="btn-testmu-primary bg-black text-white hover:bg-gray-800">Get Started Free</Button>
      </div>
    </nav>
  );
};

export default Navbar;
