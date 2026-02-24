#!/bin/bash
#
# Investment Portfolio Update Workflow
# 1. Save current git state
# 2. Run Claude Code to update all companies
# 3. Get git diff
# 4. Generate summary report
#

TOUZI_DIR=~/Code/touzi
REPORT_DIR=$TOUZI_DIR/reports

cd $TOUZI_DIR

echo "📊 投资组合更新工作流"
echo "===================="
echo ""

# Step 1: Save current state
echo "📝 Step 1: 保存当前状态..."
git add -A
git commit -m "pre-update: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true

# Step 2: Run Claude Code to update
echo ""
echo "🤖 Step 2: 运行 Claude Code 更新..."
echo "   命令: claude --dangerously-skip-permissions \"更新全部公司今天的情况\""
echo ""

# Run the update command
claude --dangerously-skip-permissions "更新全部公司今天的情况"

# Step 3: Get git diff
echo ""
echo "📈 Step 3: 获取更新差异..."
git diff --stat > /tmp/touzi_diff.txt
git status --short > /tmp/touzi_status.txt

# Step 4: Generate report
echo ""
echo "📄 Step 4: 生成更新报告..."

mkdir -p $REPORT_DIR

REPORT_FILE=$REPORT_DIR/report_$(date +%Y%m%d_%H%M%S).md

cat > $REPORT_FILE << 'EOF'
# 投资组合更新报告

## 更新概要

EOF

# Count changes
changed_files=$(git status --short | grep -E "^\s*M" | wc -l | tr -d ' ')
new_files=$(git status --short | grep -E "^\s*A" | wc -l | tr -d ' ')

echo "本次更新涉及 **$changed_files** 份修改报告，**$new_files** 份新增报告" >> $REPORT_FILE

cat >> $REPORT_FILE << 'EOF'

## 详细变更

```
EOF

cat /tmp/touzi_diff.txt >> $REPORT_FILE

cat >> $REPORT_FILE << 'EOF'
```

## 更新文件列表

| 状态 | 公司 |
|------|------|
EOF

while IFS= read -r line; do
    status=$(echo "$line" | cut -d' ' -f1)
    filename=$(echo "$line" | cut -d' ' -f2-)
    company=$(echo "$filename" | sed 's/投资报告.md//')
    case $status in
        M) status_cn="修改" ;;
        A) status_cn="新增" ;;
        D) status_cn="删除" ;;
        *) status_cn=$status ;;
    esac
    echo "| $status_cn | $company |" >> $REPORT_FILE
done < /tmp/touzi_status.txt

cat >> $REPORT_FILE << EOF

---
*报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

echo ""
echo "===================="
echo "✅ 更新完成！"
echo "📄 报告已保存: $REPORT_FILE"
echo ""

# Show the report
cat $REPORT_FILE
