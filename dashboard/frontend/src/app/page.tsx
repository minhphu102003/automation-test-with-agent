'use client';

import React from 'react';
import { Button, Typography, Space, Badge, ConfigProvider, theme } from 'antd';

const { Title, Text } = Typography;

export default function LandingPage() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#3b82f6',
          borderRadius: 12,
        },
      }}
    >
      <div className="relative min-h-screen bg-[#0b0e14] text-white overflow-hidden">
        {/* Decorative Glows */}
        <div className="glow glow-1" />
        <div className="glow glow-2" />

        {/* Navbar */}
        <nav className="fixed top-0 w-full z-50 py-6 px-8 md:px-12 flex justify-between items-center backdrop-blur-md border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center font-bold text-xl outfit">A</div>
            <span className="text-xl font-bold outfit tracking-tight">Antigravity</span>
          </div>
          <div className="hidden md:flex gap-10 items-center">
            <a className="text-gray-400 hover:text-white transition-colors cursor-pointer">Dashboard</a>
            <a className="text-gray-400 hover:text-white transition-colors cursor-pointer">Reports</a>
            <a className="text-gray-400 hover:text-white transition-colors cursor-pointer">Monitoring</a>
            <Button className="btn-primary px-8">Launch App</Button>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="pt-48 pb-24 px-8 md:px-12 container mx-auto text-center">
          <Badge count="New: V2 Engine" offset={[10, 0]} color="#3b82f6" className="mb-8">
            <div className="px-6 py-2 glass-card inline-block border-white/20">
              <span className="text-sm font-medium">Revolutionizing Web Automation</span>
            </div>
          </Badge>
          
          <h1 className="text-5xl md:text-8xl font-black outfit mb-8 tracking-tight leading-tight">
            Automate the Web <br />
            <span className="gradient-text">Like Magic.</span>
          </h1>
          
          <p className="max-w-3xl mx-auto text-lg md:text-xl text-gray-400 mb-12 leading-relaxed">
            Build, run, and scale browser automation with AI agents. 
            Get professional reports, cost tracing, and execution evidence in one unified dashboard.
          </p>
          
          <div className="flex flex-col md:flex-row gap-6 justify-center">
            <Button size="large" className="btn-primary h-14 px-10 text-lg">Start Building</Button>
            <Button size="large" ghost className="h-14 px-10 text-lg border-white/20 text-white hover:bg-white/5">Documentation</Button>
          </div>

          {/* Dashboard Preview */}
          <div className="mt-24 w-full max-w-6xl mx-auto glass-card p-4 border-white/10 shadow-2xl animate-float">
            <div className="w-full h-[400px] md:h-[500px] bg-[#161b22] rounded-xl overflow-hidden relative">
              <div className="absolute top-0 left-0 w-full h-12 bg-white/5 border-b border-white/5 flex items-center px-6 gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <div className="bg-white/5 px-4 py-1 rounded-md text-xs text-gray-500 ml-4">https://automation.antigravity.ai/dashboard</div>
              </div>
              <div className="p-6 md:p-10 pt-20 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
                <div className="md:col-span-2 space-y-8">
                  <div className="h-32 glass-card p-6 border-white/5">
                    <div className="text-gray-500 text-sm mb-2">Total Estimated Cost</div>
                    <div className="text-4xl font-bold outfit text-blue-400">$24.82</div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 md:gap-8">
                    <div className="h-28 glass-card p-6 border-white/5">
                      <div className="text-gray-500 text-sm mb-2">Success Rate</div>
                      <div className="text-2xl md:text-3xl font-bold outfit text-green-400">98.5%</div>
                    </div>
                    <div className="h-28 glass-card p-6 border-white/5">
                      <div className="text-gray-500 text-sm mb-2">Efficiency</div>
                      <div className="text-2xl md:text-3xl font-bold outfit text-purple-400">High</div>
                    </div>
                  </div>
                </div>
                <div className="glass-card p-6 border-white/5 flex flex-col items-center justify-center text-center">
                  <div className="w-24 h-24 rounded-full border-8 border-blue-500/20 border-t-blue-500 flex items-center justify-center text-xl font-bold outfit">85%</div>
                  <div className="mt-6 text-xl font-bold outfit">Active Tests</div>
                  <div className="text-gray-500 text-sm">Target: 100/day</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 px-8 md:px-12 container mx-auto">
          <div className="grid md:grid-cols-3 gap-10">
            <div className="glass-card p-10">
              <div className="w-14 h-14 bg-blue-500/20 rounded-2xl flex items-center justify-center text-3xl mb-8">🤖</div>
              <h3 className="text-2xl font-bold outfit mb-4">AI Agent Core</h3>
              <p className="text-gray-400 leading-relaxed">Leverage state-of-the-art LLMs to interact with any website exactly like a human would.</p>
            </div>
            <div className="glass-card p-10">
              <div className="w-14 h-14 bg-purple-500/20 rounded-2xl flex items-center justify-center text-3xl mb-8">📊</div>
              <h3 className="text-2xl font-bold outfit mb-4">Cost Tracing</h3>
              <p className="text-gray-400 leading-relaxed">Real-time cost analysis and token usage monitoring for every single step of your automation.</p>
            </div>
            <div className="glass-card p-10">
              <div className="w-14 h-14 bg-pink-500/20 rounded-2xl flex items-center justify-center text-3xl mb-8">📄</div>
              <h3 className="text-2xl font-bold outfit mb-4">Evidence Reports</h3>
              <p className="text-gray-400 leading-relaxed">Automatic PDF and HTML reports with embedded screenshots of every pass and fail.</p>
            </div>
          </div>
        </section>

        {/* CTA Footer */}
        <footer className="py-24 border-t border-white/5 text-center mt-20">
          <h2 className="text-3xl md:text-4xl font-bold outfit mb-8">Ready to automate?</h2>
          <Button className="btn-primary h-14 px-12 text-lg">Get Started for Free</Button>
          <div className="mt-12 text-gray-600 text-sm">© 2024 Antigravity AI. All rights reserved.</div>
        </footer>
      </div>
    </ConfigProvider>
  );
}
