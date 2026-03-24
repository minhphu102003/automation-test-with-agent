'use client';

import React from 'react';
import { Button, Typography } from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import AgentVisual from './AgentVisual';

const { Title, Paragraph } = Typography;

const Hero = () => {
  return (
    <section className="testmu-hero-bg pt-24 pb-48 relative overflow-hidden">
      {/* Nature Background Overlay */}
      <div className="absolute inset-0 testmu-forest-bg pointer-events-none" />

      <div className="container mx-auto px-6 md:px-12 grid lg:grid-cols-2 gap-16 items-center relative z-10">
        {/* Left Content */}
        <div className="max-w-xl">
          <h1 className="text-5xl md:text-7xl font-bold leading-[1.1] mb-8 text-[#1d1d1f] outfit">
            Power Your <br />
            Software Testing <br />
            with AI Agents and <br />
            Cloud
          </h1>
          <p className="text-xl text-gray-600 mb-10 leading-relaxed font-medium">
            The Native AI-Agentic Cloud Platform to Supercharge Quality Engineering.
            Test Intelligently and Ship Faster.
          </p>

          <div className="flex flex-wrap gap-4">
            <Button className="btn-testmu-primary group flex items-center gap-4" href="/dashboard">
              Start free Testing
              <div className="w-5 h-5 bg-[#f8481c] rounded flex items-center justify-center">
                <ArrowRightOutlined className="text-[10px] text-white" />
              </div>
            </Button>
            <Button className="btn-testmu-accent px-8 h-[52px]">Book a Demo</Button>
          </div>
        </div>

        {/* Right Visual */}
        <AgentVisual />
      </div>
    </section>
  );
};

export default Hero;
