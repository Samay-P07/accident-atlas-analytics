import os
import base64
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions

def print_to_pdf():
    options = EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Edge(options=options)
    html_path = os.path.abspath("presentation_defense_script.html")
    driver.get(f"file:///{html_path.replace('\\', '/')}")
    
    # Execute Edge PDF printing command
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True
    }
    
    # Chrome DevTools Protocol command to print to PDF
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    pdf_bytes = base64.b64decode(result['data'])
    
    output_pdf = "German_Accident_Data_Explorer_Oral_Defense_Script.pdf"
    with open(output_pdf, "wb") as f:
        f.write(pdf_bytes)
        
    driver.quit()
    print(f"[SUCCESS] PDF Saved successfully to {output_pdf}")

if __name__ == "__main__":
    print_to_pdf()
