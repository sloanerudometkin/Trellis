from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import TABLOID, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUT = Path(__file__).with_name("Trellis_Data_Model.pdf")
PAGE_W, PAGE_H = landscape(TABLOID)

PURPLE = colors.HexColor("#9370DB")
HEADER = colors.HexColor("#ECEAFB")
GRID = colors.HexColor("#A98BE8")
INK = colors.HexColor("#3F3F46")
LINE = colors.HexColor("#666666")
WHITE = colors.white


ENTITIES = {
    "USER": [
        ("uuid", "id", "PK,FK"),
        ("string", "name", ""),
        ("string", "email", ""),
        ("datetime", "created_at", ""),
    ],
    "WEBSITE": [
        ("int", "id", "PK"),
        ("uuid", "user_id", "FK"),
        ("string", "url", ""),
        ("string", "business_name", ""),
        ("text", "business_context", ""),
        ("datetime", "created_at", ""),
    ],
    "ANALYSIS_RUN": [
        ("int", "id", "PK"),
        ("int", "website_id", "FK"),
        ("string", "status", ""),
        ("int", "pages_scanned_count", ""),
        ("int", "health_score", ""),
        ("text", "error_message", ""),
        ("datetime", "started_at", ""),
        ("datetime", "completed_at", ""),
    ],
    "KEYWORD": [
        ("int", "id", "PK"),
        ("int", "analysis_run_id", "FK"),
        ("string", "phrase", ""),
        ("int", "frequency", ""),
        ("decimal", "tfidf_score", ""),
        ("string", "search_intent", ""),
    ],
    "SUGGESTION": [
        ("int", "id", "PK"),
        ("int", "analysis_run_id", "FK"),
        ("string", "affected_page_url", ""),
        ("string", "category", ""),
        ("string", "title", ""),
        ("text", "description", ""),
        ("json", "starter_outline", ""),
        ("text", "rationale", ""),
        ("string", "priority", ""),
        ("string", "acceptance_status", ""),
        ("string", "dismiss_reason", ""),
        ("string", "cost_tier", ""),
        ("string", "ad_group_label", ""),
        ("text", "ad_copy_angle", ""),
        ("text", "landing_page_match", ""),
        ("text", "targeting_notes", ""),
        ("text[]", "negative_keywords", ""),
        ("int", "cheaper_alternative_to_id", "FK?"),
        ("datetime", "created_at", ""),
        ("datetime", "updated_at", ""),
    ],
    "TECHNICAL_FINDING": [
        ("int", "id", "PK"),
        ("int", "analysis_run_id", "FK"),
        ("string", "affected_page_url", ""),
        ("string", "related_page_url", ""),
        ("string", "finding_type", ""),
        ("string", "severity", ""),
        ("text", "explanation", ""),
        ("string", "resolution_status", ""),
        ("datetime", "resolved_at", ""),
        ("datetime", "created_at", ""),
    ],
    "SUGGESTION_KEYWORD": [
        ("int", "suggestion_id", "PK,FK"),
        ("int", "keyword_id", "PK,FK"),
        ("int", "recommended_usage_count", ""),
    ],
    "SUGGESTION_TECHNICAL_FINDING": [
        ("int", "suggestion_id", "PK,FK"),
        ("int", "technical_finding_id", "PK,FK"),
    ],
    "ORGANIZER_ITEM": [
        ("int", "id", "PK"),
        ("int", "website_id", "FK"),
        ("int", "suggestion_id", "FK,UQ"),
        ("string", "item_type", ""),
        ("string", "title", ""),
        ("string", "stage", ""),
        ("date", "due_date", ""),
        ("datetime", "created_at", ""),
        ("datetime", "updated_at", ""),
        ("datetime", "published_at", ""),
    ],
    "ORGANIZER_STAGE_HISTORY": [
        ("int", "id", "PK"),
        ("int", "organizer_item_id", "FK"),
        ("string", "from_stage", ""),
        ("string", "to_stage", ""),
        ("datetime", "changed_at", ""),
    ],
    "REPORT": [
        ("int", "id", "PK"),
        ("int", "analysis_run_id", "FK,UQ"),
        ("int", "website_id", "FK"),
        ("int", "health_score", ""),
        ("int", "health_score_delta", ""),
        ("decimal", "aeo_completion_pct", ""),
        ("decimal", "aeo_completion_delta", ""),
        ("int", "technical_findings_open", ""),
        ("int", "technical_findings_resolved", ""),
        ("int", "content_published_count", ""),
        ("json", "top_keywords", ""),
        ("int", "sem_accepted_count", ""),
        ("json", "sem_cost_tier_breakdown", ""),
        ("int", "ad_groups_defined_count", ""),
        ("json", "organizer_stage_counts", ""),
        ("int", "tasks_published_count", ""),
        ("text", "summary", ""),
        ("datetime", "generated_at", ""),
    ],
}


