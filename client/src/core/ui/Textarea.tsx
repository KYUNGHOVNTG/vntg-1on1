/**
 * Textarea Component
 *
 * 재사용 가능한 텍스트 영역 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Textarea
 *   label="Description"
 *   placeholder="Enter description"
 *   rows={5}
 * />
 *
 * @example
 * <Textarea
 *   label="Comment"
 *   error="Comment must be at least 10 characters"
 *   helperText="Max 500 characters"
 * />
 */

import React from 'react';
import { AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** 라벨 텍스트 */
  label?: string;
  /** 에러 메시지 */
  error?: string;
  /** 도움말 텍스트 */
  helperText?: string;
  /** 전체 너비 */
  fullWidth?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = true,
      className = '',
      rows = 4,
      ...props
    },
    ref
  ) => {
    const hasError = !!error;

    return (
      <div className={cn('flex flex-col', fullWidth && 'w-full')}>
        {/* 라벨 */}
        {label && (
          <label className="text-sm font-medium text-slate-700 mb-1.5">
            {label}
            {props.required && (
              <span className="text-red-500 ml-1">*</span>
            )}
          </label>
        )}

        {/* Textarea 필드 */}
        <textarea
          ref={ref}
          rows={rows}
          className={cn(
            // 기본 스타일
            'px-4 py-2.5 rounded-xl border',
            'bg-white text-slate-900 placeholder:text-slate-400',
            'transition-all duration-200',
            'focus:outline-none focus:ring-2',
            'resize-vertical',
            // 일반 상태
            !hasError && [
              'border-slate-300',
              'focus:border-indigo-500 focus:ring-indigo-500/20',
            ],
            // 에러 상태
            hasError && [
              'border-red-500',
              'focus:border-red-500 focus:ring-red-500/20',
            ],
            // 비활성화 상태
            props.disabled && 'opacity-50 cursor-not-allowed bg-slate-50',
            // 커스텀 클래스
            className
          )}
          {...props}
        />

        {/* 에러 메시지 */}
        {hasError && (
          <div className="flex items-center gap-1.5 mt-1.5 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        {/* 헬퍼 텍스트 */}
        {helperText && !hasError && (
          <span className="mt-1.5 text-sm text-slate-500">{helperText}</span>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
