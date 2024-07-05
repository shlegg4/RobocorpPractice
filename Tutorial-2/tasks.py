from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    open_robot_order_website()
    order_table = get_orders()
    for row in order_table:
        close_annoying_modal()
        fill_form(row=row)
        preview_robot()
        while True:
            
            order()
            if check_for_error() == False:
                pdf_path = store_receipt_as_pdf(row['Order number'])
                screenshot_path = screenshot_robot(row['Order number'])
                print(screenshot_path)
                embed_screenshot_to_receipt(screenshot=screenshot_path, pdf_file=pdf_path)
                break
            print(row)
        order_another_robot()

def open_robot_order_website():
    page = browser.page()
    page.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    HTTP().download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    return Tables().read_table_from_csv("orders.csv", header=True)

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_form(row):
    page = browser.page()
    page.select_option("#head", row["Head"])
    page.click(f"#id-body-{row['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", row["Legs"])
    page.fill("#address", row["Address"])

def preview_robot():
    page = browser.page()
    page.click("#preview")

def order():
    page = browser.page()
    page.click("#order")

def check_for_error():
    page = browser.page()
    print("Check for error")
    try:
        page.get_attribute("#receipt", name="id", timeout=1000)
        return False
    except:
        return False


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    path = f"./outputs/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, path)
    return path

def screenshot_robot(order_number):
    page = browser.page()
    path = f"./outputs/image-{order_number}.png"
    page.screenshot(path=path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    print(f"{screenshot, pdf_file}")
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file)

def order_another_robot():
    page = browser.page()
    page.click("#order-another")