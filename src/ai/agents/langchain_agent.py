"""
LangChain 에이전트 간 메시지 주고받기 샘플
GEMINI_API_KEY를 사용하여 두 개의 에이전트가 대화하는 예제
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

# 환경 변수 로드
load_dotenv()

class LangChainAgent:
    """LangChain을 사용한 AI 에이전트 클래스"""
    
    def __init__(self, name: str, role: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        에이전트 초기화
        
        Args:
            name: 에이전트 이름
            role: 에이전트 역할
            model_name: 사용할 모델명
        """
        self.name = name
        self.role = role
        self.model_name = model_name
        
        # Gemini API 키 확인
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 환경변수에 설정되지 않았습니다.")
        
        # Gemini 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=1024
        )
        
        # 대화 메모리 초기화
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 시스템 프롬프트 설정
        self.system_prompt = f"""
        당신은 {self.name}입니다. 역할: {self.role}
        
        다음 규칙을 따라 대화하세요:
        1. 친근하고 도움이 되는 톤으로 대화하세요
        2. 한국어로 응답하세요
        3. 질문에 대해 구체적이고 유용한 답변을 제공하세요
        4. 다른 에이전트와 협력하여 문제를 해결하세요
        """
    
    def get_response(self, message: str, context: str = "") -> str:
        """
        메시지에 대한 응답 생성
        
        Args:
            message: 입력 메시지
            context: 추가 컨텍스트
            
        Returns:
            에이전트의 응답
        """
        try:
            # 메시지 구성
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"{context}\n{message}" if context else message)
            ]
            
            # 기존 대화 기록 추가
            chat_history = self.memory.chat_memory.messages
            if chat_history:
                messages = [SystemMessage(content=self.system_prompt)] + chat_history + [HumanMessage(content=message)]
            
            # 응답 생성
            response = self.llm.invoke(messages)
            
            # 대화 기록 저장
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response.content)
            
            return response.content
            
        except Exception as e:
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """대화 기록 반환"""
        history = []
        messages = self.memory.chat_memory.messages
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "user": messages[i].content,
                    "assistant": messages[i + 1].content
                })
        
        return history


class LangChainAgentTeam:
    """여러 LangChain 에이전트가 협력하는 팀 클래스"""
    
    def __init__(self):
        """팀 초기화"""
        self.agents = {}
        self.conversation_log = []
    
    def add_agent(self, agent: LangChainAgent):
        """에이전트 추가"""
        self.agents[agent.name] = agent
    
    def start_conversation(self, initial_message: str, max_rounds: int = 5) -> List[Dict[str, Any]]:
        """
        에이전트 간 대화 시작
        
        Args:
            initial_message: 초기 메시지
            max_rounds: 최대 대화 라운드 수
            
        Returns:
            대화 기록 리스트
        """
        if not self.agents:
            raise ValueError("에이전트가 추가되지 않았습니다.")
        
        agent_names = list(self.agents.keys())
        current_message = initial_message
        conversation = []
        
        print(f"🚀 대화 시작: {initial_message}")
        print("=" * 50)
        
        for round_num in range(max_rounds):
            print(f"\n📝 라운드 {round_num + 1}")
            
            for agent_name in agent_names:
                agent = self.agents[agent_name]
                
                # 에이전트 응답 생성
                response = agent.get_response(current_message)
                
                # 대화 기록 저장
                conversation_entry = {
                    "round": round_num + 1,
                    "agent": agent_name,
                    "role": agent.role,
                    "message": current_message,
                    "response": response
                }
                conversation.append(conversation_entry)
                
                print(f"🤖 {agent_name} ({agent.role}): {response}")
                
                # 다음 에이전트를 위한 메시지 업데이트
                current_message = response
            
            print("-" * 30)
        
        self.conversation_log.extend(conversation)
        return conversation


def create_sample_agents() -> LangChainAgentTeam:
    """샘플 에이전트 팀 생성"""
    team = LangChainAgentTeam()
    
    # 데이터 분석가 에이전트
    data_analyst = LangChainAgent(
        name="데이터분석가",
        role="데이터 분석 및 인사이트 도출 전문가",
        model_name="gemini-2.0-flash-exp"
    )
    
    # 비즈니스 컨설턴트 에이전트
    business_consultant = LangChainAgent(
        name="비즈니스컨설턴트",
        role="비즈니스 전략 및 의사결정 지원 전문가",
        model_name="gemini-2.0-flash-exp"
    )
    
    # 기술 전문가 에이전트
    tech_expert = LangChainAgent(
        name="기술전문가",
        role="기술 아키텍처 및 구현 전문가",
        model_name="gemini-2.0-flash-exp"
    )
    
    team.add_agent(data_analyst)
    team.add_agent(business_consultant)
    team.add_agent(tech_expert)
    
    return team


def run_sample_conversation():
    """샘플 대화 실행"""
    try:
        print("🎯 LangChain 에이전트 팀 대화 샘플 시작")
        print("=" * 60)
        
        # 에이전트 팀 생성
        team = create_sample_agents()
        
        # 초기 메시지 설정
        initial_message = """
        우리 회사에서 새로운 AI 기반 고객 서비스 플랫폼을 구축하려고 합니다. 
        이 프로젝트에 대해 각자의 전문 분야 관점에서 의견을 제시해주세요.
        """
        
        # 대화 시작
        conversation = team.start_conversation(initial_message, max_rounds=3)
        
        print("\n" + "=" * 60)
        print("✅ 대화 완료!")
        print(f"총 {len(conversation)}개의 메시지가 교환되었습니다.")
        
        return conversation
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    # 샘플 대화 실행
    run_sample_conversation()
