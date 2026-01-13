/**
 * Radio Component
 *
 * 재사용 가능한 라디오 버튼 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <RadioGroup label="Payment Method">
 *   <Radio name="payment" value="card" label="Credit Card" />
 *   <Radio name="payment" value="bank" label="Bank Transfer" />
 * </RadioGroup>
 *
 * @example
 * <Radio
 *   name="plan"
 *   value="pro"
 *   label="Pro Plan"
 *   helperText="$29/month"
 * />
 */

import React from 'react';
import { cn } from '@/utils/cn';

interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  /** 라벨 텍스트 */
  label?: string;
  /** 도움말 텍스트 */
  helperText?: string;
}

export const Radio = React.forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      label,
      helperText,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <label className="flex items-start gap-3 cursor-pointer group">
        {/* Hidden native radio */}
        <input
          ref={ref}
          type="radio"
          className="sr-only peer"
          {...props}
        />

        {/* Custom radio */}
        <div
          className={cn(
            'flex items-center justify-center',
            'w-5 h-5 mt-0.5 rounded-full border-2',
            'transition-all duration-200',
            'peer-focus:ring-2 peer-focus:ring-offset-2',
            'border-slate-300',
            'peer-checked:border-indigo-600',
            'peer-focus:ring-indigo-500/20',
            'group-hover:border-indigo-400',
            // 비활성화 상태
            props.disabled && 'opacity-50 cursor-not-allowed',
            className
          )}
        >
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-600 opacity-0 peer-checked:opacity-100 transition-opacity" />
        </div>

        {/* Label */}
        {label && (
          <div className="flex-1">
            <span className="text-sm font-medium text-slate-700 select-none">
              {label}
            </span>
            {helperText && (
              <p className="text-xs text-slate-500 mt-0.5">{helperText}</p>
            )}
          </div>
        )}
      </label>
    );
  }
);

Radio.displayName = 'Radio';

// RadioGroup wrapper component
interface RadioGroupProps {
  /** 그룹 라벨 */
  label?: string;
  /** 에러 메시지 */
  error?: string;
  /** 자식 요소 (Radio 컴포넌트들) */
  children: React.ReactNode;
  /** 커스텀 클래스 */
  className?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  label,
  error,
  children,
  className = '',
}) => {
  return (
    <div className={cn('flex flex-col', className)}>
      {/* 라벨 */}
      {label && (
        <label className="text-sm font-medium text-slate-700 mb-2">
          {label}
        </label>
      )}

      {/* Radio 버튼들 */}
      <div className="flex flex-col gap-3">
        {children}
      </div>

      {/* 에러 메시지 */}
      {error && (
        <span className="mt-2 text-sm text-red-600">{error}</span>
      )}
    </div>
  );
};
