/**
 * Button Component
 *
 * 재사용 가능한 버튼 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </Button>
 *
 * @example
 * <Button variant="outline" size="lg" isLoading>
 *   Loading...
 * </Button>
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** 버튼 스타일 변형 */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  /** 버튼 크기 */
  size?: 'sm' | 'md' | 'lg';
  /** 로딩 상태 */
  isLoading?: boolean;
  /** 전체 너비 */
  fullWidth?: boolean;
  /** 자식 요소 */
  children: React.ReactNode;
}

const variantStyles = {
  primary:
    'bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800 shadow-sm hover:shadow-md',
  secondary:
    'bg-slate-200 text-slate-900 hover:bg-slate-300 active:bg-slate-400',
  outline:
    'bg-transparent text-indigo-600 border-2 border-indigo-600 hover:bg-indigo-50 active:bg-indigo-100',
  ghost:
    'bg-transparent text-slate-600 hover:bg-slate-100 active:bg-slate-200',
  danger:
    'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-sm hover:shadow-md',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const isDisabled = disabled || isLoading;

  return (
    <motion.button
      className={cn(
        // 기본 스타일
        'inline-flex items-center justify-center gap-2',
        'font-semibold rounded-xl',
        'transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
        // Variant 스타일
        variantStyles[variant],
        // Size 스타일
        sizeStyles[size],
        // 전체 너비
        fullWidth && 'w-full',
        // 비활성화 스타일
        isDisabled && 'opacity-50 cursor-not-allowed',
        // 커스텀 클래스
        className
      )}
      disabled={isDisabled}
      whileTap={!isDisabled ? { scale: 0.95 } : undefined}
      {...props}
    >
      {isLoading && (
        <Loader2 className="w-4 h-4 animate-spin" />
      )}
      {children}
    </motion.button>
  );
};
