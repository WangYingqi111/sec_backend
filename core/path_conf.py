import sys
import os

def setup_project_path():
    """将项目根目录加入 sys.path，以便能导入 /src 下的共享模块"""
    # 获取当前文件 (path_conf.py) 所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 回退到 /My_Hybrid_App 根目录 (core -> app -> backend -> web_app -> My_Hybrid_App)
    project_root = os.path.join(current_dir, '..', '..', '..', '..')
    project_root = os.path.abspath(project_root)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"✅ Project root added to path: {project_root}")