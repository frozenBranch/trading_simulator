import tkinter as tk
from tkinter.filedialog import askopenfile
import pandas as pd
from services import CashManager, Stock, ReportData, strategies
from report_design import create_pdf_report
import numpy as np


class AppManager:
    def __init__(self, root):
        self.df_ok: bool = False
        self.capital: int
        self.strat1_opt_a: float = -0.01
        self.strat1_opt_b: float = 0.02
        self.strat2_opt_a: float = 0.1
        self.strat2_opt_b: int = 5
        self.capital_perc: float = 0.03
        self.update_strats_text()

# GUI START
        self.root = root
        self.gui()

    def gui(self) -> None:
        self.root.title('Trading Simulator')
        self.root.geometry('450x450')

        self.frame = tk.Frame(self.root, width=450, height=400)
        self.frame.grid(row=0, column=0, columnspan=3, pady=20)

        self.btn_upload_instruc = tk.Button(self.frame, text='How to Upload data', command=self.upload_instructions_modal)
        self.btn_upload_instruc.grid(row=0, column=1)
        self.btn_upload = tk.Button(self.frame, text='Click to upload data', command=self.open_file)
        self.btn_upload.grid(row=1, column=1)

        self.btn_strat1 = tk.Button(self.frame, text='Strategy 1', command=self.strat1_modal)
        self.btn_strat1.grid(row=2, column=0, pady=20)
        self.btn_strat2 = tk.Button(self.frame, text='Strategy 2', command=self.strat2_modal)
        self.btn_strat2.grid(row=2, column=1, pady=20)
        self.btn_strat3 = tk.Button(self.frame, text='Strategy 3', command=self.strat3_modal)
        self.btn_strat3.grid(row=2, column=2, pady=20)
        
        tk.Label(self.frame, text='Capital to be invested:').grid(row=3, column=0)
        self.entry_capital = tk.Entry(self.frame, width=10)
        self.entry_capital.grid(row=3, column=1)
        tk.Label(self.frame, text='Capital must be between 100 000 and 100 000 000 \n(only integers)').grid(row=4, columnspan=3)

        tk.Label(self.frame, text='% to risk per trade:').grid(row=5, column=0, pady=(20, 0))
        self.entry_capital_perc = tk.Entry(self.frame, width=10)
        self.entry_capital_perc.grid(row=5, column=1, pady=(20, 0))
        tk.Label(self.frame, text='% must be between 1.0 and 5.0').grid(row=6, columnspan=3)

        self.btn_start = tk.Button(self.frame, text='Start the simulation', command=self.start_simulation)
        self.btn_start.grid(row=7, column=1, pady=20)

        self.status_text = tk.StringVar()
        self.status_text.set('')
        self.label_status = tk.Label(self.frame, textvariable=self.status_text)
        self.label_status.grid(columnspan=3)

    def upload_instructions_modal(self) -> None:
        self.modal_upload = tk.Toplevel(self.root)
        self.modal_upload.transient(self.root)
        tk.Label(self.modal_upload, text='To upload the data click on "Click to upload data"\nData timespan should be between 14 days and 3 months\nIt only accepts CSV files with the following format:\nticker, date, price\nYPF, 2021-09-03, 5.6\nGGAL, 2021-09-03, 6.4').pack()
        tk.Button(self.modal_upload, text='OK', command=lambda: self.modal_upload.destroy()).pack()

    def open_file(self) -> None:
        try:
            file = askopenfile(mode='r', filetypes=[('csv file', '*.csv')])
            self.status_text.set('')
            if file:
                self.df = pd.read_csv(file)
                self.df['date'] = pd.to_datetime(self.df['date'])
                self.df = self.df.sort_values(by=['date'], ignore_index=True)
                self.date_range = self.df['date'].iloc[-1] - self.df['date'].iloc[0]
                if self.date_range.days >= 14 and self.date_range.days <= 92:
                    self.df_ok = True
                    self.status_text.set(f"Data upload succesful, tickers:\n {self.df.ticker.unique() if len(self.df.ticker.unique()) < 6 else ' '.join(map(str, self.df.ticker.unique()[:6]))+'...'}")
                else:
                    self.df_ok = False
                    self.status_text.set(f"Data upload failed.\nData timespan should be between 14 days and 3 months")
        except:
            self.status_text.set('There is been an error with the data upload\n Please read the instructions and try again')

    def strat1_modal(self) -> None:
        def close_modal():
            self.strat1_opt_a = float(entry_opt_a.get())/-100
            self.strat1_opt_b = float(entry_opt_b.get())/100
            self.update_strats_text()
            self.modal_strat1.destroy()
        self.modal_strat1 = tk.Toplevel(self.root)
        self.modal_strat1.transient(self.root)

        tk.Label(self.modal_strat1, text=f"Strategy 1\n{self.strat1_a_text}\n{self.strat1_b_text}").pack()
        self.frame_strat1 = tk.Frame(self.modal_strat1)
        self.frame_strat1.pack()
        tk.Label(self.frame_strat1, text='opt (a): %').grid(row=0, column=0)
        entry_opt_a = tk.Entry(self.frame_strat1)
        entry_opt_a.insert(0, f"{self.strat1_opt_a*-100}")
        entry_opt_a.grid(row=0, column=1)
        tk.Label(self.frame_strat1, text='opt (b): %').grid(row=1, column=0)
        entry_opt_b = tk.Entry(self.frame_strat1)
        entry_opt_b.insert(0, f"{self.strat1_opt_b*100}")
        entry_opt_b.grid(row=1, column=1)
        tk.Button(self.modal_strat1, text='OK', command=close_modal ).pack()

    def strat2_modal(self) -> None:
        def close_modal():
            self.strat2_opt_a = float(entry_opt_a.get())
            self.strat2_opt_b = int(entry_opt_b.get())
            self.update_strats_text()
            self.modal_strat2.destroy()
        self.modal_strat2 = tk.Toplevel(self.root)
        self.modal_strat2.transient(self.root)

        tk.Label(self.modal_strat2, text=f"Strategy 2\n{self.strat2_a_text}\n{self.strat2_b_text}").pack()
        self.frame_strat2 = tk.Frame(self.modal_strat2)
        self.frame_strat2.pack()
        tk.Label(self.frame_strat2, text='opt (a): %').grid(row=0, column=0)
        entry_opt_a = tk.Entry(self.frame_strat2)
        entry_opt_a.insert(0, f"{self.strat2_opt_a}")
        entry_opt_a.grid(row=0, column=1)
        tk.Label(self.frame_strat2, text='opt (b): %').grid(row=1, column=0)
        entry_opt_b = tk.Entry(self.frame_strat2)
        entry_opt_b.insert(0, f"{self.strat2_opt_b}")
        entry_opt_b.grid(row=1, column=1)
        tk.Button(self.modal_strat2, text='OK', command=close_modal).pack()

    def strat3_modal(self) -> None:
        def close_modal():
            self.modal_strat3.destroy()
        self.modal_strat3 = tk.Toplevel(self.root)
        self.modal_strat3.transient(self.root)

        tk.Label(self.modal_strat3, text=f"Strategy 3\n{self.strat3_a_text}\n{self.strat3_b_text}").pack()
        self.frame_strat3 = tk.Frame(self.modal_strat3)
        self.frame_strat3.pack()
        tk.Button(self.modal_strat3, text='OK', command=close_modal).pack()

    def update_strats_text(self) -> None:
        self.strat1_a_text = f"(a)BUY: Whenever a Stock price is {self.strat1_opt_a*100}% lower than previous close"
        self.strat1_b_text = f"(b)SELL: Whenever a Stock price is {self.strat1_opt_b*100}% higher than previous close" 
        self.strat2_a_text: str = f"(a)BUY: Whenever a Stock price is at least {self.strat2_opt_a} times higher than the mean price until given date"
        self.strat2_b_text: str = f"(b)SELL: a Stock after {self.strat2_opt_b} days of having bought it"
        self.strat3_a_text: str = f"(a)BUY: When 1(a) and 2(a) happen at the same time"
        self.strat3_b_text: str = f"(b)SELL: When 1(b) or 2(b) happen"
