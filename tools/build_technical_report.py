"""Rebuild submission/Technical_Report.pdf. Requires reportlab."""
from pathlib import Path
import html
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'submission/Technical_Report.pdf'

def markup(text):
    text = html.escape(text.replace('**', '').replace('`', ''))
    for old,new in [('×',' x '),('−','-'),('–','-'),('—','-'),('→',' to '),('²','2'),('…','...')]:
        text = text.replace(old,new)
    # Keep readable link labels; the README supplies relative-file navigation.
    return re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',text)

def main():
    styles=getSampleStyleSheet()
    styles['Title'].fontName='Times-Roman'
    styles['Title'].textColor=HexColor('#33745b')
    styles['Heading1'].fontSize=18
    styles['Heading1'].leading=23
    styles['Heading1'].textColor=HexColor('#33745b')
    styles['Heading2'].fontSize=12
    styles['Heading2'].leading=17
    styles['BodyText'].fontSize=9.2
    styles['BodyText'].leading=12.3
    styles['BodyText'].spaceAfter=6
    story=[Paragraph('Aegis REBOUND',styles['Title']),Paragraph('Recovery-aware respiratory digital twin',styles['Heading1']),Paragraph('Algorithm, data and reproducible evidence',styles['Heading2']),Spacer(1,20),Paragraph('Team Aegis: Abhishek Bharathi and Aadithya Ram<br/>Amrita Vishwa Vidyapeetham, Coimbatore<br/>Independent student team; no incubator affiliation',styles['BodyText']),Spacer(1,20),Paragraph('Digital Twin Challenge 2026<br/>https://github.com/B-Sheikh/Aegis-REBOUND',styles['BodyText']),Spacer(1,20),Paragraph('A working synthetic proof of concept combining personal historical records, sequential state estimation, competing explanations and budgeted observation selection.',styles['BodyText'])]
    story.append(PageBreak())
    for name in ['docs/ALGORITHM.md','docs/MODEL_DATA_CARD.md','docs/PRIOR_ART.md','docs/RESULTS.md','submission/DELIVERABLES.md']:
        story.append(Spacer(1,10))
        for block in (ROOT/name).read_text(encoding='utf-8').split('\n\n'):
            block=block.strip()
            if not block: continue
            if block.startswith('# '): story.append(Paragraph(markup(block[2:]),styles['Heading1']))
            elif block.startswith('## '): story.append(Paragraph(markup(block[3:]),styles['Heading2']))
            else: story.append(Paragraph(markup(block).replace('\n','<br/>'),styles['BodyText']))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(HexColor('#768470'))
        canvas.drawString(45,25,'Aegis REBOUND | Synthetic research prototype')
        canvas.drawRightString(550,25,str(doc.page))
    SimpleDocTemplate(str(OUTPUT),pagesize=(595,842),leftMargin=45,rightMargin=45,topMargin=43,bottomMargin=45,title='Aegis REBOUND - Technical Report',author='Team Aegis: Abhishek Bharathi and Aadithya Ram').build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUTPUT)
if __name__=='__main__':
    main()
