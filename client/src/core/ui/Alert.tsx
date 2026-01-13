/**
 * Alert Component
 *
 * 알림/경고/성공 메시지 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Alert variant="success">
 *   Payment processed successfully!
 * </Alert>
 *
 * @example
 * <Alert variant="danger" title="Error" onClose={handleClose}>
 *   Failed to process payment. Please try again.
 * </Alert>
 */

import React from 'react';
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/utils/cn';

interface AlertProps {
  /** Alert 내용 */
  children: React.ReactNode;
  /** Alert 스타일 변형 */
  variant?: 'info' | 'success' | 'warning' | 'danger';
  /** Alert 제목 */
  title?: string;
  /** 닫기 버튼 콜백 */
  onClose?: () => void;
  /** 커스텀 클래스 */
  className?: string;
}

const variantStyles = {
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-900',
    icon: 'text-blue-600',
    Icon: Info,
  },
  success: {
    container: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    icon: 'text-emerald-600',
    Icon: CheckCircle,
  },
  warning: {
    container: 'bg-amber-50 border-amber-200 text-amber-900',
    icon: 'text-amber-600',
    Icon: AlertTriangle,
  },
  danger: {
    container: 'bg-red-50 border-red-200 text-red-900',
    icon: 'text-red-600',
    Icon: AlertCircle,
  },
};

export const Alert: React.FC<AlertProps> = ({
  children,
  variant = 'info',
  title,
  onClose,
  className = '',
}) => {
  const { container, icon, Icon } = variantStyles[variant];

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-xl border',
        container,
        className
      )}
      role="alert"
    >
      {/* 아이콘 */}
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', icon)} />

      {/* 내용 */}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="font-semibold mb-1">{title}</h4>
        )}
        <div className="text-sm leading-relaxed">
          {children}
        </div>
      </div>

      {/* 닫기 버튼 */}
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity"
          aria-label="Close alert"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};
