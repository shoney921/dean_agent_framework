import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# plotly가 없어도 동작하도록 try-except로 처리
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ plotly가 설치되지 않았습니다. 차트 기능이 제한됩니다. 설치하려면: `pip install plotly`")

from frontend.streamlit_app.services.api import BackendAPIClient


def main():
    """스트림릿 메인 애플리케이션 (홈페이지)"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="Dean Agent Framework",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 사이드바 네비게이션
    with st.sidebar:
        for _ in range(25):
            st.text("  ")

        # 상태 정보 표시
        st.markdown("### 시스템 상태")
        
        # API 연결 상태 확인 (간단한 예시)
        try:
            client = BackendAPIClient()
            # 간단한 API 호출로 연결 상태 확인
            client.list_runs(limit=1)
            st.success("✅ API 연결됨")
        except Exception as e:
            st.error(f"❌ API 연결 실패: {str(e)}")
    
    # 홈페이지 내용 표시
    show_home_content()


def show_home_content():
    """홈페이지 내용 표시"""
    st.title("배치 시스템 모니터링")
    st.markdown("---")
    
    # API 클라이언트 초기화
    try:
        client = BackendAPIClient()
    except Exception as e:
        st.error(f"API 클라이언트 초기화 실패: {str(e)}")
        return
    
    # 실시간 상태 대시보드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🟢 활성 실행",
            value=get_active_runs_count(client),
            delta=None
        )
    
    with col2:
        st.metric(
            label="✅ 완료된 실행",
            value=get_completed_runs_count(client),
            delta=None
        )
    
    with col3:
        st.metric(
            label="📄 등록된 노션 페이지",
            value=get_registered_pages_count(client),
            delta=None
        )
    
    with col4:
        st.metric(
            label="🔄 활성 노션 페이지",
            value=get_active_pages_count(client),
            delta=None
        )
    
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        # 상태별 차트
        st.subheader("📈 실행 상태 분포")
        
        try:
            all_runs = client.list_runs(limit=100)
            if all_runs:
                df = pd.DataFrame(all_runs)
                
                # 상태별 카운트
                status_counts = df['status'].value_counts() if 'status' in df.columns else pd.Series()
                
                if not status_counts.empty:
                    if PLOTLY_AVAILABLE:
                        # 파이 차트
                        fig = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            # title="실행 상태 분포",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # plotly가 없을 때는 테이블로 표시
                        st.markdown("**실행 상태 분포**")
                        status_df = pd.DataFrame({
                            '상태': status_counts.index,
                            '개수': status_counts.values,
                            '비율(%)': (status_counts.values / status_counts.sum() * 100).round(1)
                        })
                        st.dataframe(status_df, use_container_width=True, hide_index=True)
                else:
                    st.info("상태 데이터가 없습니다.")
            else:
                st.info("차트를 그릴 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"차트 생성 실패: {str(e)}")
    with col2:
        # 시간대별 실행 트렌드
        st.subheader("🗓️ 일별 실행 추세")
        
        try:
            all_runs = client.list_runs(limit=200)
            if all_runs:
                df = pd.DataFrame(all_runs)
                
                if 'started_at' in df.columns:
                    # 날짜 변환
                    df['started_at'] = pd.to_datetime(df['started_at'])
                    df['date'] = df['started_at'].dt.date
                    
                    # 일별 카운트
                    daily_counts = df.groupby('date').size().reset_index(name='count')
                    
                    if PLOTLY_AVAILABLE:
                        # 라인 차트
                        fig = px.line(
                            daily_counts,
                            x='date',
                            y='count',
                            # title="일별 실행 횟수",
                            markers=True
                        )
                        fig.update_layout(
                            xaxis_title="날짜",
                            yaxis_title="실행 횟수"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # plotly가 없을 때는 테이블로 표시
                        st.markdown("**일별 실행 횟수**")
                        daily_counts['날짜'] = daily_counts['date']
                        daily_counts['실행 횟수'] = daily_counts['count']
                        display_df = daily_counts[['날짜', '실행 횟수']].sort_values('날짜')
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info("시작 시간 데이터가 없습니다.")
            else:
                st.info("트렌드 차트를 그릴 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"트렌드 차트 생성 실패: {str(e)}")

    st.markdown("---")

    # 팀별 통계
    st.subheader("👥 팀별 통계")
    
    try:
        all_runs = client.list_runs(limit=100)
        if all_runs:
            df = pd.DataFrame(all_runs)
            
            if 'team_name' in df.columns:
                team_stats = df.groupby('team_name').agg({
                    'id': 'count',
                    'status': lambda x: (x == 'completed').sum()
                }).reset_index()
                team_stats.columns = ['팀명', '총 실행', '완료']
                team_stats['완료율'] = (team_stats['완료'] / team_stats['총 실행'] * 100).round(1)
                
                st.dataframe(team_stats, use_container_width=True, hide_index=True)
            else:
                st.info("팀 정보가 없습니다.")
        else:
            st.info("팀 통계 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"팀 통계 조회 실패: {str(e)}")

    
    # 최근 실행 기록
    st.subheader("📊 최근 실행 기록")
    
    try:
        runs = client.list_runs(limit=10)
        if runs:
            # 데이터프레임으로 변환
            df = pd.DataFrame(runs)
            
            # 컬럼 선택 및 표시
            display_columns = ['id', 'team_name', 'task', 'status', 'started_at', 'ended_at']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                st.dataframe(
                    df[available_columns],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("표시할 수 있는 실행 기록이 없습니다.")
        else:
            st.info("실행 기록이 없습니다.")
            
    except Exception as e:
        st.error(f"실행 기록 조회 실패: {str(e)}")
    


def get_active_runs_count(client: BackendAPIClient) -> int:
    """활성 실행 수 조회"""
    try:
        runs = client.list_runs(limit=100)
        active_count = sum(1 for run in runs if run.get('status') == 'running')
        return active_count
    except:
        return 0


def get_completed_runs_count(client: BackendAPIClient) -> int:
    """완료된 실행 수 조회"""
    try:
        runs = client.list_runs(limit=100)
        completed_count = sum(1 for run in runs if run.get('status') == 'completed')
        return completed_count
    except:
        return 0


def get_registered_pages_count(client: BackendAPIClient) -> int:
    """등록된 노션 페이지 수 조회"""
    try:
        pages = client.get_registered_pages()
        return len(pages)
    except:
        return 0


def get_active_pages_count(client: BackendAPIClient) -> int:
    """활성 노션 페이지 수 조회"""
    try:
        pages = client.get_active_pages()
        return len(pages)
    except:
        return 0


if __name__ == "__main__":
    main()
