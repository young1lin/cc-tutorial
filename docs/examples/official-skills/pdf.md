# Skill: pdf

## 概述

`pdf` 是全面的 PDF 文档操作工具包 Skill，支持从 PDF 提取文本和表格、创建新 PDF、合并/拆分文档，以及处理 PDF 表单。

**核心能力**:
- 提取 PDF 中的文本内容
- 提取 PDF 中的表格数据
- 以编程方式创建新 PDF
- 合并多个 PDF 文件
- 拆分 PDF 文件
- 填写 PDF 表单

---

## 触发方式

### 斜杠命令

```bash
/pdf
```

### 自然语言触发

```
"从这个 PDF 中提取文本"
"读取 PDF 里的表格数据"
"合并这几个 PDF"
"创建一个 PDF 报告"
"填写这个 PDF 表单"
```

---

## 实际演示

### 示例 1: 提取 PDF 文本

**用户请求**:
```
从 contract.pdf 中提取所有文本内容，
特别是合同金额、签署日期和甲乙双方信息
```

**Claude 使用 PyMuPDF（fitz）处理**:

```python
import fitz  # pip install pymupdf

def extract_pdf_text(pdf_path: str) -> str:
    """提取 PDF 全文"""
    doc = fitz.open(pdf_path)
    text_parts = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_parts.append(f"--- 第 {page_num + 1} 页 ---\n{text}")

    doc.close()
    return "\n\n".join(text_parts)


# 提取文本
text = extract_pdf_text("contract.pdf")
print(text)
```

**提取结果示例**:

```
--- 第 1 页 ---
合同编号：HT-2026-001

甲方：北京科技有限公司
代表人：张总
地址：北京市朝阳区...

乙方：上海软件开发有限公司
代表人：李总
地址：上海市浦东新区...

合同金额：人民币 500,000.00 元（大写：伍拾万元整）
签署日期：2026年2月1日
```

**Claude 的分析**:

```
合同关键信息提取：

甲方: 北京科技有限公司
乙方: 上海软件开发有限公司
合同金额: ¥500,000.00（伍拾万元整）
签署日期: 2026年2月1日
合同编号: HT-2026-001
```

---

### 示例 2: 提取 PDF 表格

**用户请求**:
```
这个 PDF 报告里有财务数据表格，
帮我把数据提取出来，整理成 Excel 格式
```

**Claude 使用 pdfplumber 处理**:

```python
import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path: str) -> list[pd.DataFrame]:
    """提取 PDF 中的所有表格"""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()

            for table_idx, table in enumerate(page_tables):
                if not table:
                    continue

                # 第一行作为列名
                headers = table[0]
                rows = table[1:]

                df = pd.DataFrame(rows, columns=headers)
                df['_source_page'] = page_num + 1
                df['_table_index'] = table_idx
                tables.append(df)
                print(f"  第{page_num+1}页 表格{table_idx+1}: {len(rows)}行 x {len(headers)}列")

    return tables


# 提取并保存
tables = extract_tables_from_pdf("financial_report.pdf")

# 保存到 Excel（多个 Sheet）
with pd.ExcelWriter("extracted_data.xlsx", engine='openpyxl') as writer:
    for i, df in enumerate(tables):
        sheet_name = f"表格_{i+1}_第{df['_source_page'].iloc[0]}页"
        df.drop(columns=['_source_page', '_table_index']).to_excel(
            writer,
            sheet_name=sheet_name,
            index=False
        )

print(f"\n共提取 {len(tables)} 个表格，已保存到 extracted_data.xlsx")
```

**提取结果**:

```
提取到表格:
  第1页 表格1: 12行 x 5列 → 季度销售数据
  第2页 表格1: 8行 x 4列 → 费用明细
  第3页 表格1: 15行 x 6列 → 产品利润分析

共提取 3 个表格，已保存到 extracted_data.xlsx
```

---

### 示例 3: 创建 PDF 报告

**用户请求**:
```
根据这份销售数据，生成一份 PDF 月度报告，
包含标题、数据表格和图表
```

**Claude 使用 ReportLab 创建**:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# 注册中文字体（需要字体文件）
# pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))

