/**
 * Dashboard Page
 *
 * 메인 대시보드 페이지 - 출퇴근 관리 및 근태 현황
 */

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/core/layout';
import { Clock, Calendar, Timer, TrendingUp, Briefcase } from 'lucide-react';

export const Dashboard: React.FC = () => {
  // 현재 시간 상태 (실시간 시계)
  const [currentTime, setCurrentTime] = useState(new Date());

  // 근무 상태 (임시 상태 - 추후 API 연동)
  const [isWorking, setIsWorking] = useState(false);

  // 근무 시작 시간
  const [workStartTime, setWorkStartTime] = useState<Date | null>(null);

  // 타이머 (근무 중일 때 경과 시간)
  const [elapsedTime, setElapsedTime] = useState(0);

  // 실시간 시계 업데이트
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 근무 시간 타이머 업데이트
  useEffect(() => {
    if (isWorking && workStartTime) {
      const timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - workStartTime.getTime()) / 1000);
        setElapsedTime(elapsed);
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [isWorking, workStartTime]);

  // 출근 처리
  const handleCheckIn = () => {
    setIsWorking(true);
    setWorkStartTime(new Date());
    setElapsedTime(0);
  };

  // 퇴근 처리
  const handleCheckOut = () => {
    setIsWorking(false);
    setWorkStartTime(null);
    setElapsedTime(0);
  };

  // 시간 포맷팅 함수
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  // 경과 시간 포맷팅 (초 -> HH:MM:SS)
  const formatElapsedTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
        <div className="max-w-6xl mx-auto space-y-6">

          {/* 상단 카드: 날짜 및 시간 */}
          <div className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-3xl p-8 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Calendar className="text-white w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-slate-900">
                    {formatDate(currentTime)}
                  </h2>
                  <p className="text-slate-500 text-sm mt-1">오늘도 화이팅!</p>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-gradient-to-r from-indigo-50 to-purple-50 px-6 py-4 rounded-2xl border border-indigo-100">
                <Clock className="text-indigo-600 w-6 h-6" />
                <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 tabular-nums">
                  {formatTime(currentTime)}
                </span>
              </div>
            </div>
          </div>

          {/* 출퇴근 액션 버튼 & 타이머 */}
          <div className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-3xl p-12 shadow-lg">
            <div className="text-center space-y-8">

              {/* 근무 중일 때 타이머 표시 */}
              {isWorking && (
                <div className="inline-flex items-center gap-3 bg-gradient-to-r from-emerald-50 to-teal-50 px-8 py-4 rounded-2xl border-2 border-emerald-200 animate-pulse">
                  <Timer className="text-emerald-600 w-7 h-7" />
                  <div>
                    <p className="text-sm text-emerald-700 font-semibold">현재 근무 시간</p>
                    <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600 tabular-nums">
                      {formatElapsedTime(elapsedTime)}
                    </p>
                  </div>
                </div>
              )}

              {/* 액션 버튼 */}
              <div className="flex items-center justify-center gap-6">
                {/* 출근하기 버튼 */}
                <button
                  onClick={handleCheckIn}
                  disabled={isWorking}
                  className={`
                    group relative px-16 py-8 rounded-3xl text-2xl font-bold
                    transition-all duration-300 shadow-2xl
                    ${isWorking
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105 hover:shadow-indigo-300 active:scale-95'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <Briefcase className="w-8 h-8" />
                    <span>출근하기</span>
                  </div>
                  {!isWorking && (
                    <div className="absolute inset-0 rounded-3xl bg-white opacity-0 group-hover:opacity-20 transition-opacity"></div>
                  )}
                </button>

                {/* 퇴근하기 버튼 */}
                <button
                  onClick={handleCheckOut}
                  disabled={!isWorking}
                  className={`
                    group relative px-16 py-8 rounded-3xl text-2xl font-bold
                    transition-all duration-300 shadow-2xl
                    ${!isWorking
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-rose-500 to-orange-500 text-white hover:from-rose-600 hover:to-orange-600 hover:scale-105 hover:shadow-rose-300 active:scale-95'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <Briefcase className="w-8 h-8" />
                    <span>퇴근하기</span>
                  </div>
                  {isWorking && (
                    <div className="absolute inset-0 rounded-3xl bg-white opacity-0 group-hover:opacity-20 transition-opacity"></div>
                  )}
                </button>
              </div>

              <p className="text-slate-500 text-sm">
                {isWorking
                  ? '근무 중입니다. 퇴근 시 "퇴근하기" 버튼을 눌러주세요.'
                  : '출근 시 "출근하기" 버튼을 눌러주세요.'
                }
              </p>
            </div>
          </div>

          {/* 정보 요약 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* 이번 주 누적 근무 시간 */}
            <div className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                    <TrendingUp className="w-4 h-4" />
                    <span>이번 주 누적 근무 시간</span>
                  </div>
                  <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600 tabular-nums">
                    32:45
                  </p>
                  <p className="text-slate-400 text-sm mt-2">목표: 40시간</p>
                </div>
                <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-3xl flex items-center justify-center">
                  <Clock className="w-12 h-12 text-blue-600" />
                </div>
              </div>

              {/* 진행률 바 */}
              <div className="mt-6 bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-500"
                  style={{ width: '82%' }}
                ></div>
              </div>
            </div>

            {/* 잔여 연차 일수 */}
            <div className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                    <Calendar className="w-4 h-4" />
                    <span>잔여 연차 일수</span>
                  </div>
                  <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600 tabular-nums">
                    12일
                  </p>
                  <p className="text-slate-400 text-sm mt-2">총 연차: 15일</p>
                </div>
                <div className="w-24 h-24 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-3xl flex items-center justify-center">
                  <Briefcase className="w-12 h-12 text-emerald-600" />
                </div>
              </div>

              {/* 진행률 바 */}
              <div className="mt-6 bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
                  style={{ width: '80%' }}
                ></div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </MainLayout>
  );
};
