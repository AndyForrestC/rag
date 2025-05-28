"use client";

interface MenuButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export default function MenuButton({ onClick, isOpen }: MenuButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        fixed top-4 left-4 z-60 p-3 rounded-lg shadow-lg transition-all duration-300
        ${isOpen 
          ? 'bg-gray-800 text-white' 
          : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
        }
      `}
      title="切换侧边栏"
    >
      <svg 
        className={`w-6 h-6 transition-transform duration-300 ${isOpen ? 'rotate-90' : ''}`}
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  );
}
