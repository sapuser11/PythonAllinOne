from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_invoice(courses, filename="anubhav_invoice.pdf"):
    """
    Generate a PDF invoice with company details, course information, and tax calculation.
    
    Args:
        courses (list): List of dictionaries with course details 
                       (course_name, trainer, price, duration)
        filename (str): Output filename for the PDF
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Add company details (header)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*cm, height - 2*cm, "Anubhav Trainings")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*cm, height - 3*cm, "123 learning street, Bangalore, India")
    c.drawString(1*cm, height - 3.5*cm, "+918445454549")
    c.drawString(1*cm, height - 4*cm, "contact@anubhavtrainings")
    
    # Add date on right side
    current_date = datetime.now().strftime("%d/%m/%Y")
    c.drawRightString(width - 1*cm, height - 2*cm, f"Date: {current_date}")
    
    # Add invoice title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 6*cm, "INVOICE")
    
    # Create table data
    data = [["Course Name", "Trainer", "duration", "Price"]]
    
    # Calculate total
    total = 0
    
    # Draw table headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, height - 8*cm, "Course Name")
    c.drawString(7*cm, height - 8*cm, "Trainer")
    c.drawString(11*cm, height - 8*cm, "duration")
    c.drawString(15*cm, height - 8*cm, "Price")
    
    # Draw horizontal line below headers
    c.line(1*cm, height - 8.5*cm, width - 1*cm, height - 8.5*cm)
    
    # Add course details
    y_position = height - 9.5*cm
    c.setFont("Helvetica", 10)
    
    for course in courses:

        c.drawString(1*cm, y_position, course[1])
        c.drawString(7*cm, y_position, course[2])
        c.drawString(11*cm, y_position, str(course[4]))
        c.drawString(15*cm, y_position, f"${course[3]:.2f}")
        total += course[3]
        y_position -= 1*cm
    
    # Draw horizontal line
    c.line(1*cm, y_position + 0.5*cm, width - 1*cm, y_position + 0.5*cm)
    
    # Calculate tax
    tax = total * 0.18
    grand_total = total + tax
    
    # Add totals
    c.setFont("Helvetica-Bold", 10)
    y_position -= 1*cm
    c.drawString(11*cm, y_position, "Subtotal:")
    c.drawString(15*cm, y_position, f"${total:.2f}")
    
    y_position -= 0.8*cm
    c.drawString(11*cm, y_position, "IGST (18%):")
    c.drawString(15*cm, y_position, f"${tax:.2f}")
    
    y_position -= 0.8*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(11*cm, y_position, "Total:")
    c.drawString(15*cm, y_position, f"${grand_total:.2f}")
    
    # Add footer
    c.setFont("Helvetica", 10)
    c.drawString(1*cm, 3*cm, "Thank you for your business!")
    
    # Save the PDF
    c.save()
    
    return filename

if __name__ == "__main__":
    # Example usage
    courses = [
        {"course_name": "Python Basics", "trainer": "John Doe", "price": 10000, "duration": 20},
        {"course_name": "Advanced Python", "trainer": "Jane Smith", "price": 15000, "duration": 30},
    ]
    
    generate_invoice(courses, "sample_invoice.pdf")