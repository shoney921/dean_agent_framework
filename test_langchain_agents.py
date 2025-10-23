#!/usr/bin/env python3
"""
LangChain 에이전트 테스트 스크립트
GEMINI_API_KEY를 사용하여 에이전트 간 대화를 테스트합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai.agents.langchain_agent import LangChainAgent, LangChainAgentTeam, run_sample_conversation

def test_single_agent():
    """단일 에이전트 테스트"""
    print("🧪 단일 에이전트 테스트")
    print("=" * 40)
    
    try:
        # 단일 에이전트 생성
        agent = LangChainAgent(
            name="테스트에이전트",
            role="도움이 되는 AI 어시스턴트",
            model_name="gemini-2.0-flash-exp"
        )
        
        # 테스트 메시지들
        test_messages = [
            "안녕하세요! 자기소개를 해주세요.",
            "파이썬 프로그래밍에 대해 간단히 설명해주세요.",
            "AI의 미래에 대해 어떻게 생각하시나요?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 테스트 {i}: {message}")
            response = agent.get_response(message)
            print(f"🤖 응답: {response}")
            print("-" * 30)
        
        print("✅ 단일 에이전트 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 단일 에이전트 테스트 실패: {str(e)}")

def test_agent_team():
    """에이전트 팀 테스트"""
    print("\n🧪 에이전트 팀 테스트")
    print("=" * 40)
    
    try:
        # 에이전트 팀 생성
        team = LangChainAgentTeam()
        
        # 다양한 역할의 에이전트들 추가
        coder = LangChainAgent("개발자", "소프트웨어 개발 전문가")
        designer = LangChainAgent("디자이너", "UI/UX 디자인 전문가")
        marketer = LangChainAgent("마케터", "디지털 마케팅 전문가")
        
        team.add_agent(coder)
        team.add_agent(designer)
        team.add_agent(marketer)
        
        # 팀 대화 시작
        initial_message = "새로운 모바일 앱 프로젝트를 시작하려고 합니다. 각자의 전문 분야에서 중요한 포인트를 제시해주세요."
        
        print(f"🚀 팀 대화 시작: {initial_message}")
        conversation = team.start_conversation(initial_message, max_rounds=2)
        
        print("✅ 에이전트 팀 테스트 완료!")
        return conversation
        
    except Exception as e:
        print(f"❌ 에이전트 팀 테스트 실패: {str(e)}")
        return None

def test_custom_conversation():
    """사용자 정의 대화 테스트"""
    print("\n🧪 사용자 정의 대화 테스트")
    print("=" * 40)
    
    try:
        # 전문가 에이전트들 생성
        doctor = LangChainAgent("의사", "의료 전문가")
        nutritionist = LangChainAgent("영양사", "영양 및 건강 전문가")
        fitness_trainer = LangChainAgent("트레이너", "운동 및 피트니스 전문가")
        
        team = LangChainAgentTeam()
        team.add_agent(doctor)
        team.add_agent(nutritionist)
        team.add_agent(fitness_trainer)
        
        # 건강 관련 대화
        health_topic = "건강한 생활을 위한 종합적인 조언을 각자의 전문 분야에서 제시해주세요."
        
        print(f"🏥 건강 전문가 팀 대화: {health_topic}")
        conversation = team.start_conversation(health_topic, max_rounds=2)
        
        print("✅ 사용자 정의 대화 테스트 완료!")
        return conversation
        
    except Exception as e:
        print(f"❌ 사용자 정의 대화 테스트 실패: {str(e)}")
        return None

def main():
    """메인 테스트 함수"""
    print("🎯 LangChain 에이전트 테스트 시작")
    print("=" * 60)
    
    # 환경 변수 확인
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 GEMINI_API_KEY를 설정해주세요.")
        return
    
    try:
        # 1. 단일 에이전트 테스트
        test_single_agent()
        
        # 2. 에이전트 팀 테스트
        test_agent_team()
        
        # 3. 사용자 정의 대화 테스트
        test_custom_conversation()
        
        # 4. 샘플 대화 실행
        print("\n🧪 샘플 대화 실행")
        print("=" * 40)
        run_sample_conversation()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
