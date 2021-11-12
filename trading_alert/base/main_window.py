import time
import tkinter
from threading import Thread
from tkinter import font

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler, FigureManagerBase
from matplotlib.figure import Figure

import numpy as np

from trading_alert.binance_plot import PricePlot


class MainWindow:
    def __init__(self, ta):
        self.is_destroyed = False
        self.root = tkinter.Tk()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Courier', size=14)

        self.root.option_add("*Font", default_font)
        self.root.wm_title("Embedding in Tk")

        tkinter.Grid.rowconfigure(self.root, 0, weight=1)
        tkinter.Grid.columnconfigure(self.root, 0, weight=100)

        tkinter.Grid.columnconfigure(self.root, 1, weight=1)

        left_side = tkinter.Frame(self.root)
        left_side.grid(row=0, column=0, sticky="NSEW")

        right_side = tkinter.Frame(self.root)
        right_side.grid(row=0, column=1, sticky="NSEW")

        tkinter.Grid.rowconfigure(right_side, 0, weight=1)
        tkinter.Grid.columnconfigure(right_side, 0, weight=1)

        tkinter.Grid.rowconfigure(right_side, 1, weight=100)

        option_frame = tkinter.Frame(right_side)
        option_frame.grid(row=0, column=0, sticky="NSEW")

        button = tkinter.Button(master=option_frame, text="All", command=self._show_all_list)
        button.pack(side=tkinter.LEFT)
        button = tkinter.Button(master=option_frame, text="Has alert", command=self._show_bookmark_list)
        button.pack(side=tkinter.LEFT)

        self.all_list_frame = tkinter.Frame(right_side)
        self.all_list_frame.grid(row=1, column=0, sticky="NSEW")

        self.bookmark_list_frame = tkinter.Frame(right_side)
        self.bookmark_list_frame.grid(row=1, column=0, sticky="NSEW")

        self.ta = ta
        self._init_plot(left_side, ta)

        button = tkinter.Button(master=left_side, text="Quit", command=self._quit)
        button.pack(side=tkinter.BOTTOM)

        self._add_total_balance(left_side)

        self._init_all_list(ta)
        self._init_bookmark_list(ta)

    def _add_total_balance(self, left_side):
        self.balance_var = tkinter.StringVar()
        balance_label = tkinter.Label(left_side, textvariable=self.balance_var)
        balance_label.pack(side=tkinter.RIGHT)
        self._update_total_balance()

    def _update_total_balance(self, interval=15 * 60):
        def _th():
            while True:

                sum_usdt = 0.0
                balances = self.ta.client.get_account()
                for _balance in balances["balances"]:
                    asset = _balance["asset"]
                    if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
                        quantity = float(_balance["free"]) + float(_balance["locked"])
                        if asset == "USDT":
                            sum_usdt += quantity
                        else:
                            sum_usdt += quantity * float(self.ta.symbol_prices[asset + "USDT"])

                self.balance_var.set(f"total USDT: {sum_usdt:.2f}")

                time.sleep(interval)

        Thread(target=_th).start()

    def _init_all_list(self, ta):
        symbols = []
        for symbol in ta.symbol_prices.keys():
            if symbol[-4:] == "USDT":
                symbols.append(symbol[:-4] + "/" + symbol[-4:])
        symbols = sorted(symbols)
        list_items = tkinter.StringVar(value=symbols)
        self.all_list = tkinter.Listbox(master=self.all_list_frame, listvariable=list_items)
        self.all_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        scrollbar = tkinter.Scrollbar(self.all_list_frame)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
        self.all_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.all_list.yview)
        self.all_list.bind('<<ListboxSelect>>', self.items_selected)

    def _init_bookmark_list(self, ta):
        symbols = []
        has_alert = False
        for pp in ta.pp_collection.values():
            if pp.ld.has_alert():
                symbols.append(pp.symbol[:-4] + "/" + pp.symbol[-4:])
                has_alert = True
        symbols = sorted(symbols)
        list_items = tkinter.StringVar(value=symbols)
        self.bookmark_list = tkinter.Listbox(master=self.bookmark_list_frame, listvariable=list_items)
        self.bookmark_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        scrollbar = tkinter.Scrollbar(master=self.bookmark_list_frame)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
        self.bookmark_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.bookmark_list.yview)
        self.bookmark_list.bind('<<ListboxSelect>>', self.items_selected)
        if not has_alert:
            self._show_all_list()
        else:
            self._show_bookmark_list()

    def _show_all_list(self):
        self.all_list_frame.tkraise()
        self.current_list = self.all_list

    def _show_bookmark_list(self):
        self.bookmark_list_frame.tkraise()
        self.current_list = self.bookmark_list

    def _init_plot(self, frame, ta):
        self.canvas = FigureCanvasTkAgg(ta.main_pp.fig, frame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.figure_manager = FigureManagerBase(self.canvas, 0)
        ta.main_pp.fig.canvas.manager = self.figure_manager
        self.cid = self.canvas.mpl_connect("key_press_event", ta.main_pp.on_press)

    # handle event
    def items_selected(self, event):
        """ handle item selected event
        """
        selected_symbol = self.current_list.get(self.current_list.curselection()[0]).replace("/", "")
        print(f'You selected: {selected_symbol}')
        self.to_symbol_plot(selected_symbol)

    def to_symbol_plot(self, selected_symbol):
        if selected_symbol not in self.ta.pp_collection.keys():
            self.ta.pp_collection[selected_symbol] = PricePlot(self.ta, symbol=selected_symbol, **self.ta.kwargs)
            self.ta.main_pp = self.ta.pp_collection[selected_symbol]
            self.ta.main_pp.fig.canvas.manager = FigureManagerBase(self.canvas, 0)
        else:
            self.ta.main_pp = self.ta.pp_collection[selected_symbol]
            self.ta.main_pp.init_data_vars()
        self.canvas.figure = self.ta.main_pp.fig
        self.canvas.figure.set_canvas(self.canvas)
        self.canvas.draw()
        self.canvas.mpl_disconnect(self.cid)
        self.cid = self.canvas.mpl_connect("key_press_event", self.ta.main_pp.on_press)

        def _foucs_set():
            time.sleep(0.1)
            self.canvas._tkcanvas.focus_set()

        Thread(target=_foucs_set).start()

    def _quit(self):
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.is_destroyed = True
