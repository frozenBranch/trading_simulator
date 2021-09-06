from fpdf import FPDF

def output_df_to_pdf(pdf, df, width=25, height=6, font_size=8):
    # A cell is a rectangular area, possibly framed, which contains some text
    # Set the width and height of cell
    table_cell_width = width
    table_cell_height = height
    # Select a font as Arial, bold, 8
    pdf.set_font('Arial', 'B', font_size)
    
    # Loop over to print column names
    cols = df.columns
    for col in cols:
        pdf.cell(table_cell_width, table_cell_height, col, align='C', border=1)
    # Line break
    pdf.ln(table_cell_height)
    # Select a font as Arial, regular, 10
    pdf.set_font('Arial', '', 10)
    # Loop over to print each data in the table
    for row in df.itertuples():
        for col in cols:
            value = str(getattr(row, col))
            pdf.cell(table_cell_width, table_cell_height, value, align='C', border=1)
        pdf.ln(table_cell_height)

def create_pdf_report(report, capital, capital_perc, days, strategies_text):
    strat1_a, strat1_b, strat2_a, strat2_b, strat3_a, strat3_b = strategies_text
    strategies_titles = ['Strategy 1', 'Strategy 2', 'Strategy 3', 'Benchmark']
    pdf = FPDF()
    pdf.add_page()
    # PAGE 1
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(40, 10, 'Performance Report')
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(20, txt='Strategy 1:')
    pdf.ln(5)
    pdf.cell(20, txt=strat1_a)
    pdf.ln(5)
    pdf.cell(20, txt=strat1_b)
    pdf.ln(8)
    pdf.cell(20, txt='Strategy 2:')
    pdf.ln(5)
    pdf.cell(20, txt=strat2_a)
    pdf.ln(5)
    pdf.cell(20, txt=strat2_b)
    pdf.ln(8)
    pdf.cell(20, txt='Strategy 3:')
    pdf.ln(5)
    pdf.cell(20, txt=strat3_a)
    pdf.ln(5)
    pdf.cell(20, txt=strat3_b)
    pdf.ln(8)
    pdf.cell(20, txt='Benchmark: Buy every stock on day 1 and hold until last day')
    pdf.ln(15)
    pdf.cell(20, txt=f"Capital invested: {capital}")
    pdf.ln(5)
    pdf.cell(20, txt=f"Investment duration: {days} days")
    pdf.ln(5)
    pdf.cell(20, txt=f"Percentage of capital invested on each trade: {capital_perc*100}%")
    pdf.ln(15)
    pdf.cell(20, txt=f"Performance of each strategy")
    pdf.ln(5)
    output_df_to_pdf(pdf, report.strategies_profit())

    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Top 5 most bought stocks by strategy')
    pdf.set_font('Arial', 'B', 10)
    pdf.ln(20)

    for df, title in zip(report.most_bought_per_strat(), strategies_titles):
        pdf.cell(20, txt=title)
        pdf.ln(5)
        output_df_to_pdf(pdf, df)
        pdf.ln(10)

    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Top 3 most profitable stocks by strategy')
    pdf.set_font('Arial', 'B', 10)
    pdf.ln(20)

    for df, title in zip(report.most_profit_per_strat(), strategies_titles):
        pdf.cell(20, txt=title)
        pdf.ln(5)
        output_df_to_pdf(pdf, df)
        pdf.ln(10)
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Top 5 most bought stocks in total')
    pdf.set_font('Arial', 'B', 10)
    pdf.ln(20)
    output_df_to_pdf(pdf, report.most_bought_total())
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Top 3 most profitable stocks in total')
    pdf.set_font('Arial', 'B', 10)
    pdf.ln(20)
    output_df_to_pdf(pdf, report.most_profit_total())

    pdf.output('./exports/report.pdf', 'F')
    pass