/**
 * Select Component
 *
 * 재사용 가능한 셀렉트 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Select label="Country" options={countryOptions} />
 *
 * @example
 * <Select
 *   label="Category"
 *   options={[
 *     { value: '1', label: 'Tech' },
 *     { value: '2', label: 'Finance' },
 *   ]}
 *   error="Please select a category"
 * />
 */

import React from 'react';
import { ChevronDown, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  /** 라벨 텍스트 */
  label?: string;
  /** 옵션 목록 */
  options: SelectOption[];
  /** 에러 메시지 */
  error?: string;
  /** 도움말 텍스트 */
  helperText?: string;
  /** 전체 너비 */
  fullWidth?: boolean;
  /** 플레이스홀더 */
  placeholder?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      label,
      options,
      error,
      helperText,
      fullWidth = true,
      placeholder = 'Select an option',
      className = '',
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

        {/* Select 필드 래퍼 */}
        <div className="relative">
          <select
            ref={ref}
            className={cn(
              // 기본 스타일
              'px-4 py-2.5 pr-10 rounded-xl border',
              'bg-white text-slate-900',
              'transition-all duration-200',
              'focus:outline-none focus:ring-2',
              'appearance-none cursor-pointer',
              'w-full',
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
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>

          {/* 드롭다운 아이콘 */}
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
        </div>

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

Select.displayName = 'Select';
