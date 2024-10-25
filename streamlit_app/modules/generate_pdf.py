from io import BytesIO
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


def generate_pdf(fig1=None, fig2=None, fig3=None, fig4=None, fig5=None, fig6=None, fig7=None):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("Helvetica", 20)
        c.drawString(100, 800, "Sentiment Analysis Report")

        if fig1 is not None:
            buffer1 = BytesIO()
            fig1[1].write_image(buffer1, format="png")
            buffer1.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 700, fig1[0])
            image1 = ImageReader(buffer1)
            c.drawImage(image1, 100, 500, width=400, height=150)

        if fig2 is not None:
            buffer2 = BytesIO()
            fig2[1].write_image(buffer2, format="png")
            buffer2.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 400, fig2[0])
            image2 = ImageReader(buffer2)
            c.drawImage(image2, 100, 200, width=400, height=150)

        c.showPage()

        if fig3 is not None:
            buffer3 = BytesIO()
            fig3[1].write_image(buffer3, format="png")
            buffer3.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 800, fig3[0])
            image3 = ImageReader(buffer3)
            c.drawImage(image3, 100, 600, width=400, height=150)

        if fig4 is not None:
            buffer4 = BytesIO()
            fig4[1].write_image(buffer4, format="png")
            buffer4.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 400, fig4[0])
            image4 = ImageReader(buffer4)
            c.drawImage(image4, 100, 200, width=400, height=270)

        c.showPage()

        if fig5 is not None:
            buffer5 = BytesIO()
            fig5[1].write_image(buffer5, format="png")
            buffer5.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 800, fig5[0])
            image5 = ImageReader(buffer5)
            c.drawImage(image5, 100, 600, width=400, height=150)

        if fig6 is not None:
            buffer6 = BytesIO()
            fig6[1].write_image(buffer6, format="png")
            buffer6.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 400, fig6[0])
            image6 = ImageReader(buffer6)
            c.drawImage(image6, 100, 200, width=400, height=150)

        c.showPage()

        if fig7 is not None:
            buffer7 = BytesIO()
            fig7[1].write_image(buffer7, format="png")
            buffer7.seek(0)
            c.setFont("Helvetica", 12)
            c.drawString(100, 800, fig7[0])
            image7 = ImageReader(buffer7)
            c.drawImage(image7, 100, 600, width=400, height=150)

        c.showPage()
        c.save()

        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        print(e)
        return None


def construct_pdf():
    fig1 = ("Sentiment over Time Elapsed", st.session_state["sentiment_over_date"])
    fig2 = ("Sentiment Distribution", st.session_state["display_target_count"])
    fig3 = ("Most Frequent Bigrams", st.session_state["most_common_trigrams"])
    fig4 = ("Word Cloud - Most Common Terms", st.session_state["display_word_cloud"])
    fig5 = ("Relationship Between Number of Likes and Sentiment Tags", st.session_state["create_scatter_plot"])
    fig6 = ("Account Creation Time Distribution by Comment Sentiment", st.session_state["stacked_bar_fig"])
    fig7 = ("User Locations", st.session_state["locations_graphic"])

    return generate_pdf(fig1, fig2, fig3, fig4, fig5, fig6, fig7)

