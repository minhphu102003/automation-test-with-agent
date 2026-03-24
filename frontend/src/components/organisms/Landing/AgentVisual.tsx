'use client';

import React from 'react';
import { Typography } from 'antd';
import { RobotOutlined, SearchOutlined } from '@ant-design/icons';

const { Text } = Typography;

const AgentVisual = () => {
  return (
    <div className="relative group">
      <div className="absolute inset-x-0 -top-20 -bottom-20 bg-blue-400/10 blur-[100px] rounded-full opacity-50 group-hover:opacity-100 transition-opacity" />
      <div className="relative bg-white rounded-3xl overflow-hidden shadow-2xl border border-gray-100 transform group-hover:scale-[1.02] transition-transform duration-700">
        {/* Image Placeholder with Interactive Prompt */}
        <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-100 relative flex items-center justify-center p-12">
           <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=2070')] bg-cover bg-center mix-blend-overlay opacity-20" />
           
           <div className="bg-white/90 backdrop-blur-md p-10 rounded-3xl shadow-2xl w-full max-w-lg border border-white/50 text-center relative z-20">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-purple-500/20">
                <RobotOutlined className="text-3xl text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-6 outfit text-gray-800">What is your objective today?</h3>
              
              <div className="grid grid-cols-2 gap-4 text-xs text-left mb-6">
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-blue-300 transition-colors cursor-pointer">
                  <Text className="block font-bold mb-1">Onboarding Flow</Text>
                  <Text className="text-[10px] text-gray-500">Test the end-to-end checkout for new users.</Text>
                </div>
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-blue-300 transition-colors cursor-pointer">
                  <Text className="block font-bold mb-1">Booking Vendor</Text>
                  <Text className="text-[10px] text-gray-500">Search and book a stay for 2 guests.</Text>
                </div>
              </div>

              <div className="h-10 bg-gray-100 rounded-full flex items-center px-4 justify-between group/input border border-transparent focus-within:border-blue-400 focus-within:bg-white transition-all">
                <Text className="text-gray-400 text-xs">Type your instruction...</Text>
                <SearchOutlined className="text-blue-500" />
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default AgentVisual;
