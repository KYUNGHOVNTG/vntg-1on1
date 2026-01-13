/**
 * Card Component
 *
 * 콘텐츠를 담는 카드 컴포넌트 (2026 모던 핀테크 디자인)
 *
 * @example
 * <Card>
 *   <CardHeader>Title</CardHeader>
 *   <CardBody>Content</CardBody>
 *   <CardFooter>Footer</CardFooter>
 * </Card>
 *
 * @example
 * <Card hover>
 *   <CardBody>Hoverable card</CardBody>
 * </Card>
 */

import React from 'react';
import { cn } from '@/utils/cn';

interface CardProps {
  /** 자식 요소 */
  children: React.ReactNode;
  /** 커스텀 클래스 */
  className?: string;
  /** 호버 효과 */
  hover?: boolean;
  /** 패딩 제거 */
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  noPadding = false,
}) => {
  return (
    <div
      className={cn(
        // 기본 스타일
        'bg-white rounded-2xl border border-slate-200 shadow-sm',
        // 패딩
        !noPadding && 'p-6',
        // 호버 효과
        hover && 'transition-all duration-200 hover:shadow-lg hover:-translate-y-1',
        // 커스텀 클래스
        className
      )}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({
  children,
  className = '',
}) => {
  return (
    <div
      className={cn(
        'pb-4 border-b border-slate-200',
        className
      )}
    >
      {children}
    </div>
  );
};

export const CardBody: React.FC<CardProps> = ({
  children,
  className = '',
}) => {
  return (
    <div
      className={cn(
        'py-4',
        className
      )}
    >
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardProps> = ({
  children,
  className = '',
}) => {
  return (
    <div
      className={cn(
        'pt-4 border-t border-slate-200',
        className
      )}
    >
      {children}
    </div>
  );
};
