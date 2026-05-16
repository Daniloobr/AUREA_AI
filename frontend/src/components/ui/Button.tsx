import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
}

export const Button = ({ 
  children, 
  variant = 'primary', 
  isLoading, 
  className = '', 
  ...props 
}: ButtonProps) => {
  const baseStyles = "relative inline-flex items-center justify-center gap-2 rounded-[14px] font-semibold transition-all duration-300 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed overflow-hidden";
  
  const variants = {
    primary: "bg-[#748FCC] text-[#F5F5F7] hover:bg-[#5F7DB8] shadow-lg shadow-[#748FCC]/20 hover:shadow-xl hover:shadow-[#748FCC]/30",
    secondary: "bg-transparent text-[#748FCC] border border-[#748FCC]/50 hover:border-[#748FCC] hover:bg-[#748FCC]/5",
    ghost: "bg-transparent text-[#F5F5F7] hover:bg-white/5"
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
          <span className="opacity-80">Carregando...</span>
        </div>
      ) : (
        <span className="flex items-center gap-2">{children}</span>
      )}
      
      {/* Subtle hover overlay */}
      <div className="absolute inset-0 bg-white/10 opacity-0 hover:opacity-100 transition-opacity pointer-events-none" />
    </button>
  );
};

