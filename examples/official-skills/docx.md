# Skill: docx

## 概述

`docx` 是全面的 Word 文档创建、编辑和分析 Skill，支持批注、修订追踪（Track Changes）、格式保留和文本提取。

**核心能力**:
- 创建新 Word 文档
- 编辑和修改现有文档
- 处理修订追踪（Track Changes）
- 添加批注（Comments）
- 提取文档文本和结构
- 保留原始格式

---

## 触发方式

### 斜杠命令

```bash
/docx
```

### 自然语言触发

```
"创建一个 Word 文档"
"编辑这个 .docx 文件"
"从 Word 文档中提取内容"
"给文档添加批注"
"处理这个合同文档"
```

---

## 实际演示

### 示例 1: 创建技术文档

**用户请求**:
```
创建一份 API 技术文档的 Word 文件，包含：
- 封面页（项目名、版本、日期）
- 目录
- API 接口说明（表格格式）
- 代码示例
```

**Claude 的解决方案**（使用 python-docx）:

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def create_api_doc(output_path: str):
    """创建 API 技术文档"""
    doc = Document()

    # ============ 设置页面边距 ============
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2.5)

    # ============ 封面页 ============
    # 添加标题
    title = doc.add_heading('', 0)
    title_run = title.add_run('用户服务 API 文档')
    title_run.font.size = Pt(28)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x1a, 0x73, 0xe8)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # 空行

    # 版本信息
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run(f'版本: v2.1.0\n').font.size = Pt(12)
    info.add_run(f'更新日期: {datetime.date.today().strftime("%Y年%m月%d日")}\n').font.size = Pt(12)
    info.add_run('维护团队: 后端开发组').font.size = Pt(12)

    # 分页
    doc.add_page_break()

    # ============ API 概述 ============
    doc.add_heading('1. 概述', 1)

    overview = doc.add_paragraph(
        '本文档描述用户服务 API 接口规范。'
        '所有接口均采用 RESTful 风格设计，数据格式为 JSON。'
    )

    # 基本信息表格
    doc.add_heading('1.1 基本信息', 2)

    basic_table = doc.add_table(rows=4, cols=2)
    basic_table.style = 'Table Grid'

    basic_info = [
        ('Base URL', 'https://api.example.com/v2'),
        ('认证方式', 'Bearer Token（JWT）'),
        ('数据格式', 'application/json'),
        ('字符编码', 'UTF-8'),
    ]

    for i, (key, value) in enumerate(basic_info):
        row = basic_table.rows[i]
        key_cell = row.cells[0]
        key_cell.text = key
        # 设置背景色
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), 'E8F4FD')
        key_cell._tc.get_or_add_tcPr().append(shading_elm)

        row.cells[1].text = value

    doc.add_paragraph()  # 间距

    # ============ API 接口列表 ============
    doc.add_heading('2. 接口列表', 1)

    # 创建接口表格
    api_table = doc.add_table(rows=1, cols=4)
    api_table.style = 'Table Grid'
    api_table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 表头
    headers = ['Method', 'Path', '功能描述', '认证']
    header_row = api_table.rows[0]
    for i, header in enumerate(headers):
        cell = header_row.cells[i]
        cell.text = header
        # 表头背景色
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), '1A73E8')
        cell._tc.get_or_add_tcPr().append(shading)
        # 表头字体颜色
        run = cell.paragraphs[0].runs[0]
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.bold = True

    # 接口数据
    apis = [
        ('GET', '/users', '获取用户列表', '是'),
        ('POST', '/users', '创建用户', '是'),
        ('GET', '/users/{id}', '获取用户详情', '是'),
        ('PUT', '/users/{id}', '更新用户信息', '是'),
        ('DELETE', '/users/{id}', '删除用户', '是（管理员）'),
        ('POST', '/auth/login', '用户登录', '否'),
        ('POST', '/auth/logout', '退出登录', '是'),
        ('POST', '/auth/refresh', '刷新Token', '是'),
    ]

    for method, path, desc, auth in apis:
        row = api_table.add_row()
        row.cells[0].text = method
        row.cells[1].text = path
        row.cells[2].text = desc
        row.cells[3].text = auth

        # 根据 Method 设置颜色
        method_colors = {
            'GET': 'D4EDDA',    # 绿色
            'POST': 'CCE5FF',   # 蓝色
            'PUT': 'FFF3CD',    # 黄色
            'DELETE': 'F8D7DA', # 红色
        }
        if method in method_colors:
            shading = OxmlElement('w:shd')
            shading.set(qn('w:fill'), method_colors[method])
            row.cells[0]._tc.get_or_add_tcPr().append(shading)

    doc.add_paragraph()

    # ============ 代码示例 ============
    doc.add_heading('3. 代码示例', 1)
    doc.add_heading('3.1 获取用户列表', 2)

    # 代码块（使用等宽字体）
    code_para = doc.add_paragraph()
    code_run = code_para.add_run(
        'GET /users?page=1&size=20\n'
        'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    )
    code_run.font.name = 'Courier New'
    code_run.font.size = Pt(10)
    # 代码块背景
    pPr = code_para._p.get_or_add_pPr()
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), 'F4F4F4')
    pPr.append(shading)

    # 保存
    doc.save(output_path)
    print(f"✅ 文档已创建: {output_path}")


