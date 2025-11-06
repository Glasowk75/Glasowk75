"""
트레이딩 AI 서버
- 패턴 기반 신호 분석
- REST API 제공
- 백테스트 결과 추적
"""

from fastapi import FastAPI
from datetime import datetime
import json
import sqlite3
import pandas as pd
import os

app = FastAPI()

class TradingAIServer:
    def __init__(self):
        self.db_path = 'trading_knowledge.db'
        self.patterns = []
        self.load_patterns()
        
    def load_patterns(self):
        """저장된 패턴 로드"""
        if not os.path.exists(self.db_path):
            print(f"⚠️ 데이터베이스가 없습니다. pattern_learning_system.py를 먼저 실행하세요.")
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 테이블 존재 확인
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='patterns'
        """)
        
        if not cursor.fetchone():
            print("⚠️ patterns 테이블이 없습니다. 학습을 먼저 실행하세요.")
            conn.close()
            return
        
        # 패턴 로드
        cursor.execute("""
            SELECT pattern_name, conditions, win_rate_10, avg_return_10, confidence_score 
            FROM patterns 
            WHERE confidence_score > 50 
            ORDER BY confidence_score DESC
            LIMIT 20
        """)
        
        self.patterns = []
        for row in cursor.fetchall():
            self.patterns.append({
                'name': row[0],
                'conditions': json.loads(row[1]) if row[1] else {},
                'win_rate': row[2],
                'avg_return': row[3],
                'confidence': row[4]
            })
        
        conn.close()
        print(f"✅ {len(self.patterns)}개 패턴 로드 완료")
        
        if self.patterns:
            print("\n📊 상위 5개 패턴:")
            for i, p in enumerate(self.patterns[:5], 1):
                print(f"  {i}. {p['name']}: 승률 {p['win_rate']:.1f}%, 신뢰도 {p['confidence']:.1f}")
    
    def check_patterns(self, data):
        """현재 데이터가 패턴에 맞는지 체크"""
        matched_patterns = []
        
        for pattern in self.patterns:
            if self.match_pattern(data, pattern['conditions']):
                matched_patterns.append(pattern)
        
        return matched_patterns
    
    def match_pattern(self, data, conditions):
        """패턴 조건 매칭"""
        if not conditions:
            return False
            
        for key, value in conditions.items():
            if 'rsi' in key.lower():
                if '<' in str(value):
                    threshold = float(str(value).replace('<', '').strip())
                    if data.get('rsi', 100) >= threshold:
                        return False
                elif '>' in str(value):
                    threshold = float(str(value).replace('>', '').strip())
                    if data.get('rsi', 0) <= threshold:
                        return False
            
            elif 'adx' in key.lower():
                if '>' in str(value):
                    threshold = float(str(value).replace('>', '').strip())
                    if data.get('adx', 0) <= threshold:
                        return False
            
            elif 'sma' in key.lower():
                if '<' in str(value):
                    threshold = float(str(value).replace('<', '').replace('%', '').strip())
                    if abs(data.get('dist_sma20', 100)) >= threshold:
                        return False
        
        return True
    
    def get_statistics(self):
        """전체 통계 반환"""
        if not os.path.exists(self.db_path):
            return {}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 전체 패턴 수
        cursor.execute("SELECT COUNT(*) FROM patterns")
        result = cursor.fetchone()
        stats['total_patterns'] = result[0] if result else 0
        
        # 평균 승률
        cursor.execute("SELECT AVG(win_rate_10) FROM patterns WHERE confidence_score > 50")
        result = cursor.fetchone()
        stats['avg_win_rate'] = result[0] if result and result[0] else 0
        
        # 최고 패턴
        cursor.execute("""
            SELECT pattern_name, win_rate_10, confidence_score 
            FROM patterns 
            ORDER BY confidence_score DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            stats['best_pattern'] = {
                'name': result[0],
                'win_rate': result[1],
                'confidence': result[2]
            }
        
        conn.close()
        return stats

# 서버 인스턴스
ai_server = TradingAIServer()