BOXES = {
    "USER": (535, 710, 154),
    "WEBSITE": (515, 575, 194),
    "ANALYSIS_RUN": (500, 415, 224),
    "KEYWORD": (150, 225, 158),
    "SUGGESTION": (397, 92, 216),
    "TECHNICAL_FINDING": (630, 205, 180),
    "REPORT": (826, 106, 205),
    "ORGANIZER_ITEM": (1045, 410, 170),
    "ORGANIZER_STAGE_HISTORY": (1010, 18, 205),
    "SUGGESTION_KEYWORD": (86, 45, 205),
    "SUGGESTION_TECHNICAL_FINDING": (640, 45, 230),
}


def box_height(name):
    return 20 + 11 * len(ENTITIES[name])


def anchor(name, side):
    x, y, w = BOXES[name]
    h = box_height(name)
    return {
        "top": (x + w / 2, y + h),
        "bottom": (x + w / 2, y),
        "left": (x, y + h / 2),
        "right": (x + w, y + h / 2),
    }[side]


def draw_table(c, name):
    x, y, w = BOXES[name]
    rows = ENTITIES[name]
    h = box_height(name)
    header_h = 20
    row_h = 11
    type_w = max(43, min(58, w * 0.27))
    key_w = 31
    field_w = w - type_w - key_w

    c.setFillColor(WHITE)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(HEADER)
    c.rect(x, y + h - header_h, w, header_h, fill=1, stroke=0)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(0.9)
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.line(x, y + h - header_h, x + w, y + h - header_h)

    c.setFillColor(INK)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(x + w / 2, y + h - 13, name)

    c.setStrokeColor(GRID)
    c.setLineWidth(0.45)
    c.line(x + type_w, y, x + type_w, y + h - header_h)
    c.line(x + type_w + field_w, y, x + type_w + field_w, y + h - header_h)
    for i in range(1, len(rows)):
        yy = y + i * row_h
        c.line(x, yy, x + w, yy)

    c.setFillColor(INK)
    c.setFont("Helvetica", 6.5)
    for i, (typ, field, key) in enumerate(rows):
        yy = y + (len(rows) - i - 1) * row_h + 3
        c.drawString(x + 4, yy, typ)
        c.drawString(x + type_w + 4, yy, field)
        if key:
            c.drawCentredString(x + type_w + field_w + key_w / 2, yy, key)


def draw_cardinality(c, x, y, text):
    c.setFillColor(WHITE)
    c.rect(x - 7, y - 5, 14, 10, fill=1, stroke=0)
    c.setFillColor(LINE)
    c.setFont("Helvetica", 6)
    c.drawCentredString(x, y - 2, text)


def polyline(c, points):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.75)
    path = c.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    c.drawPath(path, fill=0, stroke=1)


def relation_label(c, x, y, label):
    tw = stringWidth(label, "Helvetica", 6.5) + 8
    c.setFillColor(WHITE)
    c.rect(x - tw / 2, y - 5, tw, 10, fill=1, stroke=0)
    c.setFillColor(LINE)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(x, y - 2, label)


