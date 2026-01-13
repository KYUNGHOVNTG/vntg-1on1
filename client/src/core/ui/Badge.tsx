/**
 * Badge Component
 *
 * 작은 라벨/태그 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Badge>Default</Badge>
 * <Badge variant="success">Success</Badge>
 * <Badge variant="warning" size="lg">Warning</Badge>
 *
 * @example
 * <Badge variant="info" dot>
 *   Active
 * </Badge>
 */

import React from 'react';
import { cn } from '@/utils/cn';

interface BadgeProps {
  /** 배지 내용 */
  children: React.ReactNode;
  /** 배지 스타일 변형 */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  /** 배지 크기 */
  size?: 'sm' | 'md' | 'lg';
  /** 점(dot) 표시 */
  dot?: boolean;
  /** 커스텀 클래스 */
  className?: string;
}

const variantStyles = {
  default: 'bg-slate-100 text-slate-700 border-slate-200',
  primary: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  success: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  warning: 'bg-amber-100 text-amber-700 border-amber-200',
  danger: 'bg-red-100 text-red-700 border-red-200',
  info: 'bg-blue-100 text-blue-700 border-blue-200',
};

const dotStyles = {
  default: 'bg-slate-500',
  primary: 'bg-indigo-500',
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
  info: 'bg-blue-500',
};

const sizeStyles = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  dot = false,
  className = '',
}) => {
  return (
    <span
      className={cn(
        // 기본 스타일
        'inline-flex items-center gap-1.5',
        'font-semibold rounded-full border',
        'whitespace-nowrap',
        // Variant 스타일
        variantStyles[variant],
        // Size 스타일
        sizeStyles[size],
        // 커스텀 클래스
        className
      )}
    >
      {/* Dot */}
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            dotStyles[variant]
          )}
        />
      )}
      {children}
    </span>
  );
};
