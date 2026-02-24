#!/bin/bash
#
# Generate Investment Portfolio Update Report
# Run this after running Claude Code update to generate a summary report
#

TOUZI_DIR=~/Code/touzi
REPORT_DIR=$TOUZI_DIR/reports

cd $TOUZI_DIR

echo "📊 生成投资组合更新报告"
echo "===================="
echo ""

# Get git diff (use porcelain mode for cleaner output)
git diff --stat -- . > /tmp/touzi_diff.txt 2>/dev/null
git status --porcelain -- . > /tmp/touzi_status.txt 2>/dev/null

# Check if there are changes
if [ ! -s /tmp/touzi_status.txt ]; then
    echo "⚠️ 没有检测到任何更新"
    echo "请先运行: ~/Code/touzi/claude --dangerously-skip-permissions \"更新全部公司今天的情况\""
    exit 1
fi

# Generate report
mkdir -p $REPORT_DIR

REPORT_FILE=$REPORT_DIR/report_$(date +%Y%m%d_%H%M%S).md

cat > $REPORT_FILE << EOF
# 投资组合更新报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 更新概要

EOF

# Count changes
changed_files=$(grep -c "^.M" /tmp/touzi_status.txt 2>/dev/null || echo 0)
new_files=$(grep -c "^??" /tmp/touzi_status.txt 2>/dev/null || echo 0)
total_changes=$(wc -l < /tmp/touzi_status.txt)

echo "本次更新涉及 **$total_changes** 项变更：" >> $REPORT_FILE
echo "- 修改: $changed_files 份报告" >> $REPORT_FILE  
echo "- 新增: $new_files 份新文件" >> $REPORT_FILE

cat >> $REPORT_FILE << 'EOF'

## 详细变更统计

```
EOF

cat /tmp/touzi_diff.txt >> $REPORT_FILE

cat >> $REPORT_FILE << 'EOF'
```

## 更新文件列表

| 状态 | 文件 |
|------|------|
EOF

while IFS= read -r line; do
    status="${line:0:2}"
    filename="${line:3}"
    
    # Skip non-markdown files
    if [[ ! "$filename" =~ \.md$ ]]; then
        continue
    fi
    
    case $status in
        " M"|"M ") status_cn="修改" ;;
        "??") status_cn="新增" ;;
        " D"|"D ") status_cn="删除" ;;
        *) status_cn=$status ;;
    esac
    echo "| $status_cn | $filename |" >> $REPORT_FILE
done < /tmp/touzi_status.txt

cat >> $REPORT_FILE << 'EOF'

如需更新更多## 下一步

如需更新更多公司，运行以下命令：

```bash
~/Code/touzi/claude --dangerously-skip-permissions "更新全部公司今天的情况"
```

---
*本报告由自动生成*
EOF

echo ""
echo "===================="
echo "✅ 报告已生成!"
echo "📄 $REPORT_FILE"
echo ""

# Display report content
cat $REPORT_FILE
