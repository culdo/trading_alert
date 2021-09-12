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

from trading_alert.candle_plotting import PricePlot


class MainWindow:
    def __init__(self, ta):
        self.is_destroyed = False
        self.root = tkinter.Tk()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Courier', size=14)

        self.root.option_add("*Font", default_font)
        self.root.wm_title("Embedding in Tk")

        frame = tkinter.Frame(self.root)
        frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

        list_frame = tkinter.Frame(self.root)
        list_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)

        self.ta = ta
        self._init_plot(frame, ta)

        button = tkinter.Button(master=frame, text="Quit", command=self._quit)
        button.pack(side=tkinter.BOTTOM)

        symbols = []
        for item in ta.symbols_ticker:
            if item["symbol"][-4:] == "USDT":
                symbols.append(item['symbol'][:-4] + "/" + item['symbol'][-4:])

        symbols = sorted(symbols)
        list_items = tkinter.StringVar(value=symbols)
        self.listbox = tkinter.Listbox(master=list_frame, listvariable=list_items)
        self.listbox.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

        scrollbar = tkinter.Scrollbar(list_frame)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)


        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind('<<ListboxSelect>>', self.items_selected)

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
        selected_symbol = self.listbox.get(self.listbox.curselection()).replace("/", "")
        print(f'You selected: {selected_symbol}')
        self.to_symbol_plot(selected_symbol)

    def to_symbol_plot(self, selected_symbol):
        if selected_symbol not in self.ta.pp_collection.keys():
            self.ta.pp_collection[selected_symbol] = PricePlot(self.ta, symbol=selected_symbol, **self.ta.kwargs)
            self.ta.main_pp = self.ta.pp_collection[selected_symbol]
            self.ta.main_pp.fig.canvas.manager = FigureManagerBase(self.canvas, 0)
        else:
            self.ta.main_pp = self.ta.pp_collection[selected_symbol]
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