def create_monthly_report(data: dict, output_path: str):
    """创建月度销售报告 PDF"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # 标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=6,
        alignment=1,  # 居中
    )
    elements.append(Paragraph("2026年1月 销售月报", title_style))

    # 副标题
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=20,
        alignment=1,
    )
    elements.append(Paragraph("报告生成时间：2026-02-01", subtitle_style))

    # 分割线
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 20))

    # 关键指标
    kpi_style = ParagraphStyle(
        'KPI',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
    )
    elements.append(Paragraph("关键指标", kpi_style))

    # KPI 表格
    kpi_data = [
        ['指标', '本月实际', '目标', '达成率'],
        ['总销售额', '¥1,250,000', '¥1,200,000', '104.2%'],
        ['新客户数', '523', '500', '104.6%'],
        ['客户满意度', '4.7/5.0', '4.5/5.0', '104.4%'],
        ['退款率', '1.2%', '<2%', '✓ 达标'],
    ]

    kpi_table = Table(kpi_data, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])
    kpi_table.setStyle(TableStyle([
        # 表头样式
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),

        # 对齐
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # 行高
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

        # 边框
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BOX', (0, 0), (-1, -1), 1, colors.gray),

        # 内边距
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 30))

    # 产品销售明细
    elements.append(Paragraph("产品销售明细", kpi_style))

    product_data = [
        ['产品', '销量', '单价', '销售额', '同比'],
        ['产品A', '1,234', '¥299', '¥368,966', '+12%'],
        ['产品B', '892', '¥599', '¥534,308', '+8%'],
        ['产品C', '456', '¥999', '¥455,544', '+15%'],
        ['其他', '203', '-', '¥91,182', '+5%'],
        ['合计', '2,785', '-', '¥1,250,000', '+10.5%'],
    ]

    product_table = Table(
        product_data,
        colWidths=[4*cm, 3*cm, 3*cm, 4*cm, 2.5*cm]
    )
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(product_table)

    # 生成 PDF
    doc.build(elements)
    print(f"PDF 报告已生成: {output_path}")


# 生成报告
create_monthly_report({}, "monthly_report_2026_01.pdf")
```

---

### 示例 4: 合并 PDF 文件

**用户请求**:
```
将本月所有的发票 PDF（invoice_001.pdf 到 invoice_020.pdf）
合并成一个汇总文件，并在每个文件前加上书签
```

**Claude 的解决方案**:

```python
import fitz
import os
from pathlib import Path

def merge_pdfs_with_bookmarks(
    input_files: list[str],
    output_path: str
) -> None:
    """
    合并多个 PDF 文件，并为每个文件添加书签

    Args:
        input_files: 输入 PDF 文件路径列表（按顺序）
        output_path: 输出文件路径
    """
    merged = fitz.open()
    toc = []  # 目录（Table of Contents）

    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"⚠️  文件不存在: {file_path}")
            continue

        # 计算当前合并文档的总页数（插入位置）
        current_page = len(merged)

        # 插入文档
        src = fitz.open(file_path)
        merged.insert_pdf(src)
        src.close()

        # 添加书签（1级标题，页码从1开始）
        file_name = Path(file_path).stem
        toc.append([1, file_name, current_page + 1])

        print(f"  ✓ 已合并: {file_name} ({len(merged)-current_page} 页)")

    # 设置目录
    merged.set_toc(toc)

    # 保存
    merged.save(output_path)
    merged.close()
    print(f"\n✅ 合并完成: {output_path} (共 {len(toc)} 个文件)")


# 获取所有发票文件
invoice_files = sorted([
    f"invoice_{i:03d}.pdf" for i in range(1, 21)
    if os.path.exists(f"invoice_{i:03d}.pdf")
])

merge_pdfs_with_bookmarks(
    input_files=invoice_files,
    output_path="invoices_2026_01_merged.pdf"
)
```

**输出**:
```
  ✓ 已合并: invoice_001 (2 页)
  ✓ 已合并: invoice_002 (1 页)
  ...
  ✓ 已合并: invoice_020 (3 页)

✅ 合并完成: invoices_2026_01_merged.pdf (共 20 个文件)
```

---

### 示例 5: 填写 PDF 表单

**用户请求**:
```
这是一份政府申请表（application_form.pdf），
帮我自动填写以下信息并生成填好的 PDF
```

**Claude 的解决方案**:

```python
import fitz

def fill_pdf_form(
    template_path: str,
    field_data: dict,
    output_path: str
) -> None:
    """
    填写 PDF 表单字段

    Args:
        template_path: 模板 PDF 路径
        field_data: 字段名 → 值 的映射
        output_path: 输出路径
    """
    doc = fitz.open(template_path)

    # 遍历所有页面的表单字段
    for page in doc:
        for widget in page.widgets():
            field_name = widget.field_name

            if field_name in field_data:
                value = field_data[field_name]

                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    widget.field_value = str(value)
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                    widget.field_value = bool(value)
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                    widget.field_value = str(value)
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_COMBOBOX:
                    widget.field_value = str(value)

                widget.update()

    # 保存填写后的 PDF
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"✅ 表单已填写并保存到: {output_path}")


# 先查看可用字段
def list_form_fields(pdf_path: str) -> dict:
    """查看 PDF 中的所有表单字段"""
    doc = fitz.open(pdf_path)
    fields = {}
    for page_num, page in enumerate(doc):
        for widget in page.widgets():
            fields[widget.field_name] = {
                'type': widget.field_type_string,
                'page': page_num + 1,
                'current_value': widget.field_value
            }
    doc.close()
    return fields

# 查看字段
fields = list_form_fields("application_form.pdf")
print("可用字段:", fields)

# 填写表单
fill_pdf_form(
    template_path="application_form.pdf",
    field_data={
        "applicant_name": "张三",
        "id_number": "110101199001011234",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "北京市朝阳区...",
        "agree_terms": True,
    },
    output_path="application_form_filled.pdf"
)
```

---

## 常用库对比

| 任务 | 推荐库 | 安装命令 |
|------|--------|---------|
| 提取文本 | PyMuPDF (fitz) | `pip install pymupdf` |
| 提取表格 | pdfplumber | `pip install pdfplumber` |
| 创建 PDF | ReportLab | `pip install reportlab` |
| 合并/拆分 | PyMuPDF | `pip install pymupdf` |
| 填写表单 | PyMuPDF | `pip install pymupdf` |
| 复杂布局 | WeasyPrint | `pip install weasyprint` |

---

## 处理大型 PDF

```python
# 分批处理大型 PDF（避免内存溢出）
def process_large_pdf(pdf_path: str, batch_size: int = 50):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    for start in range(0, total_pages, batch_size):
        end = min(start + batch_size, total_pages)
        print(f"处理第 {start+1}-{end} 页...")

        for page_num in range(start, end):
            page = doc.load_page(page_num)
            # 处理页面...
            text = page.get_text()
            process_page_text(text)

    doc.close()
```

---

## 常见问题

### Q1: 提取的文本乱码怎么处理？

**A**: 通常是字体编码问题：

```python
# 尝试不同的提取模式
text = page.get_text("text")    # 普通文本
text = page.get_text("html")    # HTML 格式（保留更多格式信息）
text = page.get_text("blocks")  # 按文本块提取
```

### Q2: 扫描版 PDF 如何处理？

**A**: 扫描版 PDF 需要 OCR：

```python
# 使用 pytesseract 进行 OCR
import pytesseract
from PIL import Image
import fitz

doc = fitz.open("scanned.pdf")
page = doc.load_page(0)

# 将页面渲染为图像
mat = fitz.Matrix(3, 3)  # 放大3倍以提高 OCR 精度
clip = page.rect
pix = page.get_pixmap(matrix=mat, clip=clip)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# OCR 识别
text = pytesseract.image_to_string(img, lang='chi_sim+eng')
print(text)
```

### Q3: 如何处理加密 PDF？

**A**:

```python
doc = fitz.open("encrypted.pdf")
if doc.is_encrypted:
    success = doc.authenticate("password123")
    if not success:
        raise ValueError("密码错误")
```

---

## 相关 Skills

- [docx](./docx.md) - 处理 Word 文档
- [project-planner](./project-planner.md) - 生成规划文档

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
