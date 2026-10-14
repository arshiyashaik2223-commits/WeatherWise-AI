"""JSON/PDF report generation from current dataset analysis."""
import json
from io import BytesIO
from .weather_analysis import summarize_dataset
from .trust_score import calculate_trust_score
from .anomaly_detection import detect_anomalies

def build_json_summary(df):
    summary=summarize_dataset(df); summary["trust_score"]=calculate_trust_score(df)
    summary["limitations"]=["Analysis describes uploaded historical data only.","Anomaly flags are statistical review candidates, not confirmed errors."]
    return json.dumps(summary,indent=2,default=str).encode("utf-8")

def build_pdf_report(df, anomalies=None):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as exc: raise RuntimeError("Install reportlab to generate PDF reports.") from exc
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=letter); styles=getSampleStyleSheet(); story=[]
    summary=summarize_dataset(df); trust=calculate_trust_score(df)
    story += [Paragraph("WeatherWise AI — Dataset Analysis Report",styles["Title"]),Paragraph("Generated from the currently selected dataset; historical analysis only.",styles["BodyText"]),Spacer(1,12)]
    story.append(Paragraph(f"Rows: {len(df)} | Columns: {len(df.columns)} | Trust Score: {trust['score']}/100",styles["Heading2"]))
    story.append(Paragraph(f"Columns: {', '.join(map(str,df.columns))}",styles["BodyText"])); story.append(Spacer(1,10))
    story.append(Paragraph("Numeric summary",styles["Heading2"]))
    data=[["Column","Count","Mean","Median","Minimum","Maximum"]]
    for col,s in summary["numeric_stats"].items(): data.append([col,str(s["count"]),f"{s['mean']:.4g}",f"{s['median']:.4g}",f"{s['min']:.4g}",f"{s['max']:.4g}"])
    table=Table(data,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dceef2")),("GRID",(0,0),(-1,-1),.4,colors.grey),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")])); story.append(table)
    story += [Spacer(1,10),Paragraph("Data quality",styles["Heading2"]),Paragraph(f"Completeness: {trust['completeness_pct']}%; missing cells: {trust['missing_cells']}; duplicate rows: {trust['duplicate_rows']}; invalid date values: {trust['invalid_date_values']}.",styles["BodyText"]),Paragraph("Trust formula: "+trust["formula"],styles["BodyText"]),Spacer(1,8),Paragraph("Limitations and recommendations",styles["Heading2"])]
    for item in trust["recommendations"]: story.append(Paragraph("• "+item,styles["BodyText"]))
    story.append(Paragraph("Statistical anomalies require human review and are not necessarily errors. This report does not forecast future weather.",styles["BodyText"]))
    doc.build(story); return buf.getvalue()
