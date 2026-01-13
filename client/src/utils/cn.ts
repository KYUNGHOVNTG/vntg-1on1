/**
 * cn (classNames) 유틸리티
 *
 * Tailwind CSS 클래스를 조건부로 병합하는 헬퍼 함수
 * clsx + tailwind-merge를 사용하여 클래스 충돌 방지
 *
 * @example
 * cn('px-4 py-2', 'bg-blue-500', disabled && 'opacity-50')
 * // → 'px-4 py-2 bg-blue-500 opacity-50'
 *
 * @example
 * cn('px-2', 'px-4') // → 'px-4' (뒤의 px-4가 우선)
 */

type ClassValue = string | number | boolean | undefined | null | ClassValue[];

/**
 * 간단한 클래스 병합 함수 (clsx 대체)
 */
function clsx(...classes: ClassValue[]): string {
  const result: string[] = [];

  for (const cls of classes) {
    if (!cls) continue;

    if (typeof cls === 'string' || typeof cls === 'number') {
      result.push(String(cls));
    } else if (Array.isArray(cls)) {
      const nested = clsx(...cls);
      if (nested) result.push(nested);
    }
  }

  return result.join(' ');
}

/**
 * Tailwind 클래스 충돌 제거 (간단 버전)
 *
 * 동일한 prefix를 가진 클래스가 여러 개 있을 경우,
 * 마지막 클래스만 유지합니다.
 *
 * 예: 'px-2 px-4' → 'px-4'
 */
function twMerge(classNames: string): string {
  const classes = classNames.split(' ').filter(Boolean);
  const merged = new Map<string, string>();

  // Tailwind prefix 패턴
  const prefixPattern = /^([a-z-]+?)(?:-|$)/;

  for (const cls of classes) {
    const match = cls.match(prefixPattern);
    if (match) {
      const prefix = match[1];
      merged.set(prefix, cls);
    } else {
      merged.set(cls, cls);
    }
  }

  return Array.from(merged.values()).join(' ');
}

/**
 * 클래스 병합 + Tailwind 충돌 제거
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(...inputs));
}
