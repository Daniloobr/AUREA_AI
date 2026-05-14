import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
}

export const Card = ({ children, className = '', hoverable = false }: CardProps) => {
  return (
    <div className={`
      bg-[#121417] 
      border border-white/8 
      rounded-[12px] 
      overflow-hidden 
      transition-all duration-300 
      ${hoverable ? 'hover:border-white/20 hover:bg-[#121417] hover:shadow-[0_0_40px_rgba(116,143,204,0.15)]' : ''} 
      ${className}
    `}>
      {children}
    </div>
  );
};