def draw_reference_page(c):
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica", 13)
    c.drawString(34, 750, "TRELLIS MVP RELATIONSHIP REFERENCE")
    c.setFont("Helvetica", 7.5)
    c.drawString(34, 735, "Use these rules when creating SQLAlchemy models, migrations, and database constraints.")

    rows = [
        ("Parent table", "Child table", "Cardinality", "Foreign key / constraint", "What it means"),
        ("users", "websites", "1 to 0..*", "websites.user_id -> users.id", "A user may manage many websites; every website has one user."),
        ("websites", "analysis_runs", "1 to 0..*", "analysis_runs.website_id -> websites.id", "A website may be scanned many times; every run belongs to one website."),
        ("analysis_runs", "keywords", "1 to 0..*", "keywords.analysis_run_id -> analysis_runs.id", "One run may discover many keyword candidates."),
        ("analysis_runs", "suggestions", "1 to 0..*", "suggestions.analysis_run_id -> analysis_runs.id", "One run may generate many AEO, SEO/content, and SEM suggestions."),
        ("analysis_runs", "technical_findings", "1 to 0..*", "technical_findings.analysis_run_id -> analysis_runs.id", "One run may detect many technical issues."),
        ("analysis_runs", "reports", "1 to 0..1", "reports.analysis_run_id FK + UNIQUE", "A completed run gets one immutable report; an unfinished run may have none."),
        ("websites", "reports", "1 to 0..*", "reports.website_id -> websites.id", "A website keeps report history across all runs."),
        ("websites", "organizer_items", "1 to 0..*", "organizer_items.website_id -> websites.id", "A website owns one ongoing task pipeline across multiple scans."),
        ("suggestions", "organizer_items", "1 to 0..1", "organizer_items.suggestion_id FK + UNIQUE", "An accepted suggestion may create one task; a task has one source suggestion."),
        ("organizer_items", "organizer_stage_history", "1 to 0..*", "stage_history.organizer_item_id -> organizer_items.id", "Every task can record many stage changes over time."),
        ("suggestions + keywords", "suggestion_keywords", "many to many", "composite PK: suggestion_id + keyword_id", "A suggestion can target many keywords; a keyword can support many suggestions."),
        ("suggestions + findings", "suggestion_technical_finding", "many to many", "composite PK: suggestion_id + finding_id", "A suggestion can address many findings and vice versa."),
        ("suggestions", "suggestions", "1 to 0..*", "cheaper_alternative_to_id nullable self-FK", "A lower-cost SEM suggestion can point back to the expensive suggestion it replaces."),
    ]

    x = 34
    y_top = 705
    widths = [145, 155, 80, 275, 495]
    row_h = 27
    total_w = sum(widths)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(0.8)
    for i, row in enumerate(rows):
        y = y_top - (i + 1) * row_h
        c.setFillColor(HEADER if i == 0 else WHITE)
        c.rect(x, y, total_w, row_h, fill=1, stroke=1)
        xx = x
        for j, (cell, width) in enumerate(zip(row, widths)):
            if j:
                c.line(xx, y, xx, y + row_h)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 6.8 if i == 0 else 6.2)
            c.drawString(xx + 4, y + 10, cell)
            xx += width

    notes_y = 190
    c.setFillColor(HEADER)
    c.setStrokeColor(PURPLE)
    c.rect(34, 42, 1156, 125, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(46, 150, "IMPLEMENTATION RULES")
    c.setFont("Helvetica", 7)
    rules = [
        "1. Keep suggestions.acceptance_status separate from organizer_items.stage: accepting work is not completing it.",
        "2. organizer_items.stage is the only stored work stage: backlog, in_production, in_review, published.",
        "3. Valid suggestion categories: aeo, seo_content, sem. Cost and ad fields remain NULL unless category = sem.",
        "4. Dismiss reasons: not_relevant, too_much_work, already_doing_this, other. Require a reason only when dismissed.",
        "5. Constrain health_score to 0-100 and enforce the unique rules listed on page 1.",
        "6. Reports are snapshots: never recalculate an old report when scoring logic changes; comparisons are computed from two saved rows.",
        "7. Process scraped content temporarily; store affected URLs on suggestions/findings, never raw HTML or page snapshots.",
    ]
    yy = 134
    for rule in rules:
        c.drawString(46, yy, rule)
        yy -= 13

    c.setFont("Helvetica-Oblique", 6.5)
    c.drawRightString(PAGE_W - 34, 24, "MVP scope only - excludes Phase 2 and Phase 3 integration tables")


def render():
    c = canvas.Canvas(str(OUT), pagesize=landscape(TABLOID), pageCompression=1)
    c.setTitle("Trellis Data Model")
    c.setAuthor("Trellis")
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Title and beginner-friendly cardinality key.
    c.setFillColor(INK)
    c.setFont("Helvetica", 12)
    c.drawString(24, 763, "TRELLIS MVP DATA MODEL")
    c.setFont("Helvetica", 7)
    c.drawString(24, 750, "Parent tables are above the records they own or produce.")
    c.setFont("Helvetica", 6.5)
    c.drawString(24, 735, "CORE UNIQUE RULES")
    c.drawString(24, 724, "users.email; websites(user_id, url); keywords(analysis_run_id, phrase);")
    c.drawString(24, 713, "reports.analysis_run_id; organizer_items.suggestion_id")
    c.drawString(24, 695, "CORE ENUMS")
    c.drawString(24, 684, "acceptance_status: pending / accepted / dismissed")
    c.drawString(24, 673, "stage: backlog / in_production / in_review / published")
    c.drawRightString(PAGE_W - 24, 763, "CARDINALITY:  1 = exactly one     0..1 = optional one     0..* = zero or many")
    c.drawRightString(PAGE_W - 24, 750, "PK = primary key     FK = foreign key     UQ = unique")

    # Relationship paths. The shared horizontal line under ANALYSIS_RUN makes its
    # four direct outputs visually explicit.
    user_b = anchor("USER", "bottom")
    website_t = anchor("WEBSITE", "top")
    website_b = anchor("WEBSITE", "bottom")
    analysis_t = anchor("ANALYSIS_RUN", "top")
    analysis_b = anchor("ANALYSIS_RUN", "bottom")
    polyline(c, [user_b, website_t])
    polyline(c, [website_b, analysis_t])

    bus_y = 385
    child_tops = [anchor(n, "top") for n in (
        "KEYWORD", "SUGGESTION", "TECHNICAL_FINDING", "REPORT"
    )]
    polyline(c, [analysis_b, (analysis_b[0], bus_y), (child_tops[0][0], bus_y)])
    polyline(c, [(child_tops[0][0], bus_y), (child_tops[-1][0], bus_y)])
    for top in child_tops:
        polyline(c, [(top[0], bus_y), top])

    # WEBSITE owns Organizer items; an accepted SUGGESTION optionally becomes one.
    website_r = anchor("WEBSITE", "right")
    organizer_t = anchor("ORGANIZER_ITEM", "top")
    polyline(c, [website_r, (organizer_t[0], website_r[1]), organizer_t])
    suggestion_t = anchor("SUGGESTION", "top")
    organizer_l = anchor("ORGANIZER_ITEM", "left")
    polyline(c, [(suggestion_t[0], suggestion_t[1]), (suggestion_t[0], 398),
                 (1028, 398), (1028, organizer_l[1]), organizer_l])
    polyline(c, [anchor("ORGANIZER_ITEM", "bottom"), anchor("ORGANIZER_STAGE_HISTORY", "top")])

    # Many-to-many bridge tables.
    polyline(c, [anchor("KEYWORD", "bottom"), anchor("SUGGESTION_KEYWORD", "top")])
    polyline(c, [anchor("SUGGESTION", "left"), (330, anchor("SUGGESTION", "left")[1]),
                 (330, 90), (291, 90)])
    polyline(c, [anchor("TECHNICAL_FINDING", "bottom"), anchor("SUGGESTION_TECHNICAL_FINDING", "top")])
    polyline(c, [anchor("SUGGESTION", "right"), (620, anchor("SUGGESTION", "right")[1]),
                 (620, 90), (640, 90)])

    for name in ENTITIES:
        draw_table(c, name)

    # Cardinalities and relationship names are drawn after tables so they remain visible.
    draw_cardinality(c, user_b[0], user_b[1] - 10, "1")
    draw_cardinality(c, website_t[0], website_t[1] + 10, "0..*")
    relation_label(c, user_b[0] + 28, (user_b[1] + website_t[1]) / 2, "manages")
    draw_cardinality(c, website_b[0], website_b[1] - 10, "1")
    draw_cardinality(c, analysis_t[0], analysis_t[1] + 10, "0..*")
    relation_label(c, website_b[0] + 30, (website_b[1] + analysis_t[1]) / 2, "has runs")

    child_cards = ["0..*", "0..*", "0..*", "0..1"]
    child_labels = ["discovers", "generates", "detects", "produces"]
    for top, card, label in zip(child_tops, child_cards, child_labels):
        draw_cardinality(c, top[0], top[1] + 9, card)
        relation_label(c, top[0], bus_y - 8, label)
    draw_cardinality(c, analysis_b[0], analysis_b[1] - 10, "1")

    draw_cardinality(c, website_r[0] + 11, website_r[1], "1")
    draw_cardinality(c, organizer_t[0], organizer_t[1] + 9, "0..*")
    relation_label(c, 974, website_r[1], "organizes")
    draw_cardinality(c, suggestion_t[0] + 14, 398, "1")
    draw_cardinality(c, organizer_l[0] - 12, organizer_l[1], "0..1")
    relation_label(c, 1000, organizer_l[1] - 10, "becomes when accepted")
    draw_cardinality(c, anchor("ORGANIZER_ITEM", "bottom")[0], anchor("ORGANIZER_ITEM", "bottom")[1] - 9, "1")
    draw_cardinality(c, anchor("ORGANIZER_STAGE_HISTORY", "top")[0], anchor("ORGANIZER_STAGE_HISTORY", "top")[1] + 9, "0..*")
    relation_label(c, 1130, 305, "records stage changes")

    relation_label(c, 190, 118, "links")
    relation_label(c, 750, 118, "links")
    draw_cardinality(c, 301, anchor("KEYWORD", "bottom")[1] - 9, "1")
    draw_cardinality(c, 188, anchor("SUGGESTION_KEYWORD", "top")[1] + 9, "0..*")
    draw_cardinality(c, 411, anchor("SUGGESTION", "left")[1], "1")
    draw_cardinality(c, 303, 90, "0..*")
    draw_cardinality(c, 720, anchor("TECHNICAL_FINDING", "bottom")[1] - 9, "1")
    draw_cardinality(c, 755, anchor("SUGGESTION_TECHNICAL_FINDING", "top")[1] + 9, "0..*")
    draw_cardinality(c, 601, anchor("SUGGESTION", "right")[1], "1")
    draw_cardinality(c, 632, 90, "0..*")

    c.showPage()
    draw_reference_page(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    render()
