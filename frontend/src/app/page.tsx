'use client';

import React from 'react';
import { ConfigProvider, Layout } from 'antd';
import TopBanner from '@/components/organisms/Landing/TopBanner';
import Navbar from '@/components/organisms/Landing/Navbar';
import Hero from '@/components/organisms/Landing/Hero';
import BrandSection from '@/components/organisms/Landing/BrandSection';
import ChatWidget from '@/components/organisms/Landing/ChatWidget';

const { Header, Content, Footer } = Layout;

export default function LandingPage() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1d1d1f',
          borderRadius: 6,
          fontFamily: "'Inter', sans-serif",
        },
      }}
    >
      <Layout className="min-h-screen bg-white text-black overflow-x-hidden selection:bg-orange-100">
        <TopBanner />
        
        <Header className="p-0 h-auto bg-white sticky top-0 z-50 border-none">
          <Navbar />
        </Header>

        <Content className="bg-white">
          <Hero />
        </Content>

        <Footer className="p-0 bg-white">
          <BrandSection />
        </Footer>

        <ChatWidget />
      </Layout>
    </ConfigProvider>
  );
}
