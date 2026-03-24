'use client';

import React from 'react';

const TopBanner = () => {
  return (
    <div className="bg-gradient-to-r from-[#003366] to-[#001a33] text-white py-2 text-center text-xs md:text-sm font-medium">
      LambdaTest is now <span className="font-bold">TestMu AI</span>. 
      <a href="#" className="underline ml-2 hover:text-blue-300 transition-colors">The Next Chapter Begins →</a>
    </div>
  );
};

export default TopBanner;