create_api_doc("api_documentation.docx")
```

---

### 示例 2: 批量处理合同文档

**用户请求**:
```
我有 100 份合同 Word 文档，
需要：
1. 提取每份合同的甲方、乙方、金额、日期
2. 汇总成 Excel 表格
```

**Claude 的解决方案**:

```python
from docx import Document
import pandas as pd
import re
import os
from pathlib import Path

def extract_contract_info(docx_path: str) -> dict:
    """从合同 Word 文档中提取关键信息"""
    doc = Document(docx_path)

    # 提取全文
    full_text = '\n'.join([para.text for para in doc.paragraphs])

    info = {
        'filename': Path(docx_path).name,
        'party_a': None,
        'party_b': None,
        'amount': None,
        'sign_date': None,
        'contract_no': None,
    }

    # 使用正则提取关键信息
    patterns = {
        'contract_no': r'合同(?:编号|号)[：:]\s*([A-Z0-9\-]+)',
        'party_a': r'甲方[：:]\s*(.+?)(?:\n|公司|有限)',
        'party_b': r'乙方[：:]\s*(.+?)(?:\n|公司|有限)',
        'amount': r'合同(?:金额|总价)[：:]\s*人民币\s*([\d,\.]+)\s*元',
        'sign_date': r'签订日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            info[field] = match.group(1).strip()

    return info


def batch_extract_contracts(folder_path: str, output_excel: str):
    """批量提取文件夹中所有合同信息"""
    contracts = []
    errors = []

    docx_files = list(Path(folder_path).glob('*.docx'))
    print(f"找到 {len(docx_files)} 份合同文档")

    for i, file_path in enumerate(docx_files, 1):
        try:
            print(f"  [{i}/{len(docx_files)}] 处理: {file_path.name}")
            info = extract_contract_info(str(file_path))
            contracts.append(info)
        except Exception as e:
            errors.append({'file': file_path.name, 'error': str(e)})

    # 保存到 Excel
    df = pd.DataFrame(contracts, columns=[
        'filename', 'contract_no', 'party_a', 'party_b', 'amount', 'sign_date'
    ])
    df.columns = ['文件名', '合同编号', '甲方', '乙方', '金额（元）', '签订日期']

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='合同汇总', index=False)
        if errors:
            pd.DataFrame(errors).to_excel(writer, sheet_name='处理错误', index=False)

    print(f"\n✅ 完成！共处理 {len(contracts)} 份，失败 {len(errors)} 份")
    print(f"结果已保存到: {output_excel}")


