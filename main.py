from requests_html import HTMLSession
import os
import re
import time

# first_delimiter = "mailto:"
symbol_string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@."

def get_csvlist(__fullpath):
    try:
        with open(__fullpath, "r+", encoding='iso-8859-1') as __f:
            __list = list(__f)
            __f.close()
            __converted_list = [i.strip() for i in __list]
            print('[+] INFO: total config lines:', len(__converted_list))
            return __converted_list
    except FileNotFoundError:
        print("[+] ERROR: file not found", __fullpath)
        return []

def parse(__string, __first_str_delimiter, __alphabet_string):
    start_index = __string.find(__first_str_delimiter)

    if start_index != -1:
        for end_index in range(start_index + len(__first_str_delimiter), start_index + len(__first_str_delimiter) + 40):
            if end_index < len(__string):
                if __string[end_index] not in __alphabet_string:
                    return __string[start_index + len(__first_str_delimiter):end_index]
            else:
                break
        # If the loop completes without finding the second delimiter, return an empty string
    return ""

def extract_emails(input_string):
    # Define the regular expression pattern for matching email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Use re.findall to extract all email addresses from the input_string
    emails = re.findall(email_pattern, input_string)

    # If no emails are found, return an empty list
    return emails if emails else []

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
            site = website_data
            retry = 0
            email_match = []
            scrape_mode = 0
            while True:
                if(retry > 3):
                    break
                try:
                    if(scrape_mode == 0):
                        print(f"{current_line}/{total_lines} - Visiting Website:", website_data)
                        r = session.get(website_data)
                        r.html.render(sleep=2, timeout=10)                    # Get the HTML source after JavaScript rendering
                        html_source = r.html.html     
                        # Extract email
                        email_match = extract_emails(html_source)
                        # email_match = parse(html_source, 'mailto:', '"')
                        if not email_match == []:
                            break
                        else:
                            scrape_mode = 1

                    if(scrape_mode == 1):
                        website_data = website_data + "/contact"
                        print(f"{current_line}/{total_lines} - Visiting Website:", website_data)
                        r = session.get(website_data)
                        r.html.render(sleep=2, timeout=10)                    # Get the HTML source after JavaScript rendering
                        html_source = r.html.html     
                        # Extract email
                        email_match = extract_emails(html_source)
                        if not email_match == []:
                            break
                        else:
                            scrape_mode = 0
                            break

                except Exception as e:
                    retry += 1
                    time.sleep(1)
                    print(f"exception... in {website_data} skipped!")

            emails_address = email_match
            if not emails_address == []:
                print("Extracted Email Address:", emails_address)

                email_count = 0
                email_csv_string = ""

                for email in emails_address:
                    if(email_count == 0):
                        email_csv_string = email + ","
                    else:
                        email_csv_string = email_csv_string + email + ","
                    email_count+=1

                save_data(company_data, site, email_csv_string)
            else:
                print("No email address found.")
                save_data(company_data, site, "No email found")
        else:
            print(f"{current_line}/{total_lines} - Visiting Website:", "not found!")
            save_data(company_data, site, "No email found")

# Close the session
session.close()