# GUI END

    #Logic begins here
    def start_simulation(self) -> None:
        ready_to_run = False
        if self.df_ok: # Check data is OK
            # Check capital is an integer
            if self.entry_capital.get().isdigit():
                self.capital = int(self.entry_capital.get())
                #Check capital is between 100k and 1000kk
                if 1e5 <= self.capital <= 1e8:
                    try:
                        self.capital_perc = float(self.entry_capital_perc.get())/100
                        if 0.01 <= self.capital_perc <= 0.05:
                            ready_to_run = True
                        else:
                            self.status_text.set('Error: Capital Percentage must be a number between 1.0 and 5.0)')
                    except:
                        self.status_text.set('Error: Capital Percentage must be a number between 1.0 and 5.0)')
                    #Execution
                    if ready_to_run:
                        self.run_simulation()
                else:
                    self.status_text.set('Error: Capital must be between 100 000 and 100 000 000 \n(only integers)')
            else:
                self.status_text.set('Error: Capital must be between 100 000 and 100 000 000 \n(only integers)')
        else:
            self.status_text.set('There is been an error with the data upload\n Please read the instructions and try again')

    def run_simulation(self) -> None:
        self.status_text.set('Processing the data...')
        trading_histories: list = []
        #Pass chosen parameters to the strategies and start looping over them
        for strategy in strategies(self.strat1_opt_a, self.strat1_opt_b, self.strat2_opt_a, self.strat2_opt_b):
            #There is one CashManager for each strategy
            cash_manager = CashManager(self.capital)
            stocks: list[Stock] = []

            #Generate a list of Stock for each stock on the CSV file
            for ticker in self.df.ticker.unique():
                amount_trade = np.round(self.capital*self.capital_perc, 2)
                stocks.append(Stock(ticker, self.df[self.df['ticker']==ticker], cash_manager, amount_trade))

            #For each stock, run every strategy on every date present on the CSV file
            for stock in stocks:
                for date in stock.df.date.iloc[1:-1]:
                    strategy(stock, date)
                #Finally sell every remaining stock
                stock.sell_stock(stock.df.price.iloc[-1], stock.df.date.iloc[-1])

            if len(cash_manager.cash_history) > 1:
                history = pd.DataFrame(cash_manager.cash_history[1:], columns=cash_manager.cash_history[0]).sort_values(by='date', ignore_index=True)
            else:
                #If none buy was made on a strategy, fill the dataframe with one generic line
                history = pd.DataFrame([['NA']*5+[self.capital]+['NA']], columns=cash_manager.cash_history[0])
            history.to_csv(f"./exports/{strategy.__name__}_history.csv", index=False)
            trading_histories.append(history)

        self.status_text.set('Data processed succesfuly, creating report...')
        report = (ReportData(trading_histories, self.date_range.days))
        strategies_text = (self.strat1_a_text, self.strat1_b_text, self.strat2_a_text, self.strat2_b_text, self.strat3_a_text, self.strat3_b_text)
        create_pdf_report(report, self.capital, self.capital_perc, self.date_range.days, strategies_text)
        self.status_text.set('Report succesfuly created, check the exports folder')
        
if __name__ == '__main__':
    root = tk.Tk()
    app_manager = AppManager(root)
    root.mainloop()