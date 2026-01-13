/**
 * Checkbox Component
 *
 * 재사용 가능한 체크박스 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Checkbox label="Agree to terms" />
 *
 * @example
 * <Checkbox
 *   label="Subscribe to newsletter"
 *   helperText="Receive updates weekly"
 *   error="You must agree to continue"
 * />
 */

import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/utils/cn';

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  /** 라벨 텍스트 */
  label?: string;
  /** 에러 메시지 */
  error?: string;
  /** 도움말 텍스트 */
  helperText?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      label,
      error,
      helperText,
      className = '',
      ...props
    },
    ref
  ) => {
    const hasError = !!error;

    return (
      <div className="flex flex-col">
        <label className="flex items-start gap-3 cursor-pointer group">
          {/* Hidden native checkbox */}
          <input
            ref={ref}
            type="checkbox"
            className="sr-only peer"
            {...props}
          />

          {/* Custom checkbox */}
          <div
            className={cn(
              'flex items-center justify-center',
              'w-5 h-5 mt-0.5 rounded-md border-2',
              'transition-all duration-200',
              'peer-focus:ring-2 peer-focus:ring-offset-2',
              // 일반 상태
              !hasError && [
                'border-slate-300',
                'peer-checked:bg-indigo-600 peer-checked:border-indigo-600',
                'peer-focus:ring-indigo-500/20',
                'group-hover:border-indigo-400',
              ],
              // 에러 상태
              hasError && [
                'border-red-500',
                'peer-checked:bg-red-600 peer-checked:border-red-600',
                'peer-focus:ring-red-500/20',
              ],
              // 비활성화 상태
              props.disabled && 'opacity-50 cursor-not-allowed',
              className
            )}
          >
            <Check className="w-3.5 h-3.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
          </div>

          {/* Label */}
          {label && (
            <div className="flex-1">
              <span className="text-sm font-medium text-slate-700 select-none">
                {label}
              </span>
              {helperText && !hasError && (
                <p className="text-xs text-slate-500 mt-0.5">{helperText}</p>
              )}
            </div>
          )}
        </label>

        {/* 에러 메시지 */}
        {hasError && (
          <span className="ml-8 mt-1 text-xs text-red-600">{error}</span>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';
