import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox, QPushButton, QLabel, QTabWidget, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QCheckBox,QHBoxLayout,QSlider, QScrollArea,QTreeWidget,QTreeWidgetItem,QMessageBox
from PyQt5.QtGui import QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_finance import candlestick_ohlc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt 
from PyQt5.QtCore import Qt
from stocker import Stocker
import threading
import csv
import matplotlib.dates as dates
from datetime import datetime
import datetime as datetmp
import pandas as pd
import strategy.genetic_algorithm as gen
import strategy.bband as bb
import strategy.rsi as rsi
import strategy.arron as arron
import strategy.redthreesoldiers as redthreesoldiers
import strategy.williams as williams
import strategy.lstmpred as lstm
import strategy.popular_model as popmoder 
import talib
import numpy as np
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
class StockAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置字体和字族
        #plt.rcParams['font.family'] = ['DFKai-sb']
        plt.rcParams['font.family'] = ['Microsoft JhengHei']  
        #plt.rcParams['font.family'] = 'sans-serif'

        self.setWindowTitle("回測工具")
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowIcon(QIcon('icon.png'))  # 設定應用程式圖示

        # Initialize the new attributes for storing data
        self.data_list = []
        self.data_list2 = []
        self.data_list3 = []
        self.data_list4 = []
        self.date_ex = []
        self.start = 0
        self.end = 0

        # 購買資料
        self.buy_list = []
        self.sell_list = []
        

        # 個別參數
        self.model = "none"
        self.now_stock = None
        self.start = None
        self.end = None
        self.str_tmp = None
        self.orgdate = None
        self.ope = None
        self.close = None
        self.high = None
        self.low = None
        self.vol = None
        self.date = None
        self.date_ex = None
        self.BBand_up = None
        self.BBand_sma = None
        self.BBand_down = None
        self.BBand_width = None
        self.BBand_mid = None
        self.catch_stock = None
        self.catch_stockgarbage = None
        self.fbpropht_data = None
        self.deposit = None
        self.strategy = ["BBand", "lstm", "Rsi", "Arron", "ATR", "KD", "T3", "一紅吃一黑", "redthreesoldiers", "Williams", "辰星", "跳空買進", "arr", "fbpropht", "keras", "google_trend"]
        self.draw_tmp = None
        self.thread_bolean = None
        self.folderpath = None
        self.folderpath = "history_data"

        # # 檢查目錄是否存在 
        if os.path.isdir(self.folderpath)==0:
            os.mkdir(self.folderpath)
        # 模組設定
        self.strategy_model = None

        df = pd.DataFrame()
        self.setup_ui()

        default_dir = os.path.expanduser(r"C:\Users\lenovo\Desktop")  # 使用單個反斜杠來表示Windows風格的路徑
        self.fname = self.ask_for_file(title="選擇回測檔案", initialdir=default_dir)
        
    def backtest(self, model_name):
        # 移动原来在 backtest 函数中的全局变量到这里，或者作为参数传递

        # 交易策略参数设置
        self.str_tmp = "回測模組:" + model_name + '\n'
        star = 100000  # 初始金額無變動
        price = 100000  # 變動初始金額
        star = price
        ex_handle = 20  # 一次股數上限

        # 参数列表
        data_param = [star,price,ex_handle,self.buy_list,self.sell_list,self.data_list,self.data_list2,self.data_list3,self.start,self.end,
                      self.str_tmp,self.ope,self.close,self.high,self.low,self.vol,self.date,self.date_ex,self.now_stock,self.model]
        data_param2 = [star,price,ex_handle,self.buy_list,self.sell_list,self.data_list,self.data_list2,self.data_list3,self.start,self.end,
                      self.str_tmp,self.ope,self.close,self.high,self.low,self.vol,self.date,self.date_ex,self.now_stock,self.model]
        # print(len(data_list4))
        if model_name == "BBand":
            self.str_tmp += bb.bband(data_param)
        if model_name == "lstm":
            self.str_tmp += lstm.lstm(data_param2)
            return
        elif model_name == "Rsi": 
            self.str_tmp += rsi.rsi(data_param)
        elif model_name == "Arron":
            self.str_tmp += arron.arron(data_param)
        elif model_name == "redthreesoldiers":
            self.str_tmp += redthreesoldiers.redthreesoldiers(data_param)
        elif model_name == "Williams":
            self.str_tmp += williams.williams(data_param)
        elif model_name == "show_fbpropht":
            self.show_fbpropht()  # 调用类内的方法
    def read_file(self, file_path):
        if not file_path:
            return
        self.now_stock = file_path
   
        # Clear previous data
        self.date_ex=[]
        self.date=[]
        self.orgdate=[]
        self.low=[]
        self.high=[]
        self.ope=[]
        self.close=[]
        self.vol=[]
        self.data_list.clear()
        self.data_list2.clear()
        self.data_list3.clear()
        self.orgdate.clear()
        self.catch_stock = []
        self.catch_stockgarbage =[]
        self.date.clear()
        self.low.clear()
        self.high.clear()
        self.close.clear()
        self.ope.clear()
        self.vol.clear()
        self.data_list.clear()
        self.data_list2.clear()
        self.data_list3.clear()
        self.data_list4.clear()
        self.date_ex.clear()

        with open(file_path, 'r', encoding="utf_8_sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ope = float(row["開盤"])
                high = float(row["最高"])
                low = float(row["最低"])
                close = float(row["收盤"])
                vol = float(row["成交量"])
                date_str = row["日期"].replace('/', '-')
                date_processed = dates.date2num(datetime.strptime(date_str, '%Y-%m-%d'))

                self.data_list.append((date_processed, ope, high, low, close))
                self.data_list2.append((date_processed, ope, high, low, close, vol))
                self.data_list3.append((date_str, close))
                self.data_list4.append([ope, high, low, close, vol])
                self.date_ex.append(date_processed)
                self.ope.append(ope)
                self.close.append(ope)
                self.high.append(high)
                self.low.append(low)
                self.vol.append(vol)
                self.date.append(date_str)
 
        self.start=0
        self.end=len(self.data_list)
        self.slider.setMinimum(self.start)
        self.slider.setMaximum(self.end-1)
        self.slider2.setMinimum(self.start)
        self.slider2.setMaximum(self.end-1)
        # self.slider.setValue(50 - 1)
        self.slider2.setValue(int(self.end)-1)

    def ask_for_file(self, title, initialdir):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, title, directory=initialdir, options=options)
        self.read_file(file_path)
        return file_path

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        self.setup_frame1(tab_widget)
        self.setup_frame2(tab_widget)
        self.setup_frame7(tab_widget)
        self.setup_frame8(tab_widget)
    def on_slider_change(self):
        self.var = self.slider.value()
        pass
    def on_slider_change2(self):
        self.var2 = self.slider2.value()
        pass
    def draw_pic(self):
        # self.statusBar().showMessage("執行繪圖中..")
        self.setWindowTitle("執行繪圖中..")
        self.strategy_model = self.numberChosen.currentText()
        
        ## 取得模組名稱
        self.backtest(self.strategy_model)
        
        self.figure1.clf()
        self.figure2.clf()

        self.a = self.figure1.add_subplot(211)
        self.a2 = self.figure1.add_subplot(212)
        
        self.figure1.subplots_adjust(hspace=0)
        self.a.xaxis_date()
        self.a2.xaxis_date()
        for label in self.a.xaxis.get_ticklabels():   
            label.set_rotation(45)
        for label in self.a2.xaxis.get_ticklabels():   
            label.set_rotation(45)

        self.a.set_title("K", fontsize=20)
        self.a2.set_xlabel("time", fontsize=10)
        self.a.set_ylabel("price", fontsize=10)
        self.a2.set_ylabel("volume", fontsize=10)

        sma_5 = talib.SMA(np.array(self.close), 5)
        sma_10 = talib.SMA(np.array(self.close), 10)
        sma_20 = talib.SMA(np.array(self.close), 20)
        sma_60 = talib.SMA(np.array(self.close), 60)

        start = self.var
        end = self.var2
        if self.var4 == 1:
            self.a.plot(self.date_ex[start:end:5], sma_5[start:end:5], label='SMA5')
            self.a.plot(self.date_ex[start:end:10], sma_10[start:end:10], label='SMA10')
            self.a.plot(self.date_ex[start:end:20], sma_20[start:end:20], label='SMA20')
            self.a.plot(self.date_ex[start:end:60], sma_60[start:end:60], label='SMA60')
            self.a.legend(loc='upper left')

        # self.var5.set(self.date[start])
        # self.var6.set(self.date[end])
        candlestick_ohlc(self.a, self.data_list[start:end+1], width=0.5, colorup='r', colordown='g')
        pos_d = []
        pos_v = []
        neg_d = []
        neg_v = []

        for x in self.data_list2[start:end+1]:
            if (x[1] - x[4]) <= 0:
                pos_d.append(x[0])
                pos_v.append(x[5])
            elif (x[1] - x[4]) > 0:
                neg_d.append(x[0])
                neg_v.append(x[5])

        self.a2.bar(pos_d, pos_v, color='red', width=0.5, align='center')
        self.a2.bar(neg_d, neg_v, color='green', width=0.5, align='center')

        if self.var7 == 1:
            self.BBand = popmoder.get_BBand(np.asarray(self.close))
            self.BBand_up = [float(x) for x in self.BBand[0]]
            self.BBand_sma = [float(x) for x in self.BBand[1]]
            self.BBand_down = [float(x) for x in self.BBand[2]]
            
            self.a.plot(self.date_ex[start:end:1], self.BBand_sma[start:end:1], label='BBnad')
            self.a.plot(self.date_ex[start:end:1], self.BBand_up[start:end:1], label='BBnad_up')
            self.a.plot(self.date_ex[start:end:1], self.BBand_down[start:end:1], label='BBnad_down')
            self.a.legend(loc='upper left')
        
        if self.var8 == 1:
            self.BBand_up = [float(x) for x in self.BBand[0]]
            self.BBand_sma = [float(x) for x in self.BBand[1]]
            self.BBand_down = [float(x) for x in self.BBand[2]]
            
            self.BBand_mid = []
            self.BBand_width = []
            for x in range(0, len(self.BBand_sma), 1):
                self.BBand_mid.append((self.BBand_up[x] + self.BBand_down[x]) / 2)
        
            for x in range(0, len(self.BBand_mid), 1):
                self.BBand_width.append(100 * ((self.BBand_up[x] - self.BBand_down[x]) / self.BBand_mid[x]))
                
            self.a.plot(self.date_ex[start:end:1], self.BBand_width[start:end:1], label='BBnad_width')
            self.a.legend(loc='upper left')

        if self.var3 == 1:
            for x in range(0, len(self.buy_list), 1):    
                self.a.annotate('', xy=(self.buy_list[x][0], self.buy_list[x][1]), xytext=(-15, -27),
                                textcoords='offset points', ha="center",
                                arrowprops=dict(facecolor='black', color='red', width=0.5),
                )
                
            for x in range(0, len(self.sell_list), 1):    
                self.a.annotate('', xy=(self.sell_list[x][0], self.sell_list[x][1]),  xytext=(-17, 20),
                                textcoords='offset points', ha="center",
                                arrowprops=dict(facecolor='black', color='green', width=0.5),
                )

        self.a.grid()
        self.a2.grid()
        self.canvas1.draw()

        df = pd.read_csv('price2.csv', index_col='date', parse_dates=['date'])
        price = df.squeeze()
        price.head()
        print(price)
        self.figure2.clf()
        self.a = self.figure2.add_subplot(111)
        self.a.grid()
        self.a.set_title('price')
        self.figure2.subplots_adjust(hspace=0) 
        self.a.plot(price)
        self.a.text(0.13, 0.3, self.str_tmp, transform=self.figure2.transFigure, fontsize=15, color='red',)
        
        self.canvas2.draw()
        self.setWindowTitle("執行繪圖中..完畢")
        self.show_info()

        
    def checkbox_changed(self, state):
        # Handle checkbox state change here
        if self.cb1.isChecked():
            self.var3 =1
        else:
            self.var3 =0
        if self.cb2.isChecked():
            self.var4 =1
        else:
            self.var4 =0
        if self.cb3.isChecked():
            self.var7 =1
        else:
            self.var7 =0
        if self.cb4.isChecked():
            self.var8 =1
        else:
            self.var8 =0
    def show_fbpropht(self):
        self.fbpropht_data
        self.now_stock
        
        df = pd.read_csv(self.now_stock, encoding= 'utf_8_sig')
    
        df = df.rename(columns={"日期":"Date", 
                            "成交量":"Volume" ,
                            "成交金額":"Turnover", 
                            "開盤":"Open", 
                            "最高":"High", 
                            "最低":"Low", 
                            "收盤":"Close", 
                            "漲跌價差":"Change",
                            "成交筆數":"Transaction"
                            })      

        df['Date']= pd.to_datetime(df['Date']) 
        df = df.sort_values(by='Date')
        df = df.reset_index(drop=True)
        df.head()
        print(df)
        price = df.squeeze()
        price.head()
        tsmc = Stocker('AMZN',price)
        # model, model_data, ax, fig = tsmc.create_prophet_model(days=90)
        self.figure2.clf()
        model, future, ax, fig = tsmc.create_prophet_model(days=90, figure=self.figure2)
        self.canvas2.draw()
        self.canvas2.update()

    def reread_file(self):
        default_dir = os.path.expanduser(r"C:\Users\lenovo\Desktop")  # 使用單個反斜杠來表示Windows風格的路徑
        self.fname = self.ask_for_file(title="選擇回測檔案", initialdir=default_dir)
        self.read_file(self.fname)

    def setup_frame1(self, tab_widget):
       
        # 在这里初始化组件并设置为类属性
        self.frame1 = QWidget()
        self.layout = QVBoxLayout()
        self.frame1.setLayout(self.layout)

        # 上面部分（图形）
        self.top_widget = QWidget()
        self.top_layout = QVBoxLayout()
        self.top_widget.setLayout(self.top_layout)

        self.figure1 = Figure(figsize=(18.3, 15))  # 调整图形的大小
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar = NavigationToolbar(self.canvas1, self)
        
        self.top_layout.addWidget(self.canvas1)
        self.top_layout.addWidget(self.toolbar)
        
        # 下面部分（按钮和下面的图形）
        self.bottom_widget = QWidget()
        self.bottom_layout = QHBoxLayout()
        self.bottom_widget.setLayout(self.bottom_layout)

        # 左侧部分（按钮、滑块和 QCheckBox）
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.button0 = QPushButton('read file', self)
        self.button0.clicked.connect(self.reread_file)
        self.button1 = QPushButton('回測', self)
        self.button1.clicked.connect(self.draw_pic)
        self.left_layout.addWidget(self.button0)
        self.left_layout.addWidget(self.button1)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.on_slider_change)

        self.slider2 = QSlider(Qt.Horizontal)

        self.slider2.valueChanged.connect(self.on_slider_change2)
        self.left_layout.addWidget(self.slider)
        self.left_layout.addWidget(self.slider2)

        self.button2 = QPushButton('績效', self)
        self.button2.clicked.connect(self.show_info)
        self.left_layout.addWidget(self.button2)

        self.button3 = QPushButton('特殊模組開啟', self)
        self.button3.clicked.connect(self.show_fbpropht)
        self.left_layout.addWidget(self.button3)

        self.button4 = QPushButton('數據處理', self)
        self.button4.clicked.connect(self.data_deal)
        self.left_layout.addWidget(self.button4)

        self.numberChosen = QComboBox()
        self.numberChosen.addItems(self.strategy )
        self.left_layout.addWidget(self.numberChosen)

        # 新增 QCheckBox
        self.cb1 = QCheckBox('買賣點', self)
        self.cb2 = QCheckBox('SMA', self)
        self.cb3 = QCheckBox('BBnad', self)
        self.cb4 = QCheckBox('BBnad_width', self)

        self.left_layout.addWidget(self.cb1)
        self.left_layout.addWidget(self.cb2)
        self.left_layout.addWidget(self.cb3)
        self.left_layout.addWidget(self.cb4)

        # Connect the stateChanged signal of each QCheckBox to a slot function
        self.cb1.stateChanged.connect(self.checkbox_changed)
        self.cb2.stateChanged.connect(self.checkbox_changed)
        self.cb3.stateChanged.connect(self.checkbox_changed)
        self.cb4.stateChanged.connect(self.checkbox_changed)

        # 右侧部分（下面的图形）
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        self.figure2 = Figure(figsize=(6, 4))
        self.canvas2 = FigureCanvas(self.figure2)
        self.right_layout.addWidget(self.canvas2)

        self.bottom_layout.addWidget(self.left_widget)
        self.bottom_layout.addWidget(self.right_widget)

        self.layout.addWidget(self.top_widget,8)
        self.layout.addWidget(self.bottom_widget,2)
        self.var = self.slider.value()
        self.var2 = self.slider2.value()
        self.var3 =0
        self.var4 =0
        self.var7 =0
        self.var8 =0
        
        # 添加 tab
        tab_widget.addTab(self.frame1, "回測技術分析")

    def get_strategies_from_table(self):
        strategies_list = []
        for row in range(self.strategy_table.rowCount()):
            strategy_item = self.strategy_table.item(row, 0)  # 假设策略名称在第一列
            if strategy_item is not None:
                strategies_list.append(strategy_item.text())
          
        return strategies_list

    def gen(self):
        # 設定參數
        N_INTERVALS = 10  # 區間數量
        POPULATION_SIZE = 100  # 族群大小
        MUTATION_RATE = 0.5  # 突變率
        GENERATIONS = 500  # 迭代代數
        print(self.get_strategies_from_table())
    
        star = 100000  # 初始金額無變動
        price = 100000  # 變動初始金額
        ex_handle = 20  # 一次股數上限
        self.model = "gen"
        data_param = [star,price,ex_handle,self.buy_list,self.sell_list,self.data_list,self.data_list2,self.data_list3,self.start,self.end,
                        self.str_tmp,self.ope,self.close,self.high,self.low,self.vol,self.date,self.date_ex,self.now_stock,self.model]
        # 假設的歷史資料區間
        # historical_days = 200

        # 假設的歷史資料收益率
        # historical_returns = np.random.normal(0, 0.01, historical_days).tolist()
        # strategies = ['Strategy1', 'Strategy2', 'Strategy3']
        strategies = ['Arron' ,'Rsi' ,'BBand']
        # self.get_strategies_from_table() 
        # 執行基因演算法
        
        best_strategy_found = gen.genetic_algorithm(N_INTERVALS, POPULATION_SIZE, MUTATION_RATE, GENERATIONS,strategies,data_param)

        print("\nBest strategy found:")
        for gene in best_strategy_found:
            print(gene)
    
    def setup_frame2(self, tab_widget):
        frame2 = QWidget()
        layout = QGridLayout(frame2)

        # ... 其他控件 ...

        self.strategy_combobox = QComboBox()
        self.strategy_combobox.addItems(self.strategy )  # 假設的策略列表
        layout.addWidget(self.strategy_combobox, 6, 0)

        self.add_strategy_button = QPushButton('Add Strategy To Table')
        self.add_strategy_button.clicked.connect(self.add_strategy_to_table)
        self.add_gen_button = QPushButton('gen')
        self.add_gen_button.clicked.connect(self.gen)
        layout.addWidget(self.add_strategy_button, 7, 0)
        layout.addWidget(self.add_gen_button, 7, 1)

        self.strategy_table = QTableWidget(0, 2)  # 調整為兩列，包括策略和刪除按鈕
        self.strategy_table.setHorizontalHeaderLabels(['Strategy', 'Delete'])
        layout.addWidget(self.strategy_table, 8, 0, 1, 3)

        tab_widget.addTab(frame2, "genetic algorithm")

    def add_strategy_to_table(self):
        current_strategy = self.strategy_combobox.currentText()

        # 檢查策略是否已經在表格中
        for row_index in range(self.strategy_table.rowCount()):
            if self.strategy_table.item(row_index, 0).text() == current_strategy:
                QMessageBox.warning(self, 'Warning', f'Strategy "{current_strategy}" is already added.')
                return

        # 添加新策略到表格
        row_position = self.strategy_table.rowCount()
        self.strategy_table.insertRow(row_position)
        self.strategy_table.setItem(row_position, 0, QTableWidgetItem(current_strategy))

        # 添加刪除按鈕
        btn_delete = QPushButton('Delete')
        btn_delete.clicked.connect(lambda: self.delete_row(row_position))
        self.strategy_table.setCellWidget(row_position, 1, btn_delete)

    def delete_row(self, row):
        # 確認是否刪除
        reply = QMessageBox.question(self, 'Delete Row', 'Are you sure you want to delete this row?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.strategy_table.removeRow(row)


    def check_data(self,data):
        print("is_trend_steady",popmoder.is_trend_steady(data))  # Volatile
        print("is_trend_increasing",popmoder.is_trend_increasing(data))  # True
        print("is_trend_decreasing",popmoder.is_trend_decreasing(data))  # False
        res = popmoder.cox_stuart(data, True)
        print(res)
        

    def read_local_file(self,file):
        path_str=file
        print(file)
        if(path_str == ""):
            return 
        #收盤
        with open(path_str,'r',encoding="utf_8_sig") as c:
            reader=csv.DictReader(c)
            c=[row["收盤"] for row in reader] #要導入的列
        #開盤
        with open(path_str,'r',encoding="utf_8_sig") as o:
            reader=csv.DictReader(o)
            o=[row["開盤"] for row in reader] #要導入的列 
        
        #最高
        with open(path_str,'r',encoding="utf_8_sig") as h:
            reader=csv.DictReader(h)
            h=[row["最高"] for row in reader] #要導入的列 
        #最低
        with open(path_str,'r',encoding="utf_8_sig") as l:
            reader=csv.DictReader(l)
            l=[row["最低"] for row in reader] #要導入的列     
        #成交量
        with open(path_str,'r',encoding="utf_8_sig") as v:
            reader=csv.DictReader(v)
            v=[row["成交量"] for row in reader] #要導入的列     
        #日期
        with open(path_str,'r',encoding="utf_8_sig") as d:
            reader=csv.DictReader(d)
            d=[row["日期"] for row in reader] #要導入的列 
        ope = [float(x) for x in o]
        close = [float(x) for x in c]
        high = [float(x) for x in h]
        low = [float(x) for x in l]
        vol = [float(x) for x in v]
        date =d
        return date,ope,high,low,close,vol

    def get_historical_data(self,name, number_of_days):
        global catch_stockgarbage
        # global folderpath
        self.local =1
        max_bb=0
        data = []
        orgdate=[]
        local_date=[]
        local_ope=[]
        local_high=[]
        local_low=[]
        local_close=[]
        local_vol=[]
    
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y")
        req_date = pd.to_datetime(current_time) - pd.DateOffset(days=number_of_days)
        req_date=req_date.strftime("%d/%m/%Y")


        start_date  =int( datetime.strptime( str(req_date),"%d/%m/%Y" ).timestamp() ) 
        last_date =int( datetime.strptime( str(current_time),"%d/%m/%Y" ).timestamp() ) 
        
        # url = "https://finance.yahoo.com/quote/" + name + "/history?"+'period1='+str(1517184000)+ '&period2=' + str(1674950400)+ '&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
        # https://query1.finance.yahoo.com/v7/finance/download/1234.TW?period1=1517184000&period2=1674950400&interval=1d&events=history&includeAdjustedClose=true
        # url = "https://finance.yahoo.com/quote/" + name + "/history/"
        # print(url)
        headers = {"User-Agent":"Mozilla/5.0"}
        try:

            # local
            if(self.local ==1) :
                local_date,local_ope,local_high,local_low,local_close,local_vol =self.read_local_file(f'./{self.folderpath}/{name}.csv')
            else:
                # online
                CSV_URL = "https://query1.finance.yahoo.com/v7/finance/download/" + name + "?"+'period1='+str(start_date)+ '&period2=' + str(last_date)+ '&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
                download = requests.get(CSV_URL, headers=headers)
                if download.status_code != 200:
                    name=name.replace(".TW", ".TWO") 
                    CSV_URL = "https://query1.finance.yahoo.com/v7/finance/download/" + name + "?"+'period1='+str(start_date)+ '&period2=' + str(last_date)+ '&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
                    download = requests.get(CSV_URL, headers=headers)
                    print(str(name))
                    print(str(download))
                    if download.status_code == 404:
                        return 0
                # CSV_URL = 'https://query1.finance.yahoo.com/v7/finance/download/1234.TW?period1=1517184000&period2=1674950400&interval=1d&events=history&includeAdjustedClose=true'
                lines = download.text.splitlines()
                # Parse as CSV object
                reader = csv.reader(lines)
                # View Result
                first = 0
                for row in reader:
                    if(first == 0):
                        first =1
                        continue
                    orgdate.append(row[0])
                    t = str(row[0]).replace('/','-')
                    date_process = (dates.date2num(datetime.strptime(t, '%Y-%m-%d')))
                    date.append(float(date_process))
                    ope.append(float(row[1]))
                    high.append(float(row[2]))
                    low.append(float(row[3]))
                    close.append(float(row[4]))
                    vol.append(float(row[6]))
                    
                    local_date.append(row[0])
                    local_ope.append(float(row[1]))
                    local_high.append(float(row[2]))
                    local_low.append(float(row[3]))
                    local_close.append(float(row[4]))
                    local_vol.append(float(row[6]))

            #篩選指標
            if(self.local ==0) :
                if(len(date)<= 0 or len(orgdate) <=0):
                    return 0
                # sleep(random.randint(0, 6))
                stock_dict = {"日期": local_date,"開盤": local_ope,"最高": local_high,"最低": local_low,"收盤": local_close,"成交量":local_vol}
                # print(stock_dict)
                stock_dataframe = pd.DataFrame(stock_dict)
                stock_dataframe.to_csv('./'+folderpath+'/'+name+'.csv',encoding = 'utf_8_sig', index=False)

            BBand=popmoder.get_BBand(np.asarray(local_close))
            BBand_up=[float(x) for x in BBand  [0]]
            BBand_sma=[float(x) for x in BBand  [1]]
            BBand_down=[float(x) for x in BBand  [2]]

            BBand_mid=[]
            BBand_width=[]
            for x in range(0,len(BBand_sma),1):
                BBand_mid.append((BBand_up[x]+BBand_down[x])/2)

            for x in range(0,len(BBand_mid),1):
                BBand_width.append(100*((BBand_up[x]-BBand_down[x])/BBand_mid[x]))

            max_vol=max(local_vol[-10:])
            print(max_vol)
            print("walk")
            if(max_vol>150000): #成交量大於150000 
                max_bb=max(BBand_width[20:])
            else :
                max_bb=0
              
            rsi = popmoder.get_RSI(np.asarray(local_close))
            atr=  popmoder.get_ATR(np.asarray(local_high),np.asarray(local_low),np.asarray(local_close))
            natr= popmoder.get_NATR(np.asarray(local_high),np.asarray(local_low),np.asarray(local_close))
            kdj = popmoder.get_KDJ(np.asarray(local_high),np.asarray(local_low),np.asarray(local_close))
            print ('stock name')   
            print(name)
            print("Current Time =", current_time)
            print("Back Time =", req_date)
            print ('----------')
            if(max_bb==0) :
                print("交易量沒有超過預設值=",150000)
            else:
                print ("max_bb = ",max_bb)
                print ("max_vol =",max_vol)
                print ("RSI  =",rsi[len(rsi)-30:])
                self.check_data(rsi[len(rsi)-30:])
                print ("ATR  =",atr[len(atr)-30:])
                print ("ATR MAX-MIN =",max(atr[len(atr)-30:])-min(atr[len(atr)-30:]))
                if(max(atr[len(atr)-30:])-min(atr[len(atr)-30:]) >=1):
                    print ("股價波動")
                self.check_data(atr[len(atr)-30:])
                print ("NATR  =",natr[len(natr)-30:])
                self.check_data(natr[len(natr)-30:])
                print ("KDJ  =",kdj['j'][len(kdj['k'])-30:])
                self.check_data(kdj['k'][len(kdj['k'])-30:])
            print ('----------')
        except  Exception as e:
            print(e)
            # global catch_stockgarbage
            # print ('找不到所選資料,或發生異常錯誤.')
            max_bb=0
            self.catch_stockgarbage.append(name)
        return  max_bb
    def job(self, num):
        stock_code = f"{num}.TW"
        max_bb = self.get_historical_data(stock_code, 365 * 5)
        if max_bb > 20:
            self.catch_stock.append(str(stock_code)+"|"+ str(max_bb))
            print("detct target stock name:", stock_code,max_bb)

    def call_download(self):
        global catch_stock
        global catch_stockgarbage
        self.catch_stock=[]
        self.catch_stockgarbage=[]

        self.tree_widget.clear()
        print( self.var9.text() )
        print( self.var10.text() )
        start_code = int(self.var9.text())
        end_code = int(self.var10.text())
        #近三個月 bb寬度篩選
        # 建立 5 個子執行緒
        threads = []
        for x in range(start_code, end_code, 1):
            # for i in range(25):
            #     num = x+i
            thread = threading.Thread(target=self.job, args=(x,))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
         
        for thread in threads:
            thread.join()
        threads.clear()
     

        print("Done.")
        print ('----------')
        print ('捕捉BBAND寬度>20股票')      


        for x in range(0,len(self.catch_stock),1):
            tree_item = QTreeWidgetItem(self.tree_widget)
            tree_item.setText(0,str(self.catch_stock[x].split("|")[0]))
            tree_item.setText(1, str(self.catch_stock[x].split("|")[1]))
     

        print("catch")
        print (self.catch_stock)
        print("garbage")
        print (self.catch_stockgarbage)

    def setup_frame7(self, tab_widget):
        frame7 = QWidget()
        main_layout = QVBoxLayout(frame7)  # 主布局改为垂直布局

        # 设置树形视图
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(['股票代號', 'BBand值'])
        self.tree_widget.setColumnWidth(0, 200)
        self.tree_widget.setColumnWidth(1, 200)
        main_layout.addWidget(self.tree_widget)

        # 创建第一行布局：输入框和标签
        row1_layout = QHBoxLayout()
        self.var9 = QLineEdit('1200', self)
        self.var10 = QLineEdit('1220', self)
        lbl3 = QLabel("起始範圍", self)
        lbl4 = QLabel("結束範圍", self)
        row1_layout.addWidget(lbl3)
        row1_layout.addWidget(self.var9)
        row1_layout.addWidget(lbl4)
        row1_layout.addWidget(self.var10)
        main_layout.addLayout(row1_layout)

        # 创建第二行布局：操作按钮
        row2_layout = QHBoxLayout()
        self.btn1 = QPushButton('篩選', self)
        self.btn1.clicked.connect(self.call_download)
        btn2 = QPushButton('取得財務報表', self)
        row2_layout.addWidget(self.btn1)
        row2_layout.addWidget(btn2)
        main_layout.addLayout(row2_layout)

        # 将整个布局添加到tab中
        tab_widget.addTab(frame7, "快篩微調")

    def setup_frame8(self, tab_widget):
        frame8 = QWidget()
        layout = QGridLayout()
        frame8.setLayout(layout)

        btn1 = QPushButton('呼叫lstm', self)
        layout.addWidget(btn1, 1, 4, 1, 2)

        tab_widget.addTab(frame8, "機器學習微調")


    def show_info(self):
        # Implement show_info logic here
        pass

    # def show_fbpropht(self):
    #     # Implement show_fbpropht logic here
    #     pass

    def data_deal(self):
        # Implement data_deal logic here
        pass

def main():
    app = QApplication(sys.argv)
    window = StockAnalysisApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
