import math
import os
import random
import pandas as pd
import numpy as np
import pickle
import finplot as fplt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# region Pathing
path_win = "fill"
path_mac = "fill"

if os.name == 'nt':
    path = path_win
else:
    path = path_mac
# endregion

# region Instrument data
duration = 86400 * 3

df_results = pd.read_csv(path + "results.csv", index_col=0)
#print(df_results.win.sum())
df_1m = pd.read_csv(path + "binance_futures_BTCUSDT_1m.csv").set_index(['time']).drop('volume', axis=1)
df_5m = pd.read_csv(path + "binance_futures_BTCUSDT_5m.csv").set_index(['time']).drop('volume', axis=1)
df_15m = pd.read_csv(path + "binance_futures_BTCUSDT_15m.csv").set_index(['time']).drop('volume', axis=1)
df_30m = pd.read_csv(path + "binance_futures_BTCUSDT_30m.csv").set_index(['time']).drop('volume', axis=1)
df_1h = pd.read_csv(path + "binance_futures_BTCUSDT_1h.csv").set_index(['time']).drop('volume', axis=1)
df_2h = pd.read_csv(path + "binance_futures_BTCUSDT_2h.csv").set_index(['time']).drop('volume', axis=1)
df_4h = pd.read_csv(path + "binance_futures_BTCUSDT_4h.csv").set_index(['time']).drop('volume', axis=1)

initial_date = 1568246400  # Thursday, 12 September 2019 00:00:00
final_date = 1688947200  # Monday, 10 July 2023 00:00:00


def obfuscation(row, y):
    """Not going for a strong obfuscation, personally. Obfuscation chances each time we open the program, nevertheless."""
    row['high'] = row['high'] * y
    row['low'] = row['low'] * y
    row['open'] = row['open'] * y
    row['close'] = row['close'] * y


# endregion

# region Memory control - Get cycles.
n_cycle = 0
obfuscation_time = random.randint(-568024668, 568024668)//86400*86400  # -18/+18 years, start of the day adjusted - probably not needed
obfuscation_price = round(random.uniform(4.001, 7.9995), 3)

with open(path + "trading_cycles_3d", 'rb') as file:
    total = pickle.load(file)
    print('Total cycle size: ', len(total), total)

with open(path + "progress_cycles_3d", 'rb') as file:
    progress = pickle.load(file)
    print('Progress size: ', len(progress), progress)

cycles = [x for x in total if x not in progress]
if len(cycles) == 0:
    print('Insane patience. All cycles done.')
# endregion

# region PyQt6 setup and Finplot initialization.

app = QApplication([])
win = QGraphicsView()
win.setWindowTitle('Vertex')
win.setWindowIcon(QIcon(path + 'buttons/logo.png'))
win.setStyleSheet("""
            QWidget {
                background-color: #242320;
                border-top: 1px solid white;
                border-left: 1px solid white;
                font-size: 15px;
                color: white;
            }
            QComboBox {
                background-color: #F3F6F4;
                color: #242320;
            }
            QPushButton {
                background-color: #F3F6F4;
                color: #242320;  
            }""")

layout = QGridLayout()
win.setLayout(layout)
win.resize(1500, 800)

# region Icons creation
right_icon = QIcon(QPixmap(path + 'buttons/next.png').scaled(33, 33))
done_icon = QIcon(QPixmap(path + 'buttons/done.png').scaled(33, 33))
cancel_icon = QIcon(QPixmap(path + 'buttons/cancel.png').scaled(33, 33))
lc_icon = QIcon(QPixmap(path + 'buttons/low_confidence.png').scaled(33, 33))
tp_icon = QIcon(QPixmap(path + 'buttons/take_profit.png').scaled(33, 33))
sl_icon = QIcon(QPixmap(path + 'buttons/stop_loss.png').scaled(34, 34))
# endregion

combo = QComboBox()
combo.setEditable(False)
combo.addItems(['1m', '5m', '15m', '30m', '1h', '2h', '4h'])
cases = {"1m": df_1m, "5m": df_5m, '15m': df_15m, '30m': df_30m,
         '1h': df_1h, '2h': df_2h, '4h': df_4h}

right_button = QPushButton(right_icon, '')
done_button = QPushButton(done_icon, '')

