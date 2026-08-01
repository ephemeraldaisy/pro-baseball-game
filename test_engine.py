# test_engine.py
from engine import PureKboEngine

def run_quick_pitcher_test():
    print("🧪 [투수 교체 및 6~9회 로직 1초 고속 검증 시작]...")
    
    # 1. 엔진 객체 생성
    engine = PureKboEngine(my_team="💖 핑크 돌핀스", enemy_team="⚡ 시흥 라이트닝스")
    
    # 2. 강제로 6회, 7회, 8회, 9회 상황을 만들어서 evaluate_pitcher_scenario 실행
    for inning in range(1, 10):
        engine.inning = inning
        print(f"\n--- 🏟️ {inning}회 상황 테스트 ---")
        
        # 수비 턴 (우리 팀 투수 평가)
        try:
            my_target = engine.evaluate_pitcher_scenario(score_diff=0, is_defense=True)
            print(f"  ✅ {inning}회 수비 투수 추천 성공 (Pitcher Index: {my_target})")
        except Exception as e:
            print(f"  ❌ {inning}회 수비 연산 중 에러 발생!! ➔ {e}")

        # 공격 턴 (상대 팀 투수 평가 - 6회에 AttributeError 잘 터지는 구간)
        try:
            enemy_target = engine.evaluate_pitcher_scenario(score_diff=-2, is_defense=False)
            print(f"  ✅ {inning}회 공격(적 투수) 추천 성공 (Pitcher Index: {enemy_target})")
        except Exception as e:
            print(f"  ❌ {inning}회 공격(적 투수) 연산 중 에러 발생!! ➔ {e}")

    print("\n🎉 모든 이닝 테스트 완료! 에러가 안 떠야 합격입니다.")

if __name__ == "__main__":
    run_quick_pitcher_test()