batch_extract_contracts('./contracts/', 'contracts_summary.xlsx')
```

---

### 示例 3: 添加批注和修订

**用户请求**:
```
审阅这份技术方案文档，在有问题的地方添加批注，
并用修订追踪模式修改几处不准确的描述
```

**Claude 的解决方案**:

```python
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def add_comment(doc, paragraph, comment_text: str, author: str = "Reviewer"):
    """为段落添加批注"""
    # 批注的 XML 结构
    comment_id = str(len(doc.part.comments._element.findall(qn('w:comment'))) + 1)

    # 创建批注元素
    comment = OxmlElement('w:comment')
    comment.set(qn('w:id'), comment_id)
    comment.set(qn('w:author'), author)
    comment.set(qn('w:date'), datetime.datetime.now().isoformat())

    comment_para = OxmlElement('w:p')
    comment_run = OxmlElement('w:r')
    comment_text_elem = OxmlElement('w:t')
    comment_text_elem.text = comment_text
    comment_run.append(comment_text_elem)
    comment_para.append(comment_run)
    comment.append(comment_para)

    # 将批注添加到文档的批注部分
    doc.part.comments._element.append(comment)

    # 在段落中添加批注标记
    p = paragraph._p
    comment_start = OxmlElement('w:commentRangeStart')
    comment_start.set(qn('w:id'), comment_id)
    comment_end = OxmlElement('w:commentRangeEnd')
    comment_end.set(qn('w:id'), comment_id)
    comment_ref = OxmlElement('w:r')
    comment_ref_rpr = OxmlElement('w:rPr')
    comment_ref_mark = OxmlElement('w:commentReference')
    comment_ref_mark.set(qn('w:id'), comment_id)
    comment_ref_rpr.append(comment_ref_mark)
    comment_ref.append(comment_ref_rpr)

    p.insert(0, comment_start)
    p.append(comment_end)
    p.append(comment_ref)

    return comment_id


def review_document(input_path: str, output_path: str):
    """审阅文档，添加批注"""
    doc = Document(input_path)

    comments_added = 0

    for para in doc.paragraphs:
        text = para.text.lower()

        # 根据内容模式添加相应批注
        if '理论上' in para.text or '可能' in para.text:
            add_comment(
                doc, para,
                "请提供更明确的技术规格，避免模糊表述",
                author="技术审阅"
            )
            comments_added += 1

        elif '最快' in para.text or '最好' in para.text:
            add_comment(
                doc, para,
                "需要量化指标，例如：响应时间 < 100ms",
                author="技术审阅"
            )
            comments_added += 1

        elif '待定' in para.text or 'TBD' in para.text.upper():
            add_comment(
                doc, para,
                "此处需要在提交前确认并补充",
                author="技术审阅"
            )
            comments_added += 1

    doc.save(output_path)
    print(f"✅ 文档审阅完成，添加了 {comments_added} 条批注")
    print(f"已保存到: {output_path}")


review_document("tech_proposal.docx", "tech_proposal_reviewed.docx")
```

---

### 示例 4: 模板文档批量生成

**用户请求**:
```
根据员工数据批量生成工资条 Word 文档，
使用统一的模板格式
```

**Claude 的解决方案**:

```python
from docx import Document
from docx.shared import Pt, RGBColor
from copy import deepcopy
import pandas as pd

# 员工数据
employees = [
    {'name': '张三', 'dept': '技术部', 'base': 15000, 'bonus': 3000, 'tax': 1500},
    {'name': '李四', 'dept': '产品部', 'base': 12000, 'bonus': 2000, 'tax': 1100},
    {'name': '王五', 'dept': '设计部', 'base': 10000, 'bonus': 1500, 'tax': 850},
]

