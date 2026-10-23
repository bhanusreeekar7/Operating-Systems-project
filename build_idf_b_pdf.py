"""
Generate PredictiveGuard_IDF_B.pdf matching the exact 3-page format of SHIFT_IDF_B_TNR9.pdf.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas supporting total page count if needed, or precise header/footer stamping."""
    pass

def generate_idf_pdf():
    pdf_filename = "PredictiveGuard_IDF_B_v1.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=22,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    
    # Custom styles matching Times New Roman 8.8pt, leading 10.5pt
    style_normal = ParagraphStyle(
        'IDF_Normal',
        fontName='Times-Roman',
        fontSize=8.6,
        leading=10.4,
        textColor=colors.black,
        spaceAfter=3
    )

    style_bold_heading = ParagraphStyle(
        'IDF_Heading',
        fontName='Times-Bold',
        fontSize=8.9,
        leading=11,
        textColor=colors.black,
        spaceBefore=3,
        spaceAfter=2
    )

    style_bullet = ParagraphStyle(
        'IDF_Bullet',
        fontName='Times-Roman',
        fontSize=8.6,
        leading=10.4,
        textColor=colors.black,
        leftIndent=10,
        spaceAfter=2
    )

    style_tbl_cell = ParagraphStyle(
        'IDF_TblCell',
        fontName='Times-Roman',
        fontSize=7.6,
        leading=9.2,
        textColor=colors.black
    )

    style_tbl_header = ParagraphStyle(
        'IDF_TblHeader',
        fontName='Times-Bold',
        fontSize=7.8,
        leading=9.5,
        textColor=colors.black
    )

    style_meta_label = ParagraphStyle(
        'IDF_MetaLabel',
        fontName='Helvetica',
        fontSize=7.9,
        leading=9.5,
        textColor=colors.black
    )

    style_meta_val = ParagraphStyle(
        'IDF_MetaVal',
        fontName='Helvetica',
        fontSize=7.9,
        leading=9.5,
        textColor=colors.black
    )

    story = []

    # ── Header Helper Function ───────────────────────────────────────────────
    def make_header_table():
        logo_path = os.path.join("extracted_ref", "idf_p1_img0_55.png")
        if os.path.exists(logo_path):
            img = RLImage(logo_path, width=105, height=34)
        else:
            img = Paragraph("<b>VIT</b>", style_normal)

        title_cell = Paragraph(
            "<b><font size='11.5'>Invention<br/>Disclosure Format (IDF)-B</font></b>",
            ParagraphStyle('TitleC', fontName='Times-Roman', alignment=1, leading=14)
        )

        doc_box_data = [
            [Paragraph("Document No.", style_meta_label), Paragraph("02-IPR-R003", style_meta_val)],
            [Paragraph("Issue No/Date", style_meta_label), Paragraph("2/01.02.2024", style_meta_val)],
            [Paragraph("Amd. No/Date", style_meta_label), Paragraph("0/00.00.0000", style_meta_val)],
        ]
        doc_box_tbl = Table(doc_box_data, colWidths=[75, 75])
        doc_box_tbl.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))

        header_data = [
            [Paragraph("<font color='#365f91' size='13.5'><b>©VIT IPR&TTCELL</b></font>", ParagraphStyle('H', fontName='Helvetica-Bold')), "", ""],
            [img, title_cell, doc_box_tbl]
        ]
        h_table = Table(header_data, colWidths=[120, 245, 150])
        h_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('SPAN', (0,0), (2,0)),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,1), 0),
            ('BOTTOMPADDING', (0,1), (-1,1), 4),
            ('ALIGN', (1,1), (1,1), 'CENTER'),
        ]))
        return h_table

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 1
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_header_table())
    story.append(Spacer(1, 4))

    # 1. Title
    story.append(Paragraph("<b>1. Title of the invention:</b>", style_bold_heading))
    story.append(Paragraph("PredictiveGuard – AI-Based Predictive Failure Detection & Autonomous Recovery: An Intelligent Multi-Source Log Analytics Engine", style_normal))

    # 2. Field
    story.append(Paragraph("<b>2. Field /Area of invention:</b>", style_bold_heading))
    story.append(Paragraph("Operating Systems reliability, automated fault tolerance, machine learning for system telemetry, autonomous recovery architectures, real-time log analytics, and distributed infrastructure health monitoring.", style_normal))

    # 3. Prior Art Table
    story.append(Paragraph("<b>3. Prior Patents and Publications from literature (provide a table summarizing the prior art)</b>", style_bold_heading))
    
    prior_data = [
        [Paragraph("Prior art", style_tbl_header), Paragraph("Main idea", style_tbl_header), Paragraph("Difference / gap", style_tbl_header)],
        [
            Paragraph("US9898363B2", style_tbl_cell),
            Paragraph("Automated log analysis and anomaly detection using clustering and thresholding.", style_tbl_cell),
            Paragraph("PredictiveGuard couples anomaly detection with failure type forecasting and policy-driven remediation.", style_tbl_cell),
        ],
        [
            Paragraph("US10489260B2", style_tbl_cell),
            Paragraph("Predictive failure analysis for computing systems using hardware telemetry.", style_tbl_cell),
            Paragraph("PredictiveGuard uses heterogeneous log streams (system, app, network) and rolling window feature extraction.", style_tbl_cell),
        ],
        [
            Paragraph("US20210097003A1", style_tbl_cell),
            Paragraph("Machine learning based IT operations (AIOps) incident management.", style_tbl_cell),
            Paragraph("PredictiveGuard operates on-premise in real time with dual-model ML and closed-loop self-healing without cloud reliance.", style_tbl_cell),
        ],
        [
            Paragraph("US20190347148A1", style_tbl_cell),
            Paragraph("Self-healing computer systems with static rule-based rollback.", style_tbl_cell),
            Paragraph("PredictiveGuard utilizes probabilistic confidence thresholds (>60%) with pre/post health validation.", style_tbl_cell),
        ],
    ]
    p_table = Table(prior_data, colWidths=[95, 210, 210])
    p_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 4))

    # 4. Summary and background
    story.append(Paragraph("<b>4. Summary and background of the invention</b>", style_bold_heading))
    story.append(Paragraph("PredictiveGuard is a Windows based operating system reliability application which runs continuously in the background while the system performs its normal workload. The main idea is to monitor operating system health and predict failures before they happen rather than performing reactive post-mortem crash analysis. Instead of storing raw unindexed logs, the system extracts high-dimensional temporal features such as sliding-window statistical aggregations, rate-of-change indicators, error frequencies, and critical failure keywords. This helps in studying system degradation and imminent mechanical or service slowdowns.", style_normal))
    story.append(Paragraph("The system first parses incoming log events from system, application, and network streams using the ingestion layer. Sensitive internal processes and excluded applications are skipped. Valid log events and OS metrics (CPU, RAM, Disk, and Network I/O) are converted into normalized feature vectors and used for multi-variate telemetry analysis. Transient spikes below the sliding window duration are treated as normal temporary variations.", style_normal))
    story.append(Paragraph("A personal system health baseline is calculated dynamically from multi-metric resource usage. Anomaly scores are evaluated using an Isolation Forest model and classified from LOW to CRITICAL. Concurrently, a Random Forest classifier predicts imminent failures with probabilistic confidence. When failure confidence exceeds 60%, the autonomous recovery engine executes targeted self-healing actions. The main difference from conventional monitoring tools is that predictive failure detection and recovery are performed autonomously on the local device without cloud dependency.", style_normal))

    # 5. Objectives
    story.append(Paragraph("<b>5. Objectives of Invention</b>", style_bold_heading))
    story.append(Paragraph("• To analyse system health and predict impending failures without requiring manual performance benchmarks.", style_bullet))
    story.append(Paragraph("• To use multi-source log timing and physical metric telemetry without retaining unindexed raw log dumps.", style_bullet))
    story.append(Paragraph("• To create a dynamic system health baseline and identify unusually high resource utilization patterns.", style_bullet))
    story.append(Paragraph("• To separate transient load spikes from persistent degradation and group anomaly behavior using Isolation Forest.", style_bullet))
    story.append(Paragraph("• To execute policy-driven autonomous recovery and keep all processing and telemetry storage on the local device.", style_bullet))

    # 6. Working principle
    story.append(Paragraph("<b>6. Working principle of the invention:</b>", style_bold_heading))
    story.append(Paragraph("Multi-source log event → regex parsing/normalization → sliding-window feature engineering → multi-variate feature vector → local SQLite storage → health baseline → Isolation Forest anomaly detection → Random Forest failure prediction → autonomous recovery execution → dashboard and alert report. For valid system transitions, PredictiveGuard calculates rate of change, resource velocity proxy, and error frequency. Non-critical background tasks do not trigger alerts, while recurring errors initiate autonomous recovery.", style_normal))

    # 7. Description in detail
    story.append(Paragraph("<b>7. Description of the invention in detail</b>", style_bold_heading))
    story.append(Paragraph("The prototype is implemented as a Python application with a real-time Flask web dashboard. The log event layer receives kernel, application, and network events and passes them through the normalization parser before they reach the analysis layer. The parser standardizes timestamps, log levels, and source identifiers. The application can also exclude its own processes and user-configured system services.", style_normal))
    story.append(Paragraph("The feature engineering layer works with core operating system metrics including CPU, memory, disk, and network I/O. It uses sliding windows across the last 30 metric snapshots and 100 log entries to calculate rolling mean, standard deviation, and rate of change. Frequency counts for error and warning messages are extracted alongside critical keyword presence such as out-of-memory and connection timeouts. A 28-dimensional feature vector is generated every 2 seconds.", style_normal))
    story.append(Paragraph("Transient spikes below the sliding window duration are treated as normal temporary fluctuations. This avoids treating a short load burst as an imminent system breakdown. Anomaly detection uses Isolation Forest with 0.10 contamination to identify statistical outliers and classify severity from LOW to CRITICAL. The failure predictor uses Random Forest classification across five failure types: disk failure, memory exhaustion, cpu overload, service crash, and network outage.", style_normal))
    story.append(Paragraph("The storage layer uses SQLite and stores aggregate telemetry, parsed log events, anomaly records, prediction confidence distributions, and recovery audit trails. Sensitive parameters are not exposed to external networks; processing is strictly on-premise. When failure confidence exceeds 60%, the recovery engine executes policy-mapped remediation actions such as service restarts, cache flushes, log rotations, and runaway process termination, and validates post-recovery health restoration.", style_normal))

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 2
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("Latest observed results from the running prototype: 4,128 total logs processed, 1,365 metrics snapshots, 1,321 anomalies detected, and 16 failure predictions evaluated. The autonomous recovery engine executed 25 self-healing interventions with an 88.9% post-recovery health restoration rate. Two machine learning models (Isolation Forest and Random Forest) operate concurrently.", style_normal))
    story.append(Spacer(1, 2))

    # Composite image
    comp_img_path = os.path.join("screenshots", "idf_p2_composite.png")
    if os.path.exists(comp_img_path):
        story.append(RLImage(comp_img_path, width=515, height=295))
    story.append(Spacer(1, 4))

    # 8. Experimental validation results
    story.append(Paragraph("<b>8. Experimental validation results:</b>", style_bold_heading))
    story.append(Paragraph("The final automated test run was performed using the project's Python virtual environment. The command python -m pytest tests -v was used from the PredictiveGuard project folder. The result was 52 passed in 9.90 seconds, with no failed tests.", style_normal))
    story.append(Paragraph("Manual testing was also carried out on the web application dashboard. The Dashboard, Log Viewer, Anomalies, Predictions, Recovery, Timeline, and Alert views were checked. The latest dashboard showed 4,128 logs, 1,365 metrics, 1,321 anomalies, 16 predictions, and 25 successful recoveries. The health gauge showed 91.4% system health. The Recovery view showed automated remediation actions (cache clearing, service restart, log rotation, runaway process termination).", style_normal))

    # 9. Protection aspects
    story.append(Paragraph("<b>9. What aspects of the invention needs protection?</b>", style_bold_heading))
    story.append(Paragraph("• The local method of collecting multi-source log telemetry and operating system performance metrics without cloud transmission.", style_bullet))
    story.append(Paragraph("• The dual-model machine learning architecture combining unsupervised Isolation Forest anomaly detection with supervised Random Forest failure prediction.", style_bullet))
    story.append(Paragraph("• The sliding-window feature engineering pipeline computing multi-variate rolling statistics, rate-of-change metrics, and error keyword indicators.", style_bullet))
    story.append(Paragraph("• The combination of confidence-gated failure prediction and policy-driven autonomous self-healing recovery in one local application.", style_bullet))
    story.append(Paragraph("• The local SQLite storage and real-time dashboard design retaining complete audit logs and pre/post health restoration metrics.", style_bullet))
    story.append(Spacer(1, 6))

    # Page 2 footer box
    story.append(make_header_table())

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 3
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("<b>10. What is Technology readiness level of your invention?</b>", style_bold_heading))
    story.append(Spacer(1, 8))

    style_trl_th = ParagraphStyle('TRLTH', fontName='Times-Bold', fontSize=8.5, alignment=1)
    style_trl_sub = ParagraphStyle('TRLSub', fontName='Times-Bold', fontSize=7.9, alignment=1)
    style_trl_desc = ParagraphStyle('TRLDesc', fontName='Times-Roman', fontSize=7.2, leading=8.5, alignment=1)
    style_check = ParagraphStyle('TRLCheck', fontName='Helvetica-Bold', fontSize=18, alignment=1)

    trl_headers = [
        Paragraph("<b>Research</b>", style_trl_th), "", "",
        Paragraph("<b>Development</b>", style_trl_th), "", "",
        Paragraph("<b>Deployment</b>", style_trl_th), "", ""
    ]

    trl_levels = [
        Paragraph("TRL 1", style_trl_sub), Paragraph("TRL 2", style_trl_sub), Paragraph("TRL 3", style_trl_sub),
        Paragraph("TRL 4", style_trl_sub), Paragraph("TRL 5", style_trl_sub), Paragraph("TRL 6", style_trl_sub),
        Paragraph("TRL 7", style_trl_sub), Paragraph("TRL 8", style_trl_sub), Paragraph("TRL 9", style_trl_sub),
    ]

    trl_descriptions = [
        Paragraph("Basic Principles observed", style_trl_desc),
        Paragraph("Technology concept formulated", style_trl_desc),
        Paragraph("Experimental proof of concept", style_trl_desc),
        Paragraph("Technology validated in a lab", style_trl_desc),
        Paragraph("Technology validated in a relevant environment (industrially relevant in case of key enabling technologies)", style_trl_desc),
        Paragraph("Technology demonstrated in a relevant environment (industrially relevant in case of key enabling technologies)", style_trl_desc),
        Paragraph("System prototype demonstration in an operational environment", style_trl_desc),
        Paragraph("System complete and qualified", style_trl_desc),
        Paragraph("Actual system proven in an operational environment (competitive manufacturing in case of key enabling technologies, or in space)", style_trl_desc),
    ]

    trl_checks = ["", "", "", "", "", Paragraph("✓", style_check), "", "", ""]

    col_w = 515 / 9
    trl_data = [
        trl_headers,
        trl_levels,
        trl_descriptions,
        trl_checks
    ]

    trl_table = Table(trl_data, colWidths=[col_w]*9)
    trl_table.setStyle(TableStyle([
        ('SPAN', (0,0), (2,0)),
        ('SPAN', (3,0), (5,0)),
        ('SPAN', (6,0), (8,0)),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))

    story.append(trl_table)
    story.append(Spacer(1, 40))

    footer_end = Paragraph(
        "----------------------END OF THE DOCUMENT-----------------------------",
        ParagraphStyle('EndDoc', fontName='Times-Roman', fontSize=8, alignment=1, textColor=colors.black)
    )
    story.append(footer_end)

    doc.build(story)
    print(f"Generated {pdf_filename} successfully.")

if __name__ == "__main__":
    generate_idf_pdf()
