"""
트레이딩 차트 시각화
캔들스틱 + 지표 + 진입/익절 포인트
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from datetime import datetime

def plot_trade_chart(csv_path, start_date, end_date, entry_time=None, exit_time=None):
    """차트 그리기"""

    # 데이터 읽기
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if start_date <= row['time'] <= end_date:
                data.append(row)

    if not data:
        print("데이터가 없습니다.")
        return

    # 데이터 파싱
    times = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    rsi = []
    rsi2 = []
    sma60 = []
    sma200 = []
    divergence = []
    it_highs = []
    it_lows = []
    high_overlaps = []
    low_overlaps = []

    for row in data:
        times.append(row['time'].split('T')[1][:5])  # HH:MM만
        opens.append(float(row['open']))
        highs.append(float(row['high']))
        lows.append(float(row['low']))
        closes.append(float(row['close']))
        volumes.append(float(row['Volume']))
        rsi.append(float(row[' rsi']))
        rsi2.append(float(row[' rsi2 ']))
        sma60.append(float(row['SMA 60']))
        sma200.append(float(row['SMA 200']))
        divergence.append(float(row['Divergence']))

        # IT 피봇
        it_high = row['IT_High'].strip() if row['IT_High'] else None
        it_low = row['IT_Low'].strip() if row['IT_Low'] else None
        it_highs.append(float(it_high) if it_high else None)
        it_lows.append(float(it_low) if it_low else None)

        high_overlaps.append(int(row['Closest_High_Overlap']))
        low_overlaps.append(int(row['Closest_Low_Overlap']))

    # Figure 생성
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 12),
                                         gridspec_kw={'height_ratios': [3, 1, 1]})
    fig.suptitle(f'BTC/USDT 1H Chart ({start_date.split("T")[0]} ~ {end_date.split("T")[0]})',
                 fontsize=16, fontweight='bold')

    x = range(len(data))

    # ========== 메인 차트 (캔들 + SMA) ==========
    ax1.set_ylabel('Price (USDT)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # 캔들스틱
    for i in x:
        color = 'green' if closes[i] >= opens[i] else 'red'

        # 몸통
        body_height = abs(closes[i] - opens[i])
        body_bottom = min(opens[i], closes[i])
        rect = Rectangle((i - 0.4, body_bottom), 0.8, body_height,
                         facecolor=color, edgecolor=color, alpha=0.8)
        ax1.add_patch(rect)

        # 꼬리
        ax1.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1, alpha=0.8)

    # SMA
    ax1.plot(x, sma60, label='SMA60', color='blue', linewidth=2, alpha=0.7)
    ax1.plot(x, sma200, label='SMA200', color='purple', linewidth=2, alpha=0.7)

    # IT 피봇 표시
    for i in x:
        if it_highs[i]:
            ax1.scatter(i, it_highs[i], color='red', marker='v', s=100, zorder=5)
            if high_overlaps[i] >= 3:
                ax1.text(i, it_highs[i], f' {high_overlaps[i]}',
                        color='red', fontsize=8, va='bottom')
        if it_lows[i]:
            ax1.scatter(i, it_lows[i], color='green', marker='^', s=100, zorder=5)
            if low_overlaps[i] >= 3:
                ax1.text(i, it_lows[i], f' {low_overlaps[i]}',
                        color='green', fontsize=8, va='top')

    # 다이버전스 표시
    for i in x:
        if divergence[i] == 1:  # 상승 다이버전스
            ax1.annotate('Bull DIV', xy=(i, lows[i]), xytext=(i, lows[i] - 500),
                        arrowprops=dict(arrowstyle='->', color='green', lw=2),
                        fontsize=10, color='green', fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        elif divergence[i] == -1:  # 하락 다이버전스
            ax1.annotate('Bear DIV', xy=(i, highs[i]), xytext=(i, highs[i] + 500),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2),
                        fontsize=10, color='red', fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

    # 진입/익절 포인트
    if entry_time:
        entry_idx = None
        for i, row in enumerate(data):
            if row['time'] == entry_time:
                entry_idx = i
                break
        if entry_idx is not None:
            ax1.scatter(entry_idx, closes[entry_idx], color='blue', marker='o',
                       s=300, zorder=10, edgecolors='white', linewidths=2)
            ax1.text(entry_idx, closes[entry_idx], ' ENTRY',
                    fontsize=12, color='blue', fontweight='bold', va='center')

    if exit_time:
        exit_idx = None
        for i, row in enumerate(data):
            if row['time'] == exit_time:
                exit_idx = i
                break
        if exit_idx is not None:
            ax1.scatter(exit_idx, closes[exit_idx], color='orange', marker='s',
                       s=300, zorder=10, edgecolors='white', linewidths=2)
            ax1.text(exit_idx, closes[exit_idx], ' EXIT',
                    fontsize=12, color='orange', fontweight='bold', va='center')

    ax1.legend(loc='upper left', fontsize=10)

    # ========== RSI 차트 ==========
    ax2.set_ylabel('RSI', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.plot(x, rsi, label='RSI', color='purple', linewidth=1.5)
    ax2.plot(x, rsi2, label='RSI2 (48)', color='orange', linewidth=2)
    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought')
    ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold')
    ax2.axhline(y=52, color='red', linestyle=':', alpha=0.7, label='RSI2 52 (Long)')
    ax2.axhline(y=48, color='yellow', linestyle=':', alpha=0.7, label='RSI2 48 (Short)')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left', fontsize=8)

    # ========== 볼륨 차트 ==========
    ax3.set_ylabel('Volume', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    colors = ['green' if closes[i] >= opens[i] else 'red' for i in x]
    ax3.bar(x, volumes, color=colors, alpha=0.6)

    # X축 라벨 (일부만 표시)
    step = max(1, len(times) // 20)
    ax3.set_xticks([i for i in x if i % step == 0])
    ax3.set_xticklabels([times[i] for i in x if i % step == 0], rotation=45)

    plt.tight_layout()

    # 저장
    output_file = f'trade_chart_{start_date.split("T")[0]}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ 차트 저장 완료: {output_file}")

    return output_file

if __name__ == "__main__":
    csv_file = 'BITGET_BTCUSDT.P, 60_7fbcf_with_overlap.csv'

    # 9월 8일 거래 차트
    start = '2025-09-07T12:00:00+09:00'
    end = '2025-09-09T12:00:00+09:00'
    entry = '2025-09-08T16:00:00+09:00'
    exit_time = '2025-09-08T23:00:00+09:00'

    print("📊 9월 8일 거래 차트 생성 중...")
    plot_trade_chart(csv_file, start, end, entry, exit_time)