def generate_payslip(employee: dict, output_path: str):
    """生成单个员工的工资条"""
    doc = Document()

    # 标题
    title = doc.add_heading('工资条', 0)
    title.alignment = 1  # 居中

    # 月份信息
    month_para = doc.add_paragraph('2026年1月')
    month_para.alignment = 1

    doc.add_paragraph()

    # 员工信息
    info_table = doc.add_table(rows=2, cols=4)
    info_table.style = 'Table Grid'

    info_data = [
        ['姓名', employee['name'], '部门', employee['dept']],
        ['发放日期', '2026-02-05', '工号', 'EMP001'],
    ]
    for i, row_data in enumerate(info_data):
        for j, cell_text in enumerate(row_data):
            cell = info_table.rows[i].cells[j]
            cell.text = cell_text
            if j % 2 == 0:  # 标签列加粗
                cell.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()

    # 薪资明细
    doc.add_heading('薪资明细', 2)

    salary_table = doc.add_table(rows=5, cols=2)
    salary_table.style = 'Table Grid'

    net = employee['base'] + employee['bonus'] - employee['tax']
    salary_data = [
        ('基本工资', f"¥{employee['base']:,.2f}"),
        ('绩效奖金', f"¥{employee['bonus']:,.2f}"),
        ('代扣税款', f"-¥{employee['tax']:,.2f}"),
        ('', ''),
        ('实发金额', f"¥{net:,.2f}"),
    ]

    for i, (label, value) in enumerate(salary_data):
        row = salary_table.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value

        # 实发金额特殊格式
        if label == '实发金额':
            for cell in row.cells:
                run = cell.paragraphs[0].runs
                if run:
                    run[0].font.bold = True
                    run[0].font.size = Pt(12)
                    run[0].font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

    # 签名区
    doc.add_paragraph()
    doc.add_paragraph('员工签收: ____________     日期: __________')

    doc.save(output_path)


# 批量生成
for emp in employees:
    output = f"payslip_{emp['name']}_2026_01.docx"
    generate_payslip(emp, output)
    print(f"✓ 已生成: {output}")

print(f"\n✅ 共生成 {len(employees)} 份工资条")
```

---

## 常用操作参考

### 文本格式设置

```python
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 添加段落并设置格式
para = doc.add_paragraph()
run = para.add_run("重要提示")
run.font.bold = True
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
para.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### 插入表格

```python
# 创建 3x4 表格
table = doc.add_table(rows=3, cols=4)
table.style = 'Table Grid'

# 设置单元格内容
table.cell(0, 0).text = "标题"
table.cell(1, 0).text = "数据"

# 合并单元格
cell = table.cell(0, 0).merge(table.cell(0, 1))
```

### 插入图片

```python
from docx.shared import Inches

doc.add_picture('logo.png', width=Inches(2))
```

### 提取文本

```python
# 提取所有段落文本
for para in doc.paragraphs:
    print(para.text)

# 提取表格数据
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text, end='\t')
        print()
```

---

## 常见问题

### Q1: 如何保留原文档的格式？

**A**: 使用 `Document()` 打开再修改：

```python
doc = Document("original.docx")
# 只修改需要的部分
para = doc.paragraphs[2]
para.runs[0].text = "新内容"
doc.save("modified.docx")
```

### Q2: 中文字体乱码怎么处理？

**A**: 明确指定字体：

```python
from docx.oxml.ns import qn

run = para.add_run("中文内容")
run.font.name = '微软雅黑'
# 设置东亚字体（处理中文）
run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
```

### Q3: 能生成带目录的文档吗？

**A**: python-docx 支持样式化标题，配合 Word 自动目录：

```python
# 使用标准标题样式
doc.add_heading('第一章', level=1)
doc.add_heading('1.1 节标题', level=2)

# 在 Word 中手动更新目录，或用 docx2pdf 等工具
```

---

## 相关 Skills

- [pdf](./pdf.md) - 处理 PDF 文档
- [project-planner](./project-planner.md) - 生成规划文档后导出 Word

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