@app.get("/")
async def root():
    """메인 페이지"""
    return {
        "message": "Trading AI Server",
        "version": "1.0",
        "patterns_loaded": len(ai_server.patterns),
        "endpoints": {
            "/status": "시스템 상태",
            "/patterns": "패턴 목록",
            "/analyze": "데이터 분석 (POST)",
            "/stats": "통계",
            "/docs": "API 문서"
        }
    }

@app.get("/status")
async def get_status():
    """시스템 상태 확인"""
    stats = ai_server.get_statistics()
    
    return {
        'status': 'running',
        'patterns_loaded': len(ai_server.patterns),
        'total_patterns': stats.get('total_patterns', 0),
        'avg_win_rate': round(stats.get('avg_win_rate', 0), 1),
        'best_pattern': stats.get('best_pattern', None),
        'database': os.path.exists(ai_server.db_path)
    }

@app.get("/patterns")
async def get_patterns():
    """패턴 목록 반환"""
    return {
        'count': len(ai_server.patterns),
        'patterns': ai_server.patterns
    }

@app.post("/analyze")
async def analyze_data(data: dict):
    """데이터 분석 - 패턴 매칭"""
    
    # 패턴 체크
    matched = ai_server.check_patterns(data)
    
    response = {
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'matched_patterns': []
    }
    
    if matched:
        # 신뢰도 순으로 정렬
        matched.sort(key=lambda x: x['confidence'], reverse=True)
        
        response['matched_patterns'] = [{
            'pattern': p['name'],
            'confidence': round(p['confidence'], 1),
            'win_rate': round(p['win_rate'], 1),
            'expected_return': round(p['avg_return'], 2)
        } for p in matched[:3]]  # 상위 3개만
        
        best = matched[0]
        response['recommendation'] = {
            'action': 'BUY' if best['avg_return'] > 0 else 'WAIT',
            'pattern': best['name'],
            'confidence': round(best['confidence'], 1)
        }
    else:
        response['recommendation'] = {
            'action': 'WAIT',
            'reason': 'No matching patterns'
        }
    
    return response

@app.get("/stats")
async def get_statistics():
    """통계 정보"""
    stats = ai_server.get_statistics()
    
    # 패턴별 분포
    pattern_distribution = {}
    if ai_server.patterns:
        for p in ai_server.patterns:
            if p['win_rate'] >= 70:
                pattern_distribution['high'] = pattern_distribution.get('high', 0) + 1
            elif p['win_rate'] >= 60:
                pattern_distribution['medium'] = pattern_distribution.get('medium', 0) + 1
            else:
                pattern_distribution['low'] = pattern_distribution.get('low', 0) + 1
    
    return {
        'total_patterns': stats.get('total_patterns', 0),
        'loaded_patterns': len(ai_server.patterns),
        'avg_win_rate': round(stats.get('avg_win_rate', 0), 1),
        'best_pattern': stats.get('best_pattern'),
        'pattern_distribution': pattern_distribution
    }

@app.post("/reload")
async def reload_patterns():
    """패턴 다시 로드"""
    ai_server.load_patterns()
    return {
        'status': 'reloaded',
        'patterns_loaded': len(ai_server.patterns)
    }

# Pine Script Alert 포맷 생성
def generate_pine_alert_format():
    """TradingView에서 사용할 Alert 메시지 포맷"""
    return """
// Pine Script Alert 메시지 설정
// Alert 조건에서 이 JSON을 메시지로 사용:
{
    "symbol": "{{ticker}}",
    "price": {{close}},
    "rsi": {{plot_0}},
    "adx": {{plot_1}},
    "dist_sma20": (({{close}} - {{plot_2}}) / {{plot_2}} * 100),
    "time": "{{time}}"
}
"""

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("🚀 Trading AI Server")
    print("="*50)
    
    # DB 체크
    if not os.path.exists('trading_knowledge.db'):
        print("\n⚠️ 경고: 데이터베이스가 없습니다!")
        print("먼저 다음 명령을 실행하세요:")
        print("  python pattern_learning_system.py")
        print("")
    
    # Pine Script 포맷 출력
    print("\n📌 TradingView Alert 설정:")
    print(generate_pine_alert_format())
    
    print("\n🌐 서버 시작...")
    print("📡 API 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    # 서버 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)