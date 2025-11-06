"""
BTC 패턴 자동 학습 시스템
- 패턴 발견
- 승률 계산  
- 지식 축적
- Pine Script 코드 생성
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import sqlite3
import os
import sys

class PatternLearningSystem:
    def __init__(self):
        self.db_path = 'trading_knowledge.db'
        self.patterns_path = 'discovered_patterns.json'
        self.csv_folder = 'data/'  # CSV 파일들 저장 폴더
        self.init_database()
        self.load_existing_patterns()
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 패턴 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                conditions TEXT,
                win_rate_5 REAL,
                win_rate_10 REAL,
                win_rate_30 REAL,
                avg_return_5 REAL,
                avg_return_10 REAL,
                avg_return_30 REAL,
                sample_size INTEGER,
                confidence_score REAL,
                discovered_date DATETIME,
                last_tested DATETIME
            )
        ''')
        
        # 학습 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                csv_file TEXT,
                patterns_found INTEGER,
                avg_confidence REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_existing_patterns(self):
        """기존 패턴 로드"""
        if os.path.exists(self.patterns_path):
            with open(self.patterns_path, 'r', encoding='utf-8') as f:
                self.discovered_patterns = json.load(f)
        else:
            self.discovered_patterns = {
                'version': 1,
                'last_updated': str(datetime.now()),
                'patterns': [],
                'best_combinations': [],
                'learning_history': []
            }
    
    def process_csv_file(self, csv_path):
        """CSV 파일 처리"""
        print(f"\n📊 파일 분석 중: {csv_path}")
        
        # CSV 읽기
        df = pd.read_csv(csv_path)
        
        # 컬럼명 자동 인식 또는 표준화
        if 'rsi_short' not in df.columns:
            # 컬럼명 매핑 (필요시 수정)
            df.columns = ['time', 'open', 'high', 'low', 'close', 'rsi_short', 'rsi_long', 
                          'plot1', 'plot2', 'adx', 'plus_di', 'minus_di', 'my_atr', 'plot3', 'plot4']
        
        # 시간 인덱스 설정
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        # 추가 지표 계산
        df['sma20'] = df['close'].rolling(20).mean()
        df['sma60'] = df['close'].rolling(60).mean()
        df['sma200'] = df['close'].rolling(200).mean()
        df['dist_sma20'] = (df['close'] - df['sma20']) / df['sma20'] * 100
        df['dist_sma60'] = (df['close'] - df['sma60']) / df['sma60'] * 100
        
        return df
    
    def discover_patterns(self, df):
        """데이터에서 패턴 자동 발견"""
        patterns = []
        
        # 1. 단일 지표 패턴
        single_patterns = self.find_single_indicator_patterns(df)
        patterns.extend(single_patterns)
        
        # 2. 2개 조합 패턴
        combo2_patterns = self.find_2_indicator_combinations(df)
        patterns.extend(combo2_patterns)
        
        # 3. 3개 조합 패턴
        combo3_patterns = self.find_3_indicator_combinations(df)
        patterns.extend(combo3_patterns)
        
        # 4. 피봇 기반 패턴
        pivot_patterns = self.find_pivot_patterns(df)
        patterns.extend(pivot_patterns)
        
        return patterns
    
    def find_single_indicator_patterns(self, df):
        """단일 지표 패턴 찾기"""
        patterns = []
        
        # RSI 구간별
        for rsi_low in [20, 25, 30, 35]:
            for rsi_high in [65, 70, 75, 80]:
                # 과매도
                mask = df['rsi_short'] < rsi_low
                if mask.sum() >= 10:
                    result = self.calculate_pattern_performance(df, mask)
                    if result and result['win_rate_10'] > 55:
                        patterns.append({
                            'name': f'RSI_Below_{rsi_low}',
                            'conditions': {'rsi': f'< {rsi_low}'},
                            **result
                        })
                
                # 과매수
                mask = df['rsi_short'] > rsi_high
                if mask.sum() >= 10:
                    result = self.calculate_pattern_performance(df, mask)
                    if result and result['win_rate_10'] > 55:
                        patterns.append({
                            'name': f'RSI_Above_{rsi_high}',
                            'conditions': {'rsi': f'> {rsi_high}'},
                            **result
                        })
        
        # ADX 강도별
        for adx_level in [20, 25, 30, 35, 40]:
            mask = df['adx'] > adx_level
            if mask.sum() >= 10:
                result = self.calculate_pattern_performance(df, mask)
                if result and result['win_rate_10'] > 55:
                    patterns.append({
                        'name': f'Strong_Trend_ADX_{adx_level}',
                        'conditions': {'adx': f'> {adx_level}'},
                        **result
                    })
        
        return patterns
    
    def find_2_indicator_combinations(self, df):
        """2개 지표 조합 패턴"""
        patterns = []
        
        # RSI + ADX 조합
        for rsi_threshold in [25, 30, 35]:
            for adx_threshold in [20, 25, 30, 35, 40]:
                mask = (df['rsi_short'] < rsi_threshold) & (df['adx'] > adx_threshold)
                if mask.sum() >= 10:
                    result = self.calculate_pattern_performance(df, mask)
                    if result and result['win_rate_10'] > 60:
                        patterns.append({
                            'name': f'RSI{rsi_threshold}_ADX{adx_threshold}',
                            'conditions': {
                                'rsi': f'< {rsi_threshold}',
                                'adx': f'> {adx_threshold}'
                            },
                            **result
                        })
        
        # RSI + SMA 거리
        for rsi_threshold in [30, 70]:
            for sma_dist in [1, 2, 3]:
                if rsi_threshold == 30:
                    mask = (df['rsi_short'] < rsi_threshold) & (abs(df['dist_sma20']) < sma_dist)
                else:
                    mask = (df['rsi_short'] > rsi_threshold) & (abs(df['dist_sma20']) < sma_dist)
                
                if mask.sum() >= 10:
                    result = self.calculate_pattern_performance(df, mask)
                    if result and result['win_rate_10'] > 60:
                        patterns.append({
                            'name': f'RSI{rsi_threshold}_SMA{sma_dist}',
                            'conditions': {
                                'rsi': f'{"<" if rsi_threshold==30 else ">"} {rsi_threshold}',
                                'sma_distance': f'< {sma_dist}%'
                            },
                            **result
                        })
        
        return patterns
    
    def find_3_indicator_combinations(self, df):
        """3개 지표 조합 - 최고 성능 패턴"""
        patterns = []
        
        # RSI + ADX + SMA
        best_combos = [
            {'rsi': 30, 'adx': 30, 'sma': 3, 'op': '<'},
            {'rsi': 30, 'adx': 35, 'sma': 2, 'op': '<'},
            {'rsi': 35, 'adx': 25, 'sma': 3, 'op': '<'},
            {'rsi': 70, 'adx': 30, 'sma': 2, 'op': '>'},
        ]
        
        for combo in best_combos:
            if combo['op'] == '<':
                mask = (
                    (df['rsi_short'] < combo['rsi']) & 
                    (df['adx'] > combo['adx']) & 
                    (abs(df['dist_sma20']) < combo['sma'])
                )
            else:
                mask = (
                    (df['rsi_short'] > combo['rsi']) & 
                    (df['adx'] > combo['adx']) & 
                    (abs(df['dist_sma20']) < combo['sma'])
                )
            
            if mask.sum() >= 10:
                result = self.calculate_pattern_performance(df, mask)
                if result and result['win_rate_10'] > 65:
                    patterns.append({
                        'name': f'Triple_RSI{combo["rsi"]}_{combo["op"]}_ADX{combo["adx"]}_SMA{combo["sma"]}',
                        'conditions': {
                            'rsi': f'{combo["op"]} {combo["rsi"]}',
                            'adx': f'> {combo["adx"]}',
                            'sma_distance': f'< {combo["sma"]}%'
                        },
                        **result
                    })
        
        return patterns
    
    def find_pivot_patterns(self, df):
        """피봇 기반 패턴"""
        patterns = []
        
        # 피봇 포인트 찾기
        pivots = self.find_pivot_points(df)
        
        # 피봇 겹침 분석 (간단 버전)
        if len(pivots['lows']) > 10:
            # 최근 저점 피봇들의 가격 분포
            recent_lows = [p['price'] for p in pivots['lows'][-20:]]
            avg_low = np.mean(recent_lows)
            
            # 평균 저점 근처에서 RSI 신호
            mask = (abs(df['close'] - avg_low) / avg_low < 0.02) & (df['rsi_short'] < 35)
            if mask.sum() >= 5:
                result = self.calculate_pattern_performance(df, mask)
                if result and result['win_rate_10'] > 60:
                    patterns.append({
                        'name': 'Pivot_Support_RSI',
                        'conditions': {
                            'near_pivot_support': True,
                            'rsi': '< 35'
                        },
                        **result
                    })
        
        return patterns
    
    def find_pivot_points(self, df, left_bars=5, right_bars=5):
        """피봇 포인트 찾기"""
        pivots = {'highs': [], 'lows': []}
        
        for i in range(left_bars, len(df) - right_bars):
            # 피봇 하이
            window_high = df['high'].iloc[i-left_bars:i+right_bars+1]
            if df['high'].iloc[i] == window_high.max():
                pivots['highs'].append({
                    'bar': i,
                    'price': df['high'].iloc[i],
                    'time': df.index[i]
                })
            
            # 피봇 로우
            window_low = df['low'].iloc[i-left_bars:i+right_bars+1]
            if df['low'].iloc[i] == window_low.min():
                pivots['lows'].append({
                    'bar': i,
                    'price': df['low'].iloc[i],
                    'time': df.index[i]
                })
        
        return pivots
    
    def calculate_pattern_performance(self, df, mask):
        """패턴 성과 계산"""
        indices = df[mask].index
        returns = {'5': [], '10': [], '30': []}
        
        for idx in indices:
            pos = df.index.get_loc(idx)
            
            for period in [5, 10, 30]:
                if pos + period < len(df):
                    ret = ((df['close'].iloc[pos+period] / df['close'].iloc[pos]) - 1) * 100
                    returns[str(period)].append(ret)
        
        if not returns['10']:
            return None
        
        result = {
            'sample_size': len(returns['10']),
            'win_rate_5': sum(1 for r in returns['5'] if r > 0) / len(returns['5']) * 100 if returns['5'] else 0,
            'win_rate_10': sum(1 for r in returns['10'] if r > 0) / len(returns['10']) * 100,
            'win_rate_30': sum(1 for r in returns['30'] if r > 0) / len(returns['30']) * 100 if returns['30'] else 0,
            'avg_return_5': np.mean(returns['5']) if returns['5'] else 0,
            'avg_return_10': np.mean(returns['10']),
            'avg_return_30': np.mean(returns['30']) if returns['30'] else 0,
            'max_return': max(returns['10']),
            'min_return': min(returns['10']),
            'sharpe_ratio': np.mean(returns['10']) / np.std(returns['10']) if np.std(returns['10']) > 0 else 0
        }
        
        # 신뢰도 점수 계산
        result['confidence_score'] = self.calculate_confidence(result)
        
        return result
    
    def calculate_confidence(self, result):
        """패턴 신뢰도 점수 (0-100)"""
        score = 0
        
        # 승률 (최대 40점)
        score += min(40, (result['win_rate_10'] - 50) * 2)
        
        # 샘플 크기 (최대 20점)
        score += min(20, result['sample_size'] / 2)
        
        # 평균 수익률 (최대 20점)
        score += min(20, max(0, result['avg_return_10'] * 10))
        
        # 일관성 - Sharpe Ratio (최대 20점)
        score += min(20, max(0, result['sharpe_ratio'] * 10))
        
        return max(0, min(100, score))
    
    def save_patterns(self, patterns):
        """발견된 패턴 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern in patterns:
            if pattern and pattern['confidence_score'] > 50:
                cursor.execute('''
                    INSERT OR REPLACE INTO patterns 
                    (pattern_name, conditions, win_rate_5, win_rate_10, win_rate_30,
                     avg_return_5, avg_return_10, avg_return_30, sample_size, 
                     confidence_score, discovered_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern['name'],
                    json.dumps(pattern['conditions']),
                    pattern['win_rate_5'],
                    pattern['win_rate_10'],
                    pattern['win_rate_30'],
                    pattern['avg_return_5'],
                    pattern['avg_return_10'],
                    pattern['avg_return_30'],
                    pattern['sample_size'],
                    pattern['confidence_score'],
                    datetime.now()
                ))
        
        conn.commit()
        conn.close()
        
        # JSON 파일로도 저장
        self.discovered_patterns['patterns'] = patterns
        self.discovered_patterns['last_updated'] = str(datetime.now())
        
        with open(self.patterns_path, 'w', encoding='utf-8') as f:
            json.dump(self.discovered_patterns, f, indent=2, ensure_ascii=False)
    
    def generate_pine_script(self, top_patterns):
        """상위 패턴들로 Pine Script 생성"""
        script = '''// Auto-generated Strategy
//@version=5
strategy("AI Discovered Patterns", overlay=true)

// === 입력 설정 ===
usePattern1 = input.bool(true, "Pattern 1")
usePattern2 = input.bool(true, "Pattern 2")
usePattern3 = input.bool(true, "Pattern 3")

// === 지표 계산 ===
rsi = ta.rsi(close, 14)
[diplus, diminus, adx] = ta.dmi(14, 14)
sma20 = ta.sma(close, 20)
dist_sma20 = (close - sma20) / sma20 * 100

// === 자동 발견된 패턴들 ===
'''
        
        for i, pattern in enumerate(top_patterns[:3], 1):
            conditions = pattern['conditions']
            condition_checks = []
            
            for key, value in conditions.items():
                if 'rsi' in key:
                    if '<' in value:
                        threshold = value.replace('<', '').strip()
                        condition_checks.append(f'rsi < {threshold}')
                    elif '>' in value:
                        threshold = value.replace('>', '').strip()
                        condition_checks.append(f'rsi > {threshold}')
                
                elif 'adx' in key:
                    if '>' in value:
                        threshold = value.replace('>', '').strip()
                        condition_checks.append(f'adx > {threshold}')
                
                elif 'sma_distance' in key:
                    if '<' in value:
                        threshold = value.replace('<', '').replace('%', '').strip()
                        condition_checks.append(f'math.abs(dist_sma20) < {threshold}')
            
            condition_string = ' and '.join(condition_checks) if condition_checks else 'false'
            
            script += f'''
// Pattern {i}: {pattern['name']}
// 승률: {pattern['win_rate_10']:.1f}%, 평균 수익: {pattern['avg_return_10']:.2f}%
pattern{i} = {condition_string}
'''
        
        script += '''
// === 진입 신호 ===
longSignal = (usePattern1 and pattern1) or (usePattern2 and pattern2) or (usePattern3 and pattern3)

// === 전략 실행 ===
if longSignal
    strategy.entry("Long", strategy.long)
    strategy.exit("Exit", "Long", profit=close*0.02, loss=close*0.01)  // 2% 익절, 1% 손절

// === 시각화 ===
plotshape(longSignal, style=shape.triangleup, location=location.belowbar, color=color.green)
'''
        
        return script
    
    def batch_process_csv_files(self):
        """data 폴더의 모든 CSV 파일 처리"""
        if not os.path.exists(self.csv_folder):
            os.makedirs(self.csv_folder)
            print(f"📁 {self.csv_folder} 폴더를 생성했습니다. CSV 파일을 넣어주세요.")
            return
        
        csv_files = [f for f in os.listdir(self.csv_folder) if f.endswith('.csv')]
        
        if not csv_files:
            print(f"⚠️ {self.csv_folder} 폴더에 CSV 파일이 없습니다.")
            return
        
        all_patterns = []
        
        for csv_file in csv_files:
            csv_path = os.path.join(self.csv_folder, csv_file)
            df = self.process_csv_file(csv_path)
            patterns = self.discover_patterns(df)
            all_patterns.extend(patterns)
            
            # 학습 이력 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_history 
                (timestamp, csv_file, patterns_found, avg_confidence)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now(),
                csv_file,
                len([p for p in patterns if p]),
                np.mean([p['confidence_score'] for p in patterns if p]) if patterns else 0
            ))
            conn.commit()
            conn.close()
            
            print(f"✅ {csv_file}: {len([p for p in patterns if p])}개 패턴 발견")
        
        return all_patterns


# === 메인 실행 ===
if __name__ == "__main__":
    print("🚀 패턴 학습 시스템 시작...")
    
    system = PatternLearningSystem()
    
    # 명령줄 인수 확인
    if len(sys.argv) > 1:
        # 특정 CSV 파일 처리
        csv_file = sys.argv[1]
        if os.path.exists(csv_file):
            df = system.process_csv_file(csv_file)
            patterns = system.discover_patterns(df)
            print(f"✅ {len([p for p in patterns if p])}개 패턴 발견!")
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
    else:
        # 기본: 현재 폴더의 BTC 파일 또는 data 폴더 처리
        if os.path.exists('BITGET_BTCUSDT_P_60.csv'):
            df = system.process_csv_file('BITGET_BTCUSDT_P_60.csv')
            patterns = system.discover_patterns(df)
        else:
            # data 폴더의 모든 CSV 처리
            patterns = system.batch_process_csv_files()
    
    if patterns:
        # 패턴 저장
        system.save_patterns(patterns)
        print("💾 데이터베이스에 저장 완료")
        
        # Pine Script 생성
        top_patterns = sorted([p for p in patterns if p], 
                             key=lambda x: x['confidence_score'], 
                             reverse=True)[:3]
        
        if top_patterns:
            pine_script = system.generate_pine_script(top_patterns)
            
            with open('auto_strategy.pine', 'w', encoding='utf-8') as f:
                f.write(pine_script)
            print("📝 Pine Script 전략 생성 완료: auto_strategy.pine")
            
            print("\n🎯 상위 3개 패턴:")
            for i, p in enumerate(top_patterns[:3], 1):
                print(f"{i}. {p['name']}: 승률 {p['win_rate_10']:.1f}%, 신뢰도 {p['confidence_score']:.1f}")
    else:
        print("⚠️ 패턴을 찾을 수 없습니다. CSV 파일을 확인해주세요.")