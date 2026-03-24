'use client';

import React from 'react';

const BrandSection = () => {
  return (
    <div className="py-20 border-t border-gray-50 flex flex-col items-center justify-center gap-4 bg-white">
      <div className="flex items-center gap-3">
        <span className="text-3xl font-black outfit text-black">TestMu AI</span>
      </div>
      <div className="text-gray-400 text-sm font-medium">
        LambdaTest is now <span className="text-black font-bold border-b-2 border-blue-500">TestMu AI</span>. The Next Chapter →
      </div>
    </div>
  );
};

export default BrandSection;
