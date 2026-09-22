import io
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from app.models.user import User
from app.services.progress_engine import ProgressEngine
from app.services.ai_service import AIService

class PDFReportGenerator:
    """
    Gerador de Relatórios Acadêmicos Semanais em PDF usando Python e ReportLab.
    Gera um relatório profissional com métricas, tabelas de desempenho e insights de IA.
    """

    @classmethod
    def generate_weekly_report(cls, db: Session, user: User) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Estilos Customizados
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=15
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        badge_style = ParagraphStyle(
            'BadgeText',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e40af"),
            fontName="Helvetica-Bold"
        )

        story = []

        # 1. Cabeçalho
        story.append(Paragraph("EduTrack AI — Relatório Semanal de Desempenho", title_style))
        now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y às %H:%M UTC")
        story.append(Paragraph(f"<b>Estudante:</b> {user.name} ({user.email}) &nbsp;|&nbsp; <b>Data de Emissão:</b> {now_str}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

        # Obter Dados
        metrics = ProgressEngine.calculate_overall_metrics(db, user.id)
        insights = AIService.generate_insights(db, user.id)

        # 2. Resumo Executivo (KPIs em Tabela com Estilo)
        story.append(Paragraph("1. Resumo Executivo e KPIs Globais", section_heading))
        
        kpi_data = [
            [
                Paragraph("<b>Progresso Ponderado:</b>", body_style),
                Paragraph(f"<font color='#2563eb'><b>{metrics.overall_weighted_progress:.1f}%</b></font>", body_style),
                Paragraph("<b>Tempo Total Estudado:</b>", body_style),
                Paragraph(f"<b>{metrics.total_study_time_hours:.1f} horas</b>", body_style)
            ],
            [
                Paragraph("<b>Tarefas Concluídas:</b>", body_style),
                Paragraph(f"<b>{metrics.completed_tasks} / {metrics.total_tasks}</b>", body_style),
                Paragraph("<b>Tempo Estimado Restante:</b>", body_style),
                Paragraph(f"<b>{metrics.estimated_remaining_hours:.1f} horas</b>", body_style)
            ],
            [
                Paragraph("<b>Velocidade de Estudo:</b>", body_style),
                Paragraph(f"<b>{metrics.study_velocity_tasks_per_week:.1f} tarefas/sem</b>", body_style),
                Paragraph("<b>Previsão de Conclusão:</b>", body_style),
                Paragraph(f"<b>{metrics.estimated_completion_date or 'N/A'}</b>", body_style)
            ]
        ]

        kpi_table = Table(kpi_data, colWidths=[130, 130, 140, 140])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 15))

        # 3. Tabela de Desempenho por Disciplina
        story.append(Paragraph("2. Detalhamento de Disciplinas e Desvios de Tempo", section_heading))

        table_header = [
            Paragraph("<b>Disciplina</b>", badge_style),
            Paragraph("<b>Carga</b>", badge_style),
            Paragraph("<b>Tarefas</b>", badge_style),
            Paragraph("<b>Progresso</b>", badge_style),
            Paragraph("<b>Previsto</b>", badge_style),
            Paragraph("<b>Real</b>", badge_style),
            Paragraph("<b>Desvio</b>", badge_style)
        ]
        
        table_rows = [table_header]
        for s in metrics.subjects_breakdown:
            dev_color = "#dc2626" if s.time_deviation_percentage > 20 else ("#16a34a" if s.time_deviation_percentage < 0 else "#2563eb")
            dev_str = f"<font color='{dev_color}'><b>{s.time_deviation_percentage:+.0f}%</b></font>" if s.total_estimated_minutes > 0 else "0%"
            
            table_rows.append([
                Paragraph(f"<b>{s.subject_name}</b>", body_style),
                Paragraph(f"{s.workload_hours:.0f}h", body_style),
                Paragraph(f"{s.completed_tasks}/{s.total_tasks}", body_style),
                Paragraph(f"<b>{s.progress_percentage:.0f}%</b>", body_style),
                Paragraph(f"{s.total_estimated_minutes/60:.1f}h", body_style),
                Paragraph(f"{s.total_actual_minutes/60:.1f}h", body_style),
                Paragraph(dev_str, body_style)
            ])

        if len(table_rows) == 1:
            table_rows.append([Paragraph("Nenhuma disciplina cadastrada ainda.", body_style)] * 7)

        subj_table = Table(table_rows, colWidths=[150, 45, 55, 65, 55, 55, 65])
        subj_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(subj_table)
        story.append(Spacer(1, 15))

        # 4. Diagnóstico e Recomendações de IA
        story.append(Paragraph(f"3. Insights e Recomendações ({insights.generated_by})", section_heading))
        story.append(Paragraph(f"<i>{insights.summary}</i>", body_style))
        story.append(Spacer(1, 8))

        if insights.critical_alerts:
            story.append(Paragraph("<b>Alertas Críticos:</b>", ParagraphStyle('AlertTitle', parent=body_style, textColor=colors.HexColor("#b91c1c"), fontName="Helvetica-Bold")))
            for alert in insights.critical_alerts:
                story.append(Paragraph(f"• <font color='#b91c1c'>{alert}</font>", body_style))
            story.append(Spacer(1, 6))

        if insights.recommendations:
            story.append(Paragraph("<b>Recomendações Práticas:</b>", ParagraphStyle('RecTitle', parent=body_style, fontName="Helvetica-Bold")))
            for rec in insights.recommendations[:4]:
                story.append(Paragraph(f"• <b>{rec.title}:</b> {rec.message}", body_style))
                if rec.action_suggested:
                    story.append(Paragraph(f"&nbsp;&nbsp;<i>Sugestão: {rec.action_suggested}</i>", ParagraphStyle('Sug', parent=body_style, textColor=colors.HexColor("#475569"))))
                story.append(Spacer(1, 4))

        if insights.weekly_focus:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Foco Recomendado para a Próxima Semana:</b>", ParagraphStyle('FocTitle', parent=body_style, fontName="Helvetica-Bold")))
            for f in insights.weekly_focus:
                story.append(Paragraph(f"• {f}", body_style))

        # Rodapé com nota OpenSpec
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
        story.append(Paragraph("EduTrack AI — Desenvolvido com metodologia Spec-Driven Development (OpenSpec) | Python + FastAPI + Xano Engine", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#94a3b8"), alignment=1)))

        doc.build(story)
        buffer.seek(0)
        return buffer
