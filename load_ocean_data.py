import re

# Use your exact file path
sql_file_path = r"C:\Users\Diya Ghorpade\Downloads\backup.sql"
csv_file_path = r"E:\Mini Project\copernicus_data.csv"

print(f"Reading from: {sql_file_path}")

try:
    # Read the SQL file
    with open(sql_file_path, 'r', encoding='utf-16') as f:
        content = f.read()
    
    print("File read successfully!")
    
    # Find the COPY data section
    copy_start = content.find('COPY public.copernicus_data')
    if copy_start == -1:
        print("ERROR: Could not find COPY statement in the file")
        exit()
        
    data_start = content.find('FROM stdin;', copy_start)
    if data_start == -1:
        print("ERROR: Could not find 'FROM stdin;' in the file")
        exit()
        
    data_start += len('FROM stdin;')
    data_end = content.find('\\.', data_start)
    
    if data_end == -1:
        print("ERROR: Could not find the end of data ('\\.')")
        exit()

    # Extract the data lines
    data_section = content[data_start:data_end].strip()
    print(f"Found {len(data_section.splitlines())} data lines")
    
    # Write to CSV
    with open(csv_file_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write('id,time,latitude,longitude,depth,so,thetao,uo,vo\n')
        
        # Process each line
        for line_num, line in enumerate(data_section.split('\n'), 1):
            line = line.strip()
            if line:
                # Replace tabs with commas and fix any issues
                line = re.sub(r'\t+', ',', line)
                f.write(line + '\n')
                
                # Progress indicator for large files
                if line_num % 10000 == 0:
                    print(f"Processed {line_num} lines...")
    
    print(f"CSV file created: {csv_file_path}")
    print(f"Total lines processed: {len(data_section.splitlines())}")

except FileNotFoundError:
    print(f"ERROR: File not found at {sql_file_path}")
    print("Please check the file path and try again")
except Exception as e:
    print(f"ERROR: {e}")