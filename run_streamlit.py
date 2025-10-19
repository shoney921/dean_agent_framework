#!/usr/bin/env python3
"""
스트림릿 애플리케이션 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    """스트림릿 애플리케이션 실행"""
    
    # 프로젝트 루트 디렉토리로 이동
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 스트림릿 앱 경로
    streamlit_app_path = "frontend/streamlit_app/app.py"
    
    print("🚀 스트림릿 애플리케이션을 시작합니다...")
    print(f"📁 프로젝트 루트: {project_root}")
    print(f"📄 앱 파일: {streamlit_app_path}")
    print("🌐 브라우저에서 http://localhost:8501 을 열어주세요")
    print("📋 사용 가능한 페이지:")
    print("   - 홈: http://localhost:8501/")
    print("   - 실행 로그: http://localhost:8501/agent_logs")
    print("   - 노션 관리: http://localhost:8501/notion_management")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    try:
        # 스트림릿 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            streamlit_app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 스트림릿 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
