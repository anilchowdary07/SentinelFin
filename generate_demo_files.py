import csv
import os

out_dir = "/Users/anilchowdary/Documents/ui_path_agent_hackathon/demo_documents/massive_dataset"

# 1. Generate a CSV file (NICE Actimize SAM Export)
csv_path = os.path.join(out_dir, "Actimize_Alert_Export_2023.csv")
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["TransactionID", "Date", "Originator", "Beneficiary", "Amount", "Currency", "Alert_Type", "Risk_Score"])
    writer.writerow(["TXN-998811", "2023-10-25T10:00:00Z", "Global Trade Corp", "Shell Co Holdings", "50000.00", "USD", "SUSPECTED_LAYERING", "85"])
    writer.writerow(["TXN-998812", "2023-10-25T11:30:00Z", "Shell Co Holdings", "Offshore Trust LLC", "49500.00", "USD", "SUSPECTED_LAYERING", "90"])
    writer.writerow(["TXN-998813", "2023-10-26T09:15:00Z", "Global Trade Corp", "Phantom Logistics", "75000.00", "USD", "HIGH_VELOCITY", "78"])

# 2. Generate a SWIFT MT103 file
swift_path = os.path.join(out_dir, "SWIFT_MT103_Wire_Transfer.txt")
with open(swift_path, 'w') as f:
    f.write("{1:F01BANKDEF0AXXX0000000000}{2:I103BANKXYZ0XXXXN}{4:\n")
    f.write(":20:TXN-998811\n")
    f.write(":32A:231025USD50000,\n")
    f.write(":50K:/123456789\nGlobal Trade Corp\n123 Business Ave\nNew York, NY 10001\n")
    f.write(":59:/987654321\nShell Co Holdings\nPO Box 1234\nGrand Cayman, KY1-1102\n")
    f.write(":70:Invoice Payment for Consulting Services\n")
    f.write("-}\n")

print("Successfully generated CSV and SWIFT files in massive_dataset!")
