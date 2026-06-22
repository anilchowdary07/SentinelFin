import os
import random
import string
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

def random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_normal_transactions(num_txns, start_date):
    txns = []
    current_date = start_date
    for _ in range(num_txns):
        # Move forward a few hours
        current_date += timedelta(hours=random.randint(1, 12))
        ref = f"TXN-{random.randint(100000, 999999)}"
        txn_type = random.choice(["WIRE_IN", "WIRE_OUT", "ACH_CREDIT", "ACH_DEBIT"])
        sender = f"Corp {random_string(4)}" if "IN" in txn_type or "CREDIT" in txn_type else "Client"
        receiver = "Client" if "IN" in txn_type or "CREDIT" in txn_type else f"Vendor {random_string(4)}"
        amount = f"${random.randint(100, 15000):,}.00"
        txns.append([current_date.strftime("%Y-%m-%d"), ref, txn_type, sender, receiver, amount])
    return txns

def create_massive_bank_statements(num_docs=15, pages_per_doc=15):
    out_dir = "demo_documents/massive_dataset"
    os.makedirs(out_dir, exist_ok=True)
    
    styles = getSampleStyleSheet()
    
    # The malicious transactions to hide in the haystack
    malicious = [
        ["2026-06-10", "TXN-201", "WIRE_IN", "Unknown Entity A", "ACC-554433", "$250,000"],
        ["2026-06-11", "TXN-202", "WIRE_OUT", "ACC-554433", "Shell Corp B", "$120,000"],
        ["2026-06-11", "TXN-203", "WIRE_OUT", "ACC-554433", "Holdings C", "$115,000"],
        ["2026-06-12", "TXN-204", "WIRE_OUT", "Shell Corp B", "Final Dest D", "$115,000"],
    ]

    malicious_inserted = 0

    for doc_idx in range(1, num_docs + 1):
        filename = os.path.join(out_dir, f"Corporate_Statement_Vol_{doc_idx:02d}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        title_style = styles['Heading1']
        title_style.alignment = 1
        story.append(Paragraph(f"<b>GLOBAL CORPORATE BANK - VOLUME {doc_idx:02d}</b>", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>COMPREHENSIVE TRANSACTION LEDGER</b>", styles['Heading2']))
        story.append(Spacer(1, 20))

        start_date = datetime(2026, 6, 1) + timedelta(days=doc_idx)
        
        for page in range(1, pages_per_doc + 1):
            story.append(Paragraph(f"<b>PAGE {page} - DAILY CLEARING DATA</b>", styles['Heading3']))
            story.append(Spacer(1, 10))
            
            # Generate ~35 normal transactions per page
            table_data = [["Date", "Ref", "Type", "Sender", "Receiver", "Amount USD"]]
            txns = generate_normal_transactions(35, start_date)
            
            # Randomly inject a malicious transaction here and there to make it a real "needle in a haystack"
            if malicious_inserted < len(malicious) and random.random() > 0.7:
                insert_pos = random.randint(0, len(txns))
                txns.insert(insert_pos, malicious[malicious_inserted])
                malicious_inserted += 1
            # If we are on the very last doc and last page, inject any remaining malicious txns
            elif doc_idx == num_docs and page == pages_per_doc and malicious_inserted < len(malicious):
                while malicious_inserted < len(malicious):
                    txns.append(malicious[malicious_inserted])
                    malicious_inserted += 1

            table_data.extend(txns)

            t2 = Table(table_data, colWidths=[70, 70, 70, 100, 100, 80])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0072FF")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t2)
            
            if page < pages_per_doc:
                story.append(PageBreak())

        doc.build(story)
        print(f"Generated {filename} ({pages_per_doc} pages)")

if __name__ == '__main__':
    create_massive_bank_statements()
