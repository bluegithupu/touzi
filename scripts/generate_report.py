#!/usr/bin/env python3
"""
Generate Investment Portfolio Update Report
Run this after running Claude Code update to generate a summary report
"""

import os
import subprocess
from datetime import datetime

TOUZI_DIR = os.path.expanduser("~/Code/touzi")
REPORT_DIR = os.path.join(TOUZI_DIR, "reports")

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=TOUZI_DIR)
    return result.stdout

def generate_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Get list of investment report files
    all_reports = [f for f in os.listdir(TOUZI_DIR) if f.endswith('投资报告.md')]
    
    # Get modified files from git diff (use -z for null-separated, then tr)
    diff_output = run_cmd("git diff --name-only -z | tr '\\0' '\\n'")
    
    # Parse modified files - handle quoted names
    modified = []
    for line in diff_output.strip().split('\n'):
        if not line:
            continue
        # Remove quotes
        filename = line.strip().strip('"')
        if filename in all_reports:
            modified.append(filename)
    
    # Get diff stat (use --no-ext-diff to avoid encoding issues)
    diff_stat = run_cmd("git diff --stat --no-ext-diff")
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_file = os.path.join(REPORT_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 投资组合更新报告\n\n")
        f.write(f"**生成时间**: {timestamp}\n\n")
        f.write(f"## 更新概要\n\n")
        
        if modified:
            f.write(f"本次更新涉及 **{len(modified)}** 份投资报告：\n\n")
        else:
            f.write(f"暂无投资报告更新。\n\n")
        
        f.write(f"## 详细变更统计\n\n")
        f.write(f"```\n{diff_stat}\n```\n\n")
        
        if modified:
            f.write(f"## 更新文件列表\n\n")
            f.write(f"| 状态 | 公司 |\n")
            f.write(f"|------|------|\n")
            
            for filename in modified:
                company = filename.replace('投资报告.md', '')
                f.write(f"| 修改 | {company} |\n")
            f.write(f"\n")
        
        f.write(f"## 下一步\n\n")
        f.write(f"如需更新更多公司，运行以下命令：\n\n")
        f.write(f"```bash\n")
        f.write(f"~/Code/touzi/claude --dangerously-skip-permissions \"更新全部公司今天的情况\"\n")
        f.write(f"```\n\n")
        f.write(f"---\n*本报告由自动生成*\n")
    
    return report_file, len(modified), modified

if __name__ == "__main__":
    print("📊 生成投资组合更新报告")
    print("=" * 40)
    
    path, count, files = generate_report()
    
    print(f"\n✅ 报告已生成!")
    print(f"📄 {path}")
    print(f"\n更新了 {count} 份报告:")
    for filename in files:
        company = filename.replace('投资报告.md', '')
        print(f"  ✅ {company}")
