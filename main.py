from requests_html import HTMLSession
import os
import re
import time

def get_csvlist(__fullpath):
    try:
        with open(__fullpath, "r+", encoding='iso-8859-1') as __f:
            __list = list(__f)
            __f.close()
            __converted_list = [i.strip() for i in __list]
            print('[+] INFO: total lines:', len(__converted_list))
            return __converted_list
    except FileNotFoundError:
        print("[+] ERROR: file not found", __fullpath)
        return []

def parse(__string, __first_str_delimiter, __second_str_delimiter):
    start_index = __string.find(__first_str_delimiter)
    end_index = __string.find(__second_str_delimiter, start_index)
    
    if start_index != -1 and end_index != -1:
        return __string[start_index + len(__first_str_delimiter):end_index]
    else:
        return ""

def save_data(company, website, email):
    global output_name
    # Output file path
    output_file_path = output_name

    # Check if the file exists
    file_exists = os.path.isfile(output_file_path)

    # Open the output CSV file in append mode, create it if it doesn't exist
    with open(output_file_path, 'a', newline='', encoding='utf-8') as output_file:
        # If the file doesn't exist, write the header
        if not file_exists:
            output_file.write('Company,Website,Email\n')

        # Write the data to the output CSV file
        output_file.write(f"{company},{website},{email}\n")

        # Print the added data
        print(f"Adding to {output_name}: {company}, {website}, {email}")

__listlist = []
binary_location_path=""
output_name = ""
__list = get_csvlist("config.txt")

for __i in range(0, len(__list)):
    __split = __list[__i].split("=")
    __listlist.append(__split)

for __i in range(0, len(__listlist)):
    if __listlist[__i][0] == "filename":
        file_path = __listlist[__i][1]
    if __listlist[__i][0] == "output_name":
        output_name = __listlist[__i][1]

session = HTMLSession()

# Open the CSV file
with open(file_path, 'r', encoding='utf-8') as file:
    # Skip the header
    header = next(file)

    # Get the total number of lines in the file
    total_lines = sum(1 for _ in file)

    # Return to the beginning of the file
    file.seek(0)

    # Skip the header again
    next(file)

    # Iterate over each line in the CSV file
    for current_line, line in enumerate(file, start=1):
        # Split the line into columns
        columns = line.strip().split(',')

        company_data = columns[0].strip('"')
        website_data = columns[1].strip('"')
        site = ""

        if not (website_data == ""):
            # Print the status and website data
            print(f"{current_line}/{total_lines} - Visiting Website:", website_data)

            site = website_data
            retry = 0
            email_match = ""
            
            while retry < 3:
                try:
                    if retry >= 3:
                        break

                    # Open the URL
                    r = session.get(website_data)
                    r.html.render(sleep=2, timeout=10)

                    # Get the HTML source after JavaScript rendering
                    html_source = r.html.html

                    # Extract email
                    email_match = parse(html_source, 'mailto:', '"')

                    if '@' in email_match:
                        if len(email_match) >= 30:
                            email_match = parse(html_source, 'mailto:', '?')

                            if '@' in email_match and len(email_match) >= 30:
                                email_match = "No email found"
                        break
                    else:
                        retry += 1
                        time.sleep(1)
                        if retry == 1:
                            website_data = website_data + "/contact"

                except Exception as e:
                    retry += 1
                    time.sleep(1)
                    print("trying...")
                    if retry == 1:
                        website_data = website_data + "/contact"
                    pass

            email_address = email_match
            if email_address:
                print("Extracted Email Address:", email_address)
                save_data(company_data, site, email_address)
            else:
                print("No email address found.")
                save_data(company_data, site, "No email found")
        else:
            print(f"{current_line}/{total_lines} - Visiting Website:", "not found!")
            save_data(company_data, site, "No email found")

# Close the session
session.close()