# region Basic buttons -> buy_high_button, sell_high_button...
buy_high_button = QPushButton('High')
buy_low_button = QPushButton('Low')
buy_open_button = QPushButton('Open')
buy_close_button = QPushButton('Close')
sell_close_button = QPushButton('Close')
sell_open_button = QPushButton('Open')
sell_low_button = QPushButton('Low')
sell_high_button = QPushButton('High')
buy_high_button.setStyleSheet("""background-color: #8db290""")
buy_low_button.setStyleSheet("""background-color: #8db290""")
buy_open_button.setStyleSheet("""background-color: #8db290""")
buy_close_button.setStyleSheet("""background-color: #8db290""")
sell_close_button.setStyleSheet("""background-color: #dd655f""")
sell_open_button.setStyleSheet("""background-color: #dd655f""")
sell_low_button.setStyleSheet("""background-color: #dd655f""")
sell_high_button.setStyleSheet("""background-color: #dd655f""")
# endregion

plays_combo = QComboBox()
plays_combo.setEditable(False)
cancel_order_button = QPushButton(cancel_icon, '')
cancel_order_button.setFixedHeight(23)
tp_button = QPushButton(tp_icon, '')
tp_button.setFixedHeight(23)
sl_button = QPushButton(sl_icon, '')
sl_button.setFixedHeight(23)
lc_button = QPushButton(lc_icon, '')
lc_button.setFixedHeight(23)
finished_label = QLabel(str(len(df_results)))

# region Add widgets to layout
layout.addWidget(done_button, 0, 0, 1, 1)
layout.addWidget(buy_high_button, 0, 2, 1, 1)
layout.addWidget(buy_low_button, 0, 3, 1, 1)
layout.addWidget(buy_open_button, 0, 4, 1, 1)
layout.addWidget(buy_close_button, 0, 5, 1, 1)
layout.addWidget(right_button, 0, 7, 1, 1)
layout.addWidget(sell_close_button, 0, 9, 1, 1)
layout.addWidget(sell_open_button, 0, 10, 1, 1)
layout.addWidget(sell_low_button, 0, 11, 1, 1)
layout.addWidget(sell_high_button, 0, 12, 1, 1)
layout.addWidget(combo, 0, 14, 1, 1)

layout.addWidget(cancel_order_button, 2, 4, 1, 1)
layout.addWidget(lc_button, 2, 5, 1, 1)
layout.addWidget(plays_combo, 2, 6, 1, 3)
layout.addWidget(tp_button, 2, 9, 1, 1)
layout.addWidget(sl_button, 2, 10, 1, 1)
layout.addWidget(finished_label, 2, 14, 1, 1)

player = QMediaPlayer()
audio_output = QAudioOutput()
player.setAudioOutput(audio_output)
player.setSource(QUrl.fromLocalFile(path + 'buttons/light.mp3'))
audio_output.setVolume(69)
# endregion

"""Finplot color scheme and initialization."""
w = fplt.foreground = '#eef'
b = fplt.background = fplt.odd_plot_background = '#242320'
fplt.candle_bull_color = fplt.volume_bull_color = fplt.candle_bull_body_color = fplt.volume_bull_body_color = '#f3f6f4'
fplt.candle_bear_color = fplt.volume_bear_color = fplt.candle_bear_body_color = fplt.volume_bear_body_color = '#1493ff'
fplt.cross_hair_color = w + 'a'
ax = fplt.create_plot()

win.axs = [ax]  # finplot requires this property
axo = ax.overlay()
layout.addWidget(ax.vb.win, 1, 0, 1, 15)
# endregion

sliced = pd.DataFrame()
orders_df = pd.DataFrame(columns=['id', 'date', 'direction', 'entry', 'ln_entry', 'tp', 'ln_tp', 'sl', 'ln_sl', 'lc', 'filled'])  # reset
order_date = 0  # no need to reset
order_id = 0  # not reset
t1 = 0  # no need to reset
t2 = 43200  # 12h data display at the start of a session. reset
t_shown_max = 0
relative_to_15m = {}
t_max = 0  # no need to reset


def update(tf):
    global sliced
    global t_max
    global t1
    global t_shown_max
    global relative_to_15m
    global orders_df

    orders_df=orders_df.apply(save_polylines, axis=1)
    ax.reset()  # remove previous plots
    axo.reset()  # remove previous plots
    combo.setCurrentText(tf)  # specific for 15min first update load

    """Display the chart related to the cycle initial timestamp."""
    sliced = cases[tf].loc[cycles[n_cycle]:cycles[n_cycle] + duration].copy()  # no problem repeating this section
    sliced.index = sliced.index + obfuscation_time
    sliced.apply(obfuscation, axis=1, args=[obfuscation_price])
    t1 = sliced.index[0]
    t_max = sliced.index[-1]
    t_shown_max = t1 + t2

    relative_to_15m = {'1m': (t1 + t2 + 840) // 60 * 60, '5m': (t1 + t2 + 600) // 300 * 300, '15m': t1 + t2,
                       '30m': (t1 + t2 - 900) // 1800 * 1800,
                       '1h': (t1 + t2 - 900 * 3) // 3600 * 3600, '2h': (t1 + t2 - 900 * 3 - 900 * 4) // 7200 * 7200,
                       '4h': (t1 + t2 - 900 * 3 - 900 * 4 * 3) // 14400 * 14400}  # loc is inclusive
    shown = sliced.loc[t1:relative_to_15m[tf]]

    fplt.candlestick_ochl(shown[['open', 'close', 'high', 'low']])
    fplt.refresh()  # refresh autoscaling when all plots complete

    """Controls line updates of current orders."""
    if plays_combo.count() > 0:
        for index, row in orders_df.iterrows():
            py = row['entry']
            p1x = row['date']  # already in the correct units (no need to multiply), as it originates from candle double click.
            p2x = relative_to_15m[tf] * (10 ** 9)  # current ax max shown time.
            if p1x < p2x:  # to handle a bug regarding drawing in times that don't yet exist on upper timeframes.
                p1x, p2x = fplt._pdtime2index(ax, pd.Series([p1x, p2x]))  # transform into ordinal units as you can't update a line with dates.
                row['ln_entry'].points = ((p1x, py), (p2x, py))


def move():
    global t2
    x = t2 + 900
    if t1 + x < t_max:
        t2 = x
        update(combo.currentText())
        check_playout()
    else:
        print("Session done.")


def listener(event: QKeyEvent):
    if event.text() == '1':
        combo.setCurrentText('15m')
    elif event.text() == '2':
        combo.setCurrentText('1h')
    elif event.text() == '3':
        combo.setCurrentText('4h')
    elif event.text() == '4':
        combo.setCurrentText('1m')


def candle_info(x, y):
    global order_date
    """ Retrieve candle information that is selected by double click.
        Gets current timeframe df and uses temporal location of the candle's row."""
    row = sliced.loc[sliced.index == x/(10 ** 9)]
    order_date = x
    h = row['high'].item()
    l = row['low'].item()
    o = row['open'].item()
    c = row['close'].item()

    buy_high_button.setText("H-" + str(round(h)))
    buy_low_button.setText("L-" + str(round(l)))
    buy_open_button.setText("O-" + str(round(o)))
    buy_close_button.setText("C-" + str(round(c)))
    sell_close_button.setText("C-" + str(round(c)))
    sell_open_button.setText("O-" + str(round(o)))
    sell_low_button.setText("L-" + str(round(l)))
    sell_high_button.setText("H-" + str(round(h)))


def entry(button):
    """ Retrieves price and direction from clicked button and creates an entry order.
        The order should appear in the plays combo-box below."""
    global orders_df
    global order_id
    latest_time = relative_to_15m[combo.currentText()]
    latest_close = sliced.loc[relative_to_15m[combo.currentText()]]['close']

    if 'o' in button.text() or 'n' in button.text() or 'i' in button.text():
        print('No candle selected.')
    else:
        price = button.text()[2:]
        palette = button.palette()
        color = palette.color(button.backgroundRole()).name()
        if color == '#8db290' and latest_close > int(price):
            ln = fplt.add_line((order_date, int(price)*1.0001), (latest_time * (10 ** 9), int(price)*1.0001), color='#8db290', interactive=False)
            orders_df.loc[len(orders_df)] = [order_id, order_date, 'long', int(price)*1.0001, ln, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
            plays_combo.addItems([str(order_id) + ' - Long order - ' + str(int(price)*1.0001)])
            plays_combo.setCurrentIndex(plays_combo.count() - 1)
        elif color != '#8db290' and latest_close < int(price):
            ln = fplt.add_line((order_date, int(price)*0.9999), (latest_time * (10 ** 9), int(price)*0.9999), color='#dd655f', interactive=False)
            orders_df.loc[len(orders_df)] = [order_id, order_date, 'short', int(price)*0.9999, ln, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
            plays_combo.addItems([str(order_id) + ' - Short order - ' + str(int(price)*0.9999)])
            plays_combo.setCurrentIndex(plays_combo.count() - 1)
        else:
            print('Error: Long order above current price | Short order below current price.')
        order_id += 1


def entry_modifier(button):
    global orders_df
    if plays_combo.count() == 0:
        return
    """ Deals with all the buttons that are on the lower row: Take-profit, Stop-loss, Low-Confidence, Cancel order."""
    current_id = int(plays_combo.currentText().split("-")[0])
    orders_df.loc[orders_df['id'] == current_id] = orders_df.loc[orders_df['id'] == current_id].apply(save_polylines, axis=1)

    row = orders_df[orders_df['id'] == current_id]
    price = row['entry'].item()
    date = row['date'].item()
    side = row['direction'].item()
    tp = row['tp'].item()
    sl = row['sl'].item()
    lc = row['lc'].item()
    lines = [row['ln_entry'].item(), row['ln_tp'].item(), row['ln_sl'].item()]
    specs = {'long': [1.001, 0.999], 'short': [0.999, 1.001]}

    if button == "TP":
        if np.isnan(tp):
            ln = fplt.add_line((date, price), (relative_to_15m[combo.currentText()] * (10 ** 9), price * specs[side][0]),
                               style='.', color='#8db290', interactive=True)
            orders_df.loc[orders_df['id'] == current_id, 'ln_tp'] = ln
        else:
            """If you only knew how bad things really are. remove line; add line; change in orders_df."""
            fplt.remove_primitive(lines[1])
            ln = fplt.add_line((date, price), (relative_to_15m[combo.currentText()] * (10 ** 9), tp),
                               style='.', color='#8db290', interactive=True)
            orders_df.loc[orders_df['id'] == current_id, 'ln_tp'] = ln

    elif button == "SL":
        if np.isnan(sl):
            ln = fplt.add_line((date, price), (relative_to_15m[combo.currentText()] * (10 ** 9), price * specs[side][1]),
                               style='.', color='#dd655f', interactive=True)
            orders_df.loc[orders_df['id'] == current_id, 'ln_sl'] = ln
        else:
            """If you only knew how bad things really are. remove line; add line; change in orders_df."""
            fplt.remove_primitive(lines[2])
            ln = fplt.add_line((date, price), (relative_to_15m[combo.currentText()] * (10 ** 9), sl),
                               style='.', color='#dd655f', interactive=True)
            orders_df.loc[orders_df['id'] == current_id, 'ln_sl'] = ln

    elif button == "LC":
        if lc == 1:
            orders_df.loc[orders_df['id'] == current_id, 'lc'] = 0
            text = plays_combo.currentText().split("-")[0] + '-' + plays_combo.currentText().split("-")[1] + '-' + \
                   str(float(plays_combo.currentText().split("-")[2]))  # peak programming (str-int-str) to stop blank space building on LC clicks
            plays_combo.setItemText(plays_combo.currentIndex(), text)
        else:
            orders_df.loc[orders_df['id'] == current_id, 'lc'] = 1
            text = plays_combo.currentText() + ' - LC'
            plays_combo.setItemText(plays_combo.currentIndex(), text)

    else:  # cancel order button
        for ln in lines:
            if str(ln) != 'nan':
                fplt.remove_primitive(ln)
        orders_df = orders_df.drop(orders_df[orders_df['id'] == current_id].index).reset_index(drop=True)
        plays_combo.removeItem(plays_combo.currentIndex())


def save_polylines(row):
    """Saves the polylines information - tp and sl - IF they exist and WHEN they have been moved/changed."""
    if str(row['ln_tp']) != 'nan':
        if len(row['ln_tp'].texts)>0:  # addition for update()
            p2 = str(row['ln_tp'].texts[0].segment.handles[1]['pos'])
            start = p2.find('(')
            end = p2.find(')')
            p2y = [float(x) for x in p2[start + 1: end].split(',')][1]
            row['tp'] = p2y

    if str(row['ln_sl']) != 'nan':
        if len(row['ln_sl'].texts) > 0:
            p2 = str(row['ln_sl'].texts[0].segment.handles[1]['pos'])
            start = p2.find('(')
            end = p2.find(')')
            p2y = [float(x) for x in p2[start + 1: end].split(',')][1]
            row['sl'] = p2y
    return row


def update_play():
    """ Retrieves and displays information on the play that is selected at the moment or last play selected on the lower end combobox."""
    global orders_df
    if plays_combo.count() == 0:
        return
    current_id = int(plays_combo.currentText().split("-")[0])

    def set_pen(row):
        color = '#8db290' if row['direction'] == 'long' else '#dd655f'
        width = 2 if row['id'] == current_id else 1
        row['ln_entry'].pen = fplt._makepen(color=color, width=width)

    orders_df.apply(set_pen, axis=1)
    fplt.refresh()


def check_playout():
    """Checks if the new candle that represents the present triggers any order. If it does, calls playout()."""
    candle = df_15m[df_15m.index == t_shown_max-obfuscation_time]
    low = candle['low'].item()*obfuscation_price
    high = candle['high'].item()*obfuscation_price
    for index, row in orders_df.iterrows():
        if np.isnan(row['filled']):
            if row['direction'] == 'long':
                if low <= row['entry']:
                    player.play()
                    playout(row, 1)
            else:
                if high >= row['entry']:
                    player.play()
                    playout(row, 1)
        else:
            playout(row)


def playout(row, just_filled=0):
    global orders_df
    df_playout = df_1m.loc[t_shown_max-obfuscation_time:t_shown_max-obfuscation_time + 840].copy()  # just pointing is a bad idea
    df_playout.apply(obfuscation, axis=1, args=[obfuscation_price])
    date = row['date']
    direction = row['direction']
    entry_price = row['entry']
    tp = row['tp']
    sl = row['sl']
    lc = row['lc']
    lines = [row['ln_entry'], row['ln_tp'], row['ln_sl']]
    """Redirect attention."""
    plays = plays_combo.count()
    plays_text = [[int(plays_combo.itemText(index).split("-")[0]), index] for index in range(plays)]
    for x in plays_text:
        if x[0] == row['id']:
            plays_combo.setCurrentIndex(x[1])
            tp_button.click()  # Save polylines twice with no change on TP/SL values. Just visual.
            sl_button.click()  # Unless no tp&sl - saves tp only but no one cares cause next candle would save them on update().

    for i, flux in df_playout.iterrows():
        check_tp = True
        """First find the actual fill on the minute and ignore prior 1min"""
        if just_filled == 1:
            if row['filled']!=1 and ((direction == 'long' and flux['low'] <= entry_price) or (direction == 'short' and flux['high'] >= entry_price)):
                row['filled'] = 1  # this changes this temporary row copy, not in orders_df
                orders_df.loc[orders_df['id']==row['id'], 'filled'] = 1
                check_tp=False
        """When filled, check every 1min candle."""
        if row['filled'] == 1:
            r = check_1m_playout(flux, tp, sl, direction, check_tp)
            if r == 'sl':
                df_results.loc[len(df_results)] = [date/(10 ** 9)-obfuscation_time, direction, entry_price/obfuscation_price,
                                                   tp/obfuscation_price, sl/obfuscation_price, lc, 0]
                """Check entry modifier, equal removal of information: lines, orders_df, plays_combo."""
                for ln in lines:
                    if str(ln) != 'nan':
                        fplt.remove_primitive(ln)
                plays_combo.removeItem(plays_combo.currentIndex())
                orders_df = orders_df.drop(orders_df[orders_df['id'] == row['id']].index).reset_index(drop=True)
                finished_label.setText(str(len(df_results)))
                print('SL', abs((sl/entry_price-1)*100*100))
                break
            elif r == 'tp':
                df_results.loc[len(df_results)] = [date/(10 ** 9)-obfuscation_time, direction, entry_price/obfuscation_price,
                                                   tp/obfuscation_price, sl/obfuscation_price, lc, 1]
                for ln in lines:
                    if str(ln) != 'nan':
                        fplt.remove_primitive(ln)
                plays_combo.removeItem(plays_combo.currentIndex())
                orders_df = orders_df.drop(orders_df[orders_df['id'] == row['id']].index).reset_index(drop=True)
                finished_label.setText(str(len(df_results)))
                print('TP', abs((tp/entry_price-1)*100*100))
                break

            elif r == 'dummy':
                for ln in lines:
                    if str(ln) != 'nan':
                        fplt.remove_primitive(ln)
                plays_combo.removeItem(plays_combo.currentIndex())
                orders_df = orders_df.drop(orders_df[orders_df['id'] == row['id']].index).reset_index(drop=True)
                finished_label.setText(str(len(df_results)))
                print('dummy, forgot apriori SL')
                break


def check_1m_playout(flux, tp, sl, direction, check_tp):
    if np.isnan(sl):  # able to not have a TP
        return 'dummy'
    elif direction=='long':
        if flux['low']<=sl:
            return 'sl'
        elif flux['high']>=tp and check_tp:
            return 'tp'
    else:
        if flux['high']>=sl:
            return 'sl'
        elif flux['low']<=tp and check_tp:
            return 'tp'


def done():
    """Update progress, clear plays combo-box and orders_df, save trades. Advance cycle and update variables."""
    global n_cycle
    global obfuscation_time
    global obfuscation_price
    global t2
    global orders_df

    progress.append(cycles[n_cycle])
    with open(path + "progress_cycles_3d", "wb") as prog:
        pickle.dump(progress, prog)
    print('Progress', progress)
    
    """Remove lines, combo and reset orders_df."""
    orders_df.apply(nuke_lines, axis=1)

    plays_combo.clear()
    orders_df = pd.DataFrame(columns=['id', 'date', 'direction', 'entry', 'ln_entry', 'tp', 'ln_tp', 'sl', 'ln_sl', 'lc', 'filled'])
    df_results.to_csv(path + "results.csv")
    print('Done', len(df_results), df_results['win'])

    n_cycle += 1
    obfuscation_time = random.randint(-568024668, 568024668)//86400*86400  # -18/+18 years adjusted start of day
    obfuscation_price = round(random.uniform(4.001, 7.9995), 3)
    t2 = 43200
    update('15m')


def nuke_lines(row):
    if str(row['ln_tp']) != 'nan':
        fplt.remove_primitive(row['ln_tp'])
    if str(row['ln_sl']) != 'nan':
        fplt.remove_primitive(row['ln_sl'])
    if str(row['ln_entry']) != 'nan':
        fplt.remove_primitive(row['ln_entry'])


# region Logic control
"""Start"""
combo.currentTextChanged.connect(update)
update('15m')
"""Macros"""
QShortcut(Qt.Key.Key_Space, win, autoRepeat=False).activated.connect(right_button.click)
win.keyPressEvent = listener
"""Clicks and button actions"""
fplt.set_time_inspector(candle_info, ax=ax, when='double-click')
right_button.clicked.connect(move)  # next button
buy_high_button.clicked.connect(lambda: entry(buy_high_button))
buy_low_button.clicked.connect(lambda: entry(buy_low_button))
buy_open_button.clicked.connect(lambda: entry(buy_open_button))
buy_close_button.clicked.connect(lambda: entry(buy_close_button))
sell_close_button.clicked.connect(lambda: entry(sell_close_button))
sell_open_button.clicked.connect(lambda: entry(sell_open_button))
sell_low_button.clicked.connect(lambda: entry(sell_low_button))
sell_high_button.clicked.connect(lambda: entry(sell_high_button))
done_button.clicked.connect(done)
"""Bottom actions"""
plays_combo.currentTextChanged.connect(update_play)
cancel_order_button.clicked.connect(lambda: entry_modifier("X"))
lc_button.clicked.connect(lambda: entry_modifier("LC"))
tp_button.clicked.connect(lambda: entry_modifier("TP"))
sl_button.clicked.connect(lambda: entry_modifier("SL"))

# endregion

fplt.show(qt_exec=False)  # prepares plots when they're all setup
win.show()
app.exec()
