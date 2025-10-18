"""
팀 구성 설정 관리

YAML 또는 JSON 기반으로 팀 구성을 정의하고 관리합니다.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


@dataclass
class AgentConfig:
    """에이전트 설정"""
    name: str
    factory: str  # factory 함수명
    system_message: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@dataclass
class TeamDefinition:
    """팀 정의"""
    name: str
    description: str
    agents: List[AgentConfig]
    max_messages: int = 20
    termination_keyword: str = "TERMINATE"
    execution_order: Optional[List[str]] = None


@dataclass
class HierarchicalWorkflow:
    """계층적 워크플로우 정의"""
    name: str
    description: str
    teams: List[str]  # 팀 이름들
    execution_strategy: str = "parallel"  # "parallel" 또는 "sequential"
    master_team: Optional[str] = None
    task_templates: Dict[str, str] = field(default_factory=dict)


class TeamConfigManager:
    """팀 설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "src/ai/orchestrator/team_configs.yaml"
        self.team_definitions: Dict[str, TeamDefinition] = {}
        self.workflows: Dict[str, HierarchicalWorkflow] = {}
        self.agent_factories: Dict[str, callable] = {}
        self._load_agent_factories()
        self._load_configs()
    
    def _load_agent_factories(self):
        """에이전트 팩토리 함수들을 로드"""
        from src.ai.agents.web_search_agent import create_web_search_agent
        from src.ai.agents.data_analyst_agent import create_data_analyst_agent
        from src.ai.agents.analysis_agent import create_analysis_agent, create_devil_advocate_analyst_agent
        from src.ai.agents.insight_agent import create_insight_agent
        from src.ai.agents.summary_agent import create_summary_agent
        
        self.agent_factories = {
            "create_web_search_agent": create_web_search_agent,
            "create_data_analyst_agent": create_data_analyst_agent,
            "create_analysis_agent": create_analysis_agent,
            "create_devil_advocate_analyst_agent": create_devil_advocate_analyst_agent,
            "create_insight_agent": create_insight_agent,
            "create_summary_agent": create_summary_agent,
        }
    
    def _load_configs(self):
        """설정 파일 로드"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            self._create_default_config()
            return
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 팀 정의 로드
        for team_data in config_data.get('teams', []):
            agents = [AgentConfig(**agent_data) for agent_data in team_data['agents']]
            team_def = TeamDefinition(
                name=team_data['name'],
                description=team_data['description'],
                agents=agents,
                max_messages=team_data.get('max_messages', 20),
                termination_keyword=team_data.get('termination_keyword', 'TERMINATE'),
                execution_order=team_data.get('execution_order')
            )
            self.team_definitions[team_def.name] = team_def
        
        # 워크플로우 정의 로드
        for workflow_data in config_data.get('workflows', []):
            workflow = HierarchicalWorkflow(
                name=workflow_data['name'],
                description=workflow_data['description'],
                teams=workflow_data['teams'],
                execution_strategy=workflow_data.get('execution_strategy', 'parallel'),
                master_team=workflow_data.get('master_team'),
                task_templates=workflow_data.get('task_templates', {})
            )
            self.workflows[workflow.name] = workflow
    
    def _create_default_config(self):
        """기본 설정 파일 생성"""
        default_config = {
            'teams': [
                {
                    'name': '데이터수집팀',
                    'description': '웹 검색 및 데이터 수집을 담당하는 팀',
                    'agents': [
                        {'name': 'web_search', 'factory': 'create_web_search_agent'},
                        {'name': 'data_analyst', 'factory': 'create_data_analyst_agent'}
                    ],
                    'max_messages': 15,
                    'termination_keyword': 'TERMINATE'
                },
                {
                    'name': '분석팀',
                    'description': '데이터 분석 및 인사이트 도출을 담당하는 팀',
                    'agents': [
                        {'name': 'analysis', 'factory': 'create_analysis_agent'},
                        {'name': 'insight', 'factory': 'create_insight_agent'}
                    ],
                    'max_messages': 20,
                    'termination_keyword': 'TERMINATE'
                },
                {
                    'name': '검증팀',
                    'description': '결과 검증 및 요약을 담당하는 팀',
                    'agents': [
                        {'name': 'devil_advocate', 'factory': 'create_devil_advocate_analyst_agent'},
                        {'name': 'summary', 'factory': 'create_summary_agent'}
                    ],
                    'max_messages': 15,
                    'termination_keyword': 'TERMINATE'
                },
                {
                    'name': '마스터팀',
                    'description': '하위 팀 결과를 종합하는 마스터 팀',
                    'agents': [
                        {'name': 'master_analyst', 'factory': 'create_analysis_agent'}
                    ],
                    'max_messages': 10,
                    'termination_keyword': 'TERMINATE'
                }
            ],
            'workflows': [
                {
                    'name': 'standard_analysis',
                    'description': '표준 분석 워크플로우',
                    'teams': ['데이터수집팀', '분석팀', '검증팀'],
                    'execution_strategy': 'parallel',
                    'master_team': '마스터팀',
                    'task_templates': {
                        '데이터수집팀': '다음 작업에 필요한 데이터를 수집해주세요: {main_task}',
                        '분석팀': '다음 작업을 분석해주세요: {main_task}',
                        '검증팀': '다음 작업의 결과를 검증하고 요약해주세요: {main_task}',
                        '마스터팀': '다음 하위 팀 결과들을 종합하여 최종 보고서를 작성해주세요:\n{sub_results}'
                    }
                }
            ]
        }
        
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"기본 설정 파일이 생성되었습니다: {config_file}")
    
    def get_team_definition(self, team_name: str) -> Optional[TeamDefinition]:
        """팀 정의 조회"""
        return self.team_definitions.get(team_name)
    
    def get_workflow(self, workflow_name: str) -> Optional[HierarchicalWorkflow]:
        """워크플로우 정의 조회"""
        return self.workflows.get(workflow_name)
    
    def create_agents_for_team(self, team_name: str, model_client: OpenAIChatCompletionClient) -> List[AssistantAgent]:
        """팀에 필요한 에이전트들 생성"""
        team_def = self.get_team_definition(team_name)
        if not team_def:
            raise ValueError(f"팀 '{team_name}'을 찾을 수 없습니다")
        
        agents = []
        for agent_config in team_def.agents:
            factory = self.agent_factories.get(agent_config.factory)
            if not factory:
                raise ValueError(f"에이전트 팩토리 '{agent_config.factory}'을 찾을 수 없습니다")
            
            agent = factory(model_client)
            agents.append(agent)
        
        return agents
    
    def list_teams(self) -> List[str]:
        """사용 가능한 팀 목록"""
        return list(self.team_definitions.keys())
    
    def list_workflows(self) -> List[str]:
        """사용 가능한 워크플로우 목록"""
        return list(self.workflows.keys())
    
    def create_task_for_team(self, team_name: str, main_task: str, workflow_name: str = "standard_analysis") -> str:
        """팀별 작업 템플릿 생성"""
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"워크플로우 '{workflow_name}'을 찾을 수 없습니다")
        
        template = workflow.task_templates.get(team_name)
        if not template:
            return main_task
        
        return template.format(main_task=main_task)


# 전역 설정 관리자 인스턴스
config_manager = TeamConfigManager()


def get_config_manager() -> TeamConfigManager:
    """설정 관리자 인스턴스 반환"""
    return config_manager

