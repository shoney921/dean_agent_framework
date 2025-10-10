from typing import List, Dict, Any
import asyncio


# Mock tools - 데모용 도구 함수들 (AutoGen과 동일)
def search_web_tool(query: str) -> str:
    """웹 검색을 시뮬레이션하는 도구"""
    if "2006-2007" in query:
        return """2006-2007 시즌 마이애미 히트 선수들의 총 득점은 다음과 같습니다:
        우도니스 하슬렘: 844점
        드웨인 웨이드: 1397점
        제임스 포지: 550점
        ...
        """
    elif "2007-2008" in query:
        return "마이애미 히트 2007-2008 시즌 드웨인 웨이드의 총 리바운드 수는 214개입니다."
    elif "2008-2009" in query:
        return "마이애미 히트 2008-2009 시즌 드웨인 웨이드의 총 리바운드 수는 398개입니다."
    return "데이터를 찾을 수 없습니다."


def percentage_change_tool(start: float, end: float) -> float:
    """퍼센트 변화를 계산하는 도구"""
    return ((end - start) / start) * 100


# 웹 검색 에이전트 클래스 (AutoGen 방식)
class WebSearchAgent:
    def __init__(self):
        self.name = "WebSearchAgent"
        self.description = "스포츠 통계에 대한 웹 정보를 검색하는 에이전트입니다."
        self.tools = [search_web_tool]
        
    def process(self, task: str) -> Dict[str, Any]:
        """웹 검색 에이전트 처리"""
        print(f"\n---------- {self.name} ----------")
        
        # 프롬프트를 통한 툴 선택 시뮬레이션
        print("🤖 에이전트가 프롬프트를 분석하여 툴을 선택합니다...")
        print("📋 사용자 요청: 스포츠 통계 검색이 필요")
        print("🔍 선택된 툴: search_web_tool (웹 검색 도구)")
        print("✅ 툴 실행 중...")
        
        # 검색 수행
        search_result = search_web_tool(task)
        
        print(f"검색 결과: {search_result}")
        
        return {
            "agent": self.name,
            "result": search_result,
            "next_agent": "DataAnalystAgent"
        }


# 데이터 분석 에이전트 클래스 (AutoGen 방식)
class DataAnalystAgent:
    def __init__(self):
        self.name = "DataAnalystAgent"
        self.description = "계산 및 데이터 분석을 수행하는 에이전트입니다."
        self.tools = [percentage_change_tool]
        
    def process(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 분석 에이전트 처리"""
        print(f"\n---------- {self.name} ----------")
        
        # 프롬프트를 통한 툴 선택 시뮬레이션
        print("🤖 에이전트가 프롬프트를 분석하여 툴을 선택합니다...")
        print("📋 사용자 요청: 퍼센트 변화 계산이 필요")
        print("🧮 선택된 툴: percentage_change_tool (퍼센트 변화 계산 도구)")
        print("✅ 툴 실행 중...")
        
        # 2006-2007 시즌 데이터에서 최고 득점자 찾기
        if "2006-2007" in str(search_results):
            if "드웨인 웨이드: 1397점" in search_results.get("result", ""):
                print("최고 득점자: 드웨인 웨이드 (1397점)")
        
        # 리바운드 데이터 추출
        rebounds_2007_2008 = 214
        rebounds_2008_2009 = 398
        
        # 퍼센트 변화 계산
        percentage_change = percentage_change_tool(rebounds_2007_2008, rebounds_2008_2009)
        
        print(f"2007-2008 시즌 리바운드: {rebounds_2007_2008}개")
        print(f"2008-2009 시즌 리바운드: {rebounds_2008_2009}개")
        print(f"퍼센트 변화: {percentage_change:.2f}%")
        
        # 프롬프트를 통한 최종 답변 생성 (실제 AutoGen 방식)
        print("🤖 에이전트가 프롬프트를 통해 최종 답변을 생성합니다...")
        
        # 실제로는 모델이 프롬프트를 통해 답변을 생성해야 함
        # 여기서는 시뮬레이션을 위해 계산된 데이터를 바탕으로 답변 생성
        final_answer = f"""검색 결과를 바탕으로 분석한 결과:

1. 2006-2007 시즌 마이애미 히트 최고 득점자: 드웨인 웨이드 (1397점)
2. 드웨인 웨이드의 리바운드 퍼센트 변화 (2007-2008 → 2008-2009): {percentage_change:.2f}%

분석 완료. TERMINATE"""
        
        print(f"생성된 답변: {final_answer}")
        
        return {
            "agent": self.name,
            "result": final_answer,
            "next_agent": "TERMINATE"
        }


async def main() -> None:
    """메인 실행 함수 (AutoGen 방식)"""
    # 사용 가능한 모델 정보 출력
    print("=" * 80)
    print("모델 정보 확인")
    print("=" * 80)
    
    # 일반적으로 사용 가능한 Gemini 모델들
    available_gemini_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-002"
    ]
    
    print("📋 일반적으로 사용 가능한 Gemini 모델들:")
    print("-" * 50)
    
    for i, model_name in enumerate(available_gemini_models, 1):
        status = "✅ 현재 사용 중" if model_name == "gemini-1.5-flash" else "   "
        print(f"{status} {i}. {model_name}")
    
    print("-" * 50)
    print(f"현재 사용 중인 모델: gemini-1.5-flash")
    print("💡 다른 모델을 사용하려면 코드에서 model 파라미터를 변경하세요.")
    print("=" * 80)

    # 1. Web Search Agent - 정보를 검색하는 에이전트
    web_search_agent = WebSearchAgent()
    
    # 2. Data Analyst Agent - 데이터를 분석하는 에이전트
    data_analyst_agent = DataAnalystAgent()

    # 작업 실행
    print("=" * 80)
    print("LangGraph 스타일 예시 시작")
    print("=" * 80)
    
    task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
    그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""
    
    print(f"\n질문: {task}\n")
    print("=" * 80)
    
    # 워크플로우 실행 (AutoGen 방식 - 에이전트 간 대화)
    try:
        print("🤖 에이전트들이 서로 대화하며 작업을 진행합니다...")
        print("=" * 80)
        
        # 1단계: 웹 검색
        print("\n🔄 1단계: WebSearchAgent가 검색을 수행합니다")
        search_result = web_search_agent.process(task)
        
        # 2단계: 데이터 분석 (에이전트 간 대화 시뮬레이션)
        print("\n🔄 2단계: DataAnalystAgent가 분석을 수행합니다")
        print("💬 WebSearchAgent → DataAnalystAgent: '검색 결과를 바탕으로 계산을 수행해주세요'")
        analysis_result = data_analyst_agent.process(search_result)
        
        print("\n🔄 3단계: 최종 답변 생성")
        print("💬 DataAnalystAgent: '모든 분석이 완료되었습니다. TERMINATE'")
        
        print("\n" + "=" * 80)
        print("작업 완료!")
        print("=" * 80)
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
