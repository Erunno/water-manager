import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io
import math
import os
import tempfile

# Constants (you can adjust these later)
QR_CODE_SIZE = 35 * mm  # Width and height of the QR code
LABEL_HEIGHT = 10 * mm  # Height of the label area
ITEM_HEIGHT = QR_CODE_SIZE + LABEL_HEIGHT  # Total height of each QR code + label
ITEM_WIDTH = QR_CODE_SIZE  # Width of each QR code + label
MARGIN = 15 * mm  # Margin around the edges of the page
SPACING = 0 * mm  # Spacing between QR codes
FONT_SIZE = 30  # Font size for labels

# Register a font that supports Czech characters
try:
    # Try several fonts that might exist on the system
    font_found = False
    
    # Windows common fonts that support Czech characters
    possible_fonts = [
        ('Calibri', 'c:/windows/fonts/calibri.ttf'),
        ('Arial', 'c:/windows/fonts/arial.ttf'),
        ('Segoe UI', 'c:/windows/fonts/segoeui.ttf'),
        ('Times New Roman', 'c:/windows/fonts/times.ttf'),
    ]
    
    for font_name, font_path in possible_fonts:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            print(f"Using font: {font_name}")
            font_found = True
            FONT_NAME = font_name
            break
    
    if not font_found:
        print("Warning: No font with Czech character support found. Using default font.")
        FONT_NAME = "Helvetica"
except Exception as e:
    print(f"Warning: Error registering font: {e}. Using default font.")
    FONT_NAME = "Helvetica"

def generate_qr_codes_pdf(names, output_filename="qr_codes.pdf"):
    # Create a new PDF with A4 size
    c = canvas.Canvas(output_filename, pagesize=A4)
    width, height = A4
    
    # Calculate how many QR codes can fit on a page
    usable_width = width - 2 * MARGIN
    usable_height = height - 2 * MARGIN
    
    cols = math.floor(usable_width / (ITEM_WIDTH + SPACING))
    rows = math.floor(usable_height / (ITEM_HEIGHT + SPACING))
    
    # Print some info
    print(f"Page size: {width/mm:.1f}mm x {height/mm:.1f}mm")
    print(f"Grid: {cols} columns x {rows} rows")
    print(f"Total QR codes per page: {cols * rows}")
    
    # Create temporary directory for QR code images
    temp_dir = tempfile.mkdtemp()
    temp_files = []
    
    try:
        # Initialize counters
        current_page = 1
        qr_count = 0
        
        # Process each name
        for name in names:
            # Calculate position for this QR code
            row = math.floor(qr_count / cols) % rows
            col = qr_count % cols
            
            # If we've filled a page, create a new one
            if row == 0 and col == 0 and qr_count > 0:
                # Draw cutting guidelines on the current page before moving to next page
                draw_cutting_guidelines(c, cols, rows, MARGIN, ITEM_WIDTH + SPACING, ITEM_HEIGHT + SPACING)
                c.showPage()
                current_page += 1
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(name)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save the QR code as a temporary file
            temp_file = os.path.join(temp_dir, f"qr_{qr_count}.png")
            img.save(temp_file)
            temp_files.append(temp_file)
            
            # Calculate cell position
            cell_x = MARGIN + col * (ITEM_WIDTH + SPACING) + 0 * mm # manual offset
            cell_y = height - MARGIN - ITEM_HEIGHT - row * (ITEM_HEIGHT + SPACING) - 0 * mm # manual offset
            
            # Center QR code within the cell
            x = cell_x + (ITEM_WIDTH - QR_CODE_SIZE) / 2
            y = cell_y + LABEL_HEIGHT
            
            # Draw QR code
            c.drawImage(temp_file, x, y, width=QR_CODE_SIZE, height=QR_CODE_SIZE)
            
            # Draw label using the registered font that supports Czech characters
            c.setFont(FONT_NAME, FONT_SIZE)
            c.drawCentredString(cell_x + ITEM_WIDTH/2, cell_y + LABEL_HEIGHT/2, name)
            
            # Increment counter
            qr_count += 1
        
        # Draw cutting guidelines on the last page
        draw_cutting_guidelines(c, cols, rows, MARGIN, ITEM_WIDTH + SPACING, ITEM_HEIGHT + SPACING)
        
        # Save the PDF
        c.save()
        print(f"Generated {current_page} page(s) with a total of {qr_count} QR codes.")
        print(f"Output saved to {output_filename}")
        
    finally:
        # Clean up temporary files
        for file in temp_files:
            try:
                os.remove(file)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

def draw_cutting_guidelines(c, cols, rows, margin, col_width, row_height):
    """Draw dashed lines for cutting guides"""
    c.setDash([2, 2], 0)  # Set dashed line style
    c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Light gray color
    
    page_width, page_height = A4
    
    # Draw vertical lines (cols - 1)
    for i in range(0, cols + 1):
        x = margin + i * col_width
        c.line(x, margin, x, page_height - margin)
    
    # Draw horizontal lines (rows - 1)
    for i in range(0, rows + 1):
        y = page_height - margin - i * row_height
        c.line(margin, y, page_width - margin, y)

if __name__ == "__main__":
    # Example list of names
    names = [
        "Bětka", "Anča", "Eli", "Tereza", "Baru", "Klára", "Maru", "Kika", "Adéla", 
        "Kačka", "Jana", "Ála", "Verča", "Zuzka", "Luci", "Naty", "Mája", "Vendy",
        "Hanka", "Kája", "Sofi", "Eva", "Martina", "Dája", "Lída", "Marky",
        "Niky", "Andy", "Štěpa", "Bea", "Róza", "Dorka", "Justy", "Áma", 
        "Joha", "Lenka", "Božka", "Móňa", "Sába", "Radka", "Peťa", "Ivča", 
        "Reny", "Blanka", "Céca", "Cilda", "Dáša", "Fany"
    ]
    
    # To use the script with your own list, replace the names list above
    # or uncomment and modify the following code to read from a text file:
    """
    with open('names.txt', 'r') as file:
        names = [line.strip() for line in file if line.strip()]
    """
    
    generate_qr_codes_pdf(names)