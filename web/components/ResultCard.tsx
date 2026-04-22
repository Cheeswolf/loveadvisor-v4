import React from 'react';

interface ResultCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'risk' | 'next_step';
}

export default function ResultCard({ title, children, className = '', variant = 'default' }: ResultCardProps) {
  const baseStyles = 'rounded-md p-4';
  const variantStyles = variant === 'risk'
    ? 'border border-red-200 bg-red-50 shadow-sm shadow-red-100'
    : variant === 'next_step'
    ? 'border-2 border-green-300 bg-green-50 shadow-md shadow-green-100'
    : 'bg-gray-50';
  const titleStyles = variant === 'risk'
    ? 'font-semibold text-red-800 mb-2'
    : variant === 'next_step'
    ? 'font-bold text-green-800 mb-3 text-lg'
    : 'font-medium text-gray-700 mb-2';
  const contentStyles = variant === 'risk'
    ? 'text-gray-800 text-sm'
    : variant === 'next_step'
    ? 'text-green-900 text-base leading-relaxed'
    : 'text-gray-700 text-sm';

  return (
    <div className={`${baseStyles} ${variantStyles} ${className}`}>
      <h3 className={titleStyles}>{title}</h3>
      <div className={contentStyles}>{children}</div>
    </div>
  );
}