import React from 'react';

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
  const baseStyles = "inline-flex items-center justify-center gap-2 rounded-[12px] font-medium transition-all duration-300 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none cursor-pointer";
  
  const variants = {
    primary: "bg-[#748FCC] text-[#F5F5F7] hover:bg-[#5F7DB8] hover:shadow-[0_0_40px_rgba(116,143,204,0.35)]",
    secondary: "bg-transparent text-[#748FCC] border border-[#748FCC] hover:bg-[rgba(116,143,204,0.12)] hover:text-[#5F7DB8]",
    ghost: "bg-transparent text-[#F5F5F7] hover:bg-[#121417]"
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <div className="w-5 h-5 border-2 border-[#F5F5F7]/20 border-t-[#F5F5F7] rounded-full animate-spin" />
      ) : children}
    </button>
  );
};
