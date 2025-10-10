import os
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "AIzaSyAsh2RsHqQxUMiMxEdNv6moXnw-jkAn0NU"

@tool
def search_web_tool(query: str) -> str:
    """주어진 쿼리에 대한 스포츠 통계를 웹에서 검색합니다. 시즌(예: "2006-2007")을 포함해야 합니다."""
    print(f"--- Calling Web Search Tool with query: '{query}' ---")
    if "2006-2007" in query:
        return """2006-2007 시즌 마이애미 히트 선수들의 총 득점은 다음과 같습니다:
        드웨인 웨이드: 1397점
        우도니스 하슬렘: 844점
        제임스 포지: 550점
        ...
        """
    elif "2007-2008" in query:
        return "마이애미 히트 2007-2008 시즌 드웨인 웨이드의 총 리바운드 수는 214개입니다."
    elif "2008-2009" in query:
        return "마이애미 히트 2008-2009 시즌 드웨인 웨이드의 총 리바운드 수는 398개입니다."
    return "요청하신 시즌의 데이터를 찾을 수 없습니다."

@tool
def percentage_change_tool(start: float, end: float) -> float:
    """두 숫자 간의 퍼센트 변화를 계산합니다. (예: 이전 시즌 리바운드, 현재 시즌 리바운드)"""
    print(f"--- Calling Percentage Change Tool with start={start}, end={end} ---")
    result = ((end - start) / start) * 100
    return f"{result:.2f}%"


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

llm = ChatOpenAI(model="gpt-4o")

supervisor_agent = llm.bind_tools(tools)

# --- 4. 그래프 노드(Nodes) 및 엣지(Edges) 로직 정의 ---

# Supervisor 노드: Agent를 호출하여 다음 행동을 결정합니다.
def supervisor_node(state: AgentState):
    print("--- Calling Supervisor ---")
    response = supervisor_agent.invoke(state['messages'])
    return {"messages": [response]}

# Tool 노드: Supervisor가 도구 사용을 결정했을 때, 해당 도구를 실행합니다.
# 참고: LangGraph는 도구 호출과 실행을 자동으로 처리하는 ToolNode를 제공하지만,
# 여기서는 명시적인 이해를 위해 직접 함수를 작성합니다.
def tool_node(state: AgentState):
    print("--- Calling Tools ---")
    # 마지막 메시지(AIMessage)에 도구 호출 정보가 있는지 확인합니다.
    last_message = state['messages'][-1]
    tool_calls = last_message.tool_calls

    # 도구 호출이 없으면 아무것도 하지 않습니다.
    if not tool_calls:
        return {}

    responses = []
    for call in tool_calls:
        # 실행할 도구를 이름으로 찾습니다.
        tool_func = {t.name: t for t in tools}[call['name']]
        # 도구를 실행하고 결과를 저장합니다.
        response = tool_func.invoke(call['args'])
        # 결과를 ToolMessage 형태로 변환하여 리스트에 추가합니다.
        responses.append(
            {
                "tool_call_id": call['id'],
                "name": call['name'],
                "content": str(response), # 결과는 항상 문자열로 변환
            }
        )
    # 실행 결과를 ToolMessage 형태로 변환하여 Supervisor가 다음 단계를 인지할 수 있도록 합니다.
    tool_messages = []
    for response in responses:
        tool_messages.append(ToolMessage(
            content=response['content'],
            tool_call_id=response['tool_call_id']
        ))
    return {"messages": tool_messages}

# 조건부 엣지: 다음 단계를 결정하는 라우팅 함수
def router(state: AgentState) -> str:
    print("--- Routing ---")
    last_message = state['messages'][-1]
    # 마지막 메시지가 도구 호출을 포함하고 있다면 'tools' 노드로 분기합니다.
    if last_message.tool_calls:
        return "tools"
    # 도구 호출이 없다면(즉, 최종 답변이 생성되었다면) 그래프를 종료합니다.
    return "end"

# --- 5. 그래프 생성 및 실행 ---

# 그래프 워크플로우를 정의합니다.
workflow = StateGraph(AgentState)

# 노드를 추가합니다.
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tools", tool_node)

# 엣지를 연결합니다.
workflow.set_entry_point("supervisor")
workflow.add_edge("tools", "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    router,
    {"tools": "tools", "end": END}
)

# 메모리(체크포인트) 설정을 통해 대화 기록을 유지합니다.
# 임시 파일을 사용하여 SQLite 데이터베이스를 생성합니다.
import tempfile
import sqlite3

# 임시 SQLite 파일 생성
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()

# SqliteSaver 인스턴스 생성
memory = SqliteSaver.from_conn_string(f"sqlite:///{temp_db.name}")

# 그래프를 컴파일합니다.
# with_checkpointer를 통해 각 단계의 상태를 저장하고 불러올 수 있습니다.
graph = workflow.compile(checkpointer=memory)


# --- 실행 ---
task = """2006-2007 시즌에 가장 높은 득점을 기록한 마이애미 히트 선수는 누구였고, 
그의 2007-2008 시즌과 2008-2009 시즌 간 총 리바운드 수의 퍼센트 변화는 얼마인가요?"""

# 대화 스레드 설정
config = {"configurable": {"thread_id": "1"}}

# 스트리밍 방식으로 실행하여 중간 과정을 실시간으로 확인합니다.
print("="*80)
print(f"질문: {task}")
print("="*80)

final_response = None
for event in graph.stream({"messages": [HumanMessage(content=task)]}, config=config):
    for key, value in event.items():
        if key == 'supervisor' and value['messages']:
            message = value['messages'][-1]
            if not message.tool_calls:
                final_response = message
                print("\n--- 최종 답변 ---")
                print(message.content)
            else:
                print("\n--- Supervisor의 결정 (도구 호출) ---")
                print(message.tool_calls)
        elif key == 'tools' and value['messages']:
             print("\n--- 도구 실행 결과 ---")
             print(value['messages'][-1].content)


print("\n" + "="*80)
print("작업 완료!")
print("="*80)

# 임시 파일 정리
import os
try:
    os.unlink(temp_db.name)
except:
    pass

# 최종 상태 확인 (선택 사항)
# final_state = graph.get_state(config)
# print(final_state.values['messages'][-1].content)