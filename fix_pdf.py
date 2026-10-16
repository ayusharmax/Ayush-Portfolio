from pypdf import PdfReader, PdfWriter

reader = PdfReader("static/AYUSH_RESUME.pdf")
writer = PdfWriter(clone_from=reader)
writer.add_metadata({
    "/Title": "Ayush Sharma - Resume",
    "/Author": "Ayush Sharma",
})
with open("static/AYUSH_RESUME_fixed.pdf", "wb") as f:
    writer.write(f)
print("done")