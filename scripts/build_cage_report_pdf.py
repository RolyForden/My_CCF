from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


PAGE_W, PAGE_H = A4
INK = colors.HexColor("#1D252C")
MUTED = colors.HexColor("#5D6A72")
NAVY = colors.HexColor("#173B57")
TEAL = colors.HexColor("#167D7F")
CORAL = colors.HexColor("#C65345")
GOLD = colors.HexColor("#C69332")
PALE_BLUE = colors.HexColor("#EAF2F7")
PALE_TEAL = colors.HexColor("#E7F3F1")
PALE_GOLD = colors.HexColor("#F8F0DE")
GRID = colors.HexColor("#C9D2D8")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("CJK", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("CJK-Bold", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))
    pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK-Bold")


class Cover(Flowable):
    def __init__(self) -> None:
        super().__init__()
        self.width = PAGE_W
        self.height = PAGE_H

    def draw(self) -> None:
        c = self.canv
        c.saveState()
        c.setFillColor(colors.HexColor("#F4F7F8"))
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.rect(0, PAGE_H - 18 * mm, PAGE_W, 18 * mm, fill=1, stroke=0)
        c.setFillColor(CORAL)
        c.rect(0, 0, PAGE_W, 7 * mm, fill=1, stroke=0)

        c.setFont("CJK-Bold", 27)
        c.setFillColor(NAVY)
        c.drawString(23 * mm, PAGE_H - 58 * mm, "CAGE")
        c.setFont("CJK-Bold", 20)
        c.drawString(23 * mm, PAGE_H - 72 * mm, "Query Control 在三维功能区域定位中的")
        c.drawString(23 * mm, PAGE_H - 84 * mm, "传播、衰减与因果定位")

        c.setStrokeColor(TEAL)
        c.setLineWidth(2)
        c.line(23 * mm, PAGE_H - 93 * mm, 166 * mm, PAGE_H - 93 * mm)
        c.setFont("CJK", 11)
        c.setFillColor(MUTED)
        c.drawString(23 * mm, PAGE_H - 103 * mm, "研究方案报告  |  导师讨论初稿  |  v0.1")

        labels = ["q", "E_q", "Fusion", "Z_point", "Decoder", "Mask"]
        fills = [PALE_GOLD, PALE_BLUE, PALE_TEAL, PALE_BLUE, PALE_GOLD, colors.HexColor("#F7E9E6")]
        x0, y0 = 20 * mm, PAGE_H - 145 * mm
        box_w, box_h, gap = 24 * mm, 15 * mm, 5 * mm
        for i, label in enumerate(labels):
            x = x0 + i * (box_w + gap)
            c.setFillColor(fills[i])
            c.setStrokeColor([GOLD, NAVY, TEAL, NAVY, GOLD, CORAL][i])
            c.roundRect(x, y0, box_w, box_h, 2.5 * mm, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont("CJK-Bold", 9.5)
            c.drawCentredString(x + box_w / 2, y0 + 5.2 * mm, label)
            if i < len(labels) - 1:
                c.setStrokeColor(MUTED)
                c.line(x + box_w, y0 + box_h / 2, x + box_w + gap - 1 * mm, y0 + box_h / 2)
                c.line(x + box_w + gap - 2.5 * mm, y0 + box_h / 2 + 1.2 * mm, x + box_w + gap - 1 * mm, y0 + box_h / 2)
                c.line(x + box_w + gap - 2.5 * mm, y0 + box_h / 2 - 1.2 * mm, x + box_w + gap - 1 * mm, y0 + box_h / 2)

        c.setFillColor(colors.white)
        c.setStrokeColor(GRID)
        c.roundRect(22 * mm, 62 * mm, 166 * mm, 50 * mm, 3 * mm, fill=1, stroke=1)
        c.setFillColor(CORAL)
        c.setFont("CJK-Bold", 12)
        c.drawString(30 * mm, 98 * mm, "研究对象")
        c.setFillColor(INK)
        c.setFont("CJK", 10.2)
        lines = [
            "CAGE 是 measurement apparatus，不是 method。",
            "先确认 behaviour，再定位 representation，最后做 causal intervention。",
            "D2 通过前，正式方法保持空白。",
        ]
        for idx, line in enumerate(lines):
            c.drawString(30 * mm, (87 - idx * 9) * mm, line)

        c.setFillColor(MUTED)
        c.setFont("CJK", 9)
        c.drawString(23 * mm, 32 * mm, "状态：IDEA / PENDING  ·  无实验结果  ·  版本日期：2026-09-20")
        c.restoreState()


class PipelineDiagram(Flowable):
    def __init__(self, width: float) -> None:
        super().__init__()
        self.width = width
        self.height = 38 * mm

    def draw(self) -> None:
        c = self.canv
        stages = [
            ("D0", "Behaviour", CORAL),
            ("D1", "Localization", NAVY),
            ("D2", "Intervention", TEAL),
            ("D3", "Method", GOLD),
        ]
        gap = 5 * mm
        w = (self.width - 3 * gap) / 4
        y = 8 * mm
        for idx, (code, label, color) in enumerate(stages):
            x = idx * (w + gap)
            c.setFillColor(colors.white)
            c.setStrokeColor(color)
            c.setLineWidth(1.2)
            c.roundRect(x, y, w, 22 * mm, 2 * mm, fill=1, stroke=1)
            c.setFillColor(color)
            c.rect(x, y + 15 * mm, w, 7 * mm, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("CJK-Bold", 9)
            c.drawCentredString(x + w / 2, y + 17.2 * mm, code)
            c.setFillColor(INK)
            c.setFont("CJK-Bold", 8.5)
            c.drawCentredString(x + w / 2, y + 7.5 * mm, label)
            if idx < 3:
                c.setStrokeColor(MUTED)
                c.line(x + w, y + 11 * mm, x + w + gap - 1 * mm, y + 11 * mm)


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r'<font name="CJK" color="#A33F32">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(
        r"https?://[^\s<]+",
        lambda m: f'<link href="{m.group(0)}" color="#156A8A">[链接]</link>',
        escaped,
    )
    return escaped


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "BodyCJK", parent=base["BodyText"], fontName="CJK", fontSize=9.4,
            leading=15.2, textColor=INK, alignment=TA_LEFT, wordWrap="CJK",
            spaceAfter=3.5 * mm,
        ),
        "h1": ParagraphStyle(
            "H1CJK", parent=base["Heading1"], fontName="CJK-Bold", fontSize=16,
            leading=22, textColor=NAVY, wordWrap="CJK", spaceBefore=4 * mm,
            spaceAfter=3 * mm, borderColor=TEAL, borderWidth=0, borderPadding=(0, 0, 2, 0),
        ),
        "h2": ParagraphStyle(
            "H2CJK", parent=base["Heading2"], fontName="CJK-Bold", fontSize=11.5,
            leading=17, textColor=CORAL, wordWrap="CJK", spaceBefore=3 * mm,
            spaceAfter=2 * mm,
        ),
        "quote": ParagraphStyle(
            "QuoteCJK", parent=base["BodyText"], fontName="CJK-Bold", fontSize=10.2,
            leading=16, textColor=NAVY, backColor=PALE_BLUE, borderColor=NAVY,
            borderWidth=0.8, borderPadding=8, leftIndent=4 * mm, rightIndent=4 * mm,
            wordWrap="CJK", spaceBefore=2 * mm, spaceAfter=4 * mm,
        ),
        "bullet": ParagraphStyle(
            "BulletCJK", parent=base["BodyText"], fontName="CJK", fontSize=9.2,
            leading=14.4, textColor=INK, wordWrap="CJK", leftIndent=4 * mm,
            firstLineIndent=0, spaceAfter=1.2 * mm,
        ),
        "small": ParagraphStyle(
            "SmallCJK", parent=base["BodyText"], fontName="CJK", fontSize=7.6,
            leading=11.2, textColor=INK, wordWrap="CJK",
        ),
        "table_header": ParagraphStyle(
            "TableHeader", parent=base["BodyText"], fontName="CJK-Bold", fontSize=7.6,
            leading=10.5, textColor=colors.white, wordWrap="CJK", alignment=TA_CENTER,
        ),
        "caption": ParagraphStyle(
            "CaptionCJK", parent=base["BodyText"], fontName="CJK", fontSize=7.8,
            leading=11, textColor=MUTED, wordWrap="CJK", alignment=TA_CENTER,
        ),
    }


def parse_table(lines: list[str], styles: dict[str, ParagraphStyle], usable_width: float) -> Table:
    rows: list[list[str]] = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]+", c or "-") for c in cells):
            continue
        rows.append(cells)
    ncols = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (ncols - len(row)))
    if ncols == 4:
        col_widths = [0.18 * usable_width, 0.28 * usable_width, 0.20 * usable_width, 0.34 * usable_width]
    elif ncols == 3:
        col_widths = [0.22 * usable_width, 0.38 * usable_width, 0.40 * usable_width]
    else:
        col_widths = [usable_width / ncols] * ncols
    data = []
    for r_idx, row in enumerate(rows):
        style = styles["table_header"] if r_idx == 0 else styles["small"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7F8")]),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def markdown_to_story(md_path: Path, styles: dict[str, ParagraphStyle], usable_width: float) -> list[Flowable]:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("## 一句话概括"))
    lines = lines[start:]
    story: list[Flowable] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), styles["body"]))
            paragraph.clear()

    i = 0
    pipeline_inserted = False
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            story.append(parse_table(block, styles, usable_width))
            story.append(Spacer(1, 4 * mm))
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), styles["h1"]))
            if stripped.startswith("## 5.") and not pipeline_inserted:
                story.append(PipelineDiagram(usable_width))
                pipeline_inserted = True
            i += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            story.append(Paragraph(inline_markup(" ".join(quote_lines)), styles["quote"]))
            continue
        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        number_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if bullet_match or number_match:
            flush_paragraph()
            items = []
            ordered = bool(number_match)
            while i < len(lines):
                current = lines[i].strip()
                match = re.match(r"^\d+\.\s+(.*)$", current) if ordered else re.match(r"^[-*]\s+(.*)$", current)
                if not match:
                    break
                items.append(ListItem(Paragraph(inline_markup(match.group(1)), styles["bullet"]), leftIndent=4 * mm))
                i += 1
            list_args = {
                "bulletType": "1" if ordered else "bullet",
                "leftIndent": 7 * mm,
                "bulletFontName": "CJK",
                "bulletFontSize": 8,
                "bulletColor": TEAL,
                "spaceAfter": 2 * mm,
            }
            if ordered:
                list_args["start"] = "1"
            story.append(ListFlowable(items, **list_args))
            continue
        if stripped == "---":
            flush_paragraph()
            story.append(Spacer(1, 2 * mm))
            i += 1
            continue
        paragraph.append(stripped)
        i += 1
    flush_paragraph()
    return story


def body_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, PAGE_H - 16 * mm, PAGE_W - 18 * mm, PAGE_H - 16 * mm)
    canvas.setFont("CJK-Bold", 7.8)
    canvas.setFillColor(NAVY)
    canvas.drawString(18 * mm, PAGE_H - 12 * mm, "CAGE Mechanism Research Report v0.1")
    canvas.setFont("CJK", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - 18 * mm, 11 * mm, f"第 {doc.page - 1} 页")
    canvas.restoreState()


def build_pdf(md_path: Path, out_path: Path) -> None:
    register_fonts()
    styles = make_styles()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm,
        title="CAGE: Query Control 在三维功能区域定位中的传播、衰减与因果定位",
        author="科研总控台项目",
        subject="Mechanism-discovery research plan",
    )
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    body_frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
        id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame]),
        PageTemplate(id="Body", frames=[body_frame], onPage=body_page),
    ])
    story: list[Flowable] = [Cover(), NextPageTemplate("Body"), PageBreak()]
    story.extend(markdown_to_story(md_path, styles, doc.width))
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build_pdf(args.source, args.output)


if __name__ == "__main__":
    main()
