from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import base64
import os
import time
import re 
import fitz

# Set directories for PDF and text files
pdf_folder = r"C:\Users\Liam\Downloads\383-400-20240112T204202Z-001\Test\Booktoki Raws\RAGS\PDF"
txt_folder = r"C:\Users\Liam\Downloads\383-400-20240112T204202Z-001\Test\Booktoki Raws\RAGS"
profile_directory = 'Default'

# Ensure the directories exist
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(txt_folder, exist_ok=True)

# Setup Chrome options
edge_options = EdgeOptions()
edge_options.use_chromium = True  # Tell WebDriver to use Chromium backend
edge_options.add_experimental_option("prefs", {
    "printing.print_preview_sticky_settings.appState": '{"recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}], "selectedDestinationId": "Save as PDF", "version": 2}',
    "savefile.default_directory": pdf_folder  # Set directory for saving PDFs
})
edge_options.add_argument(f"profile-directory={profile_directory}")
user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data')  # Update for Edge
edge_options.add_argument(f"user-data-dir={user_data_dir}")
edge_options.add_argument('--no-sandbox')  # Adding this to see if it helps
edge_options.add_argument('--disable-dev-shm-usage')  # Avoid shared memory issues
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--remote-debugging-port=9222")
edge_options.add_argument('--no-first-run')
edge_options.add_argument('--no-default-browser-check')

# Initialize Edge WebDriver
edge_service = Service(executable_path=r'C:\Users\Liam\Downloads\edgedriver\msedgedriver.exe')
driver = webdriver.Edge(service=edge_service, options=edge_options)

pattern_str = r'\b[0-9a-fA-F]+(?:[0-9a-fA-F]{2})+\b\s*'

# Function to save the current chapter
def save_current_chapter(chapter_number):
    # Create specific directory for the chapter
    chapter_dir = os.path.join(txt_folder, f"{chapter_number}")
    original_txt_dir = os.path.join(chapter_dir, "Original Txt Files")
    os.makedirs(chapter_dir, exist_ok=True)
    os.makedirs(original_txt_dir, exist_ok=True)

    # Adjust file paths for each chapter
    pdf_path = os.path.join(original_txt_dir, f"original_chapter_{chapter_number}.pdf")
    original_txt_path = os.path.join(original_txt_dir, f"original_chapter_{chapter_number}.txt")
    cleaned_txt_path = os.path.join(chapter_dir, f"chapter_{chapter_number}.txt")

    # Then, when cleaning the content:

    result = driver.execute_cdp_cmd("Page.printToPDF", {
    "landscape": False,
    "printBackground": True,
    "preferCSSPageSize": True,
    })

    # Save the PDF
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(result['data']))

    # Open the PDF and extract text
    doc = fitz.open(pdf_path)
    content = ""  # Initialize content variable
    for page in doc:
        content += page.get_text()
    doc.close()

    # Save the original, unedited text
    with open(original_txt_path, 'w', encoding='utf-8') as file:
        file.write(content)

    # Compile the pattern with additional matching for trailing whitespace/newlines
    pattern = re.compile(pattern_str + r'\s*', re.MULTILINE)

    # Clean the content
    cleaned_content = re.sub(pattern, '', content)

    # Save the cleaned content
    with open(cleaned_txt_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

    print(f"Original and cleaned versions of Chapter {chapter_number} saved.")

# Main loop for chapters
    
driver.get(f"https://page.kakao.com/content/57948732/viewer/63553247")

time.sleep(90)  # Wait for the page to load

body_element = driver.find_element(By.TAG_NAME, 'body')
ActionChains(driver).move_to_element(body_element).click().perform()

try:
# Adjusted XPath to target the image within the list item with alt text "페이지"
    page_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//li[contains(@class,"jsx-2531468679 jsx-3187517800 list-child-item")]//img[@alt="스크롤"]'))
    )
    page_button.click()
except TimeoutException:
    print('The format button was not found or not clickable.')

for chapter_number in range(839, 865):  # Example: Save chapters 1 through 5
      # Adjust URL for each chapter
    time.sleep(10)
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.flex.cursor-pointer.flex-row.items-center.justify-center'))
        )
        next_button.click()
    except TimeoutException:
        print('The down button was not found or not clickable.')
    driver.execute_script("""
    var closeButton = document.querySelector('img[alt="닫기"]');
    if (closeButton) {
        closeButton.closest('div.fixed').remove();
    }
    """)
    # Remove the '이펍 설정' button container element
    driver.execute_script("""
    var epubButton = document.querySelector('img[alt="이펍 설정"]');
    if (epubButton) {
        epubButton.closest('div.fixed').remove();
    }
    """)
    # Remove the '상단으로' button container element, if it's separate or needs specific targeting
    driver.execute_script("""
    var topButton = document.querySelector('img[alt="상단으로"]');
    if (topButton) {
        topButton.closest('div.fixed').remove();
    }
    """)
    body_element = driver.find_element(By.TAG_NAME, 'body')
    ActionChains(driver).move_to_element(body_element).click().perform()
    time.sleep(10)
    driver.execute_script("""
    var element = document.querySelector('div.relative.flex.w-full.cursor-pointer.flex-row.items-center.bg-bg-a-10');
    if (element) {
        element.parentNode.removeChild(element);
    }
    """)
    driver.execute_script("""
    var element = document.querySelector('div.flex.cursor-pointer.flex-row.items-center.justify-center');
    if (element) {
        element.parentNode.removeChild(element);
    }
    """)
    ActionChains(driver).move_to_element(body_element).click().perform()
    time.sleep(5)
    save_current_chapter(chapter_number)
    # Click the "next chapter" button, if present
    try:
        body_element = driver.find_element(By.TAG_NAME, 'body')
        ActionChains(driver).move_to_element(body_element).click().perform()
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'flex cursor-pointer flex-row items-center') and .//img[@alt='다음']]"))
        )
        next_button.click()
        time.sleep(5)  # Wait for next chapter to load
    except TimeoutException:
        print(f"No next button found or clickable for chapter {chapter_number}. Ending the loop.")
        break

driver.quit()
