from math import pi
from flask import Flask, render_template, request, redirect
import finnhub
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter

app = Flask(__name__)

app.vars={}
app.vars['ticker'] = 'AMD'
app.vars['_from'] = '2020-08-01'
app.vars['to'] = '2020-08-31'
app.vars['features'] = ['c']

@app.route('/')
def start():
    return render_template('index.html')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', ticker='SSS')
    else:
        #request was a POST
        app.vars['ticker'] = request.form['ticker']
        app.vars['_from'] = pd.to_datetime(request.form['_from']).value // 10**9
        app.vars['to'] = pd.to_datetime(request.form['to']).value // 10**9
        # Setup client
        finnhub_client = finnhub.Client(api_key="btgn9uv48v6r5euapsdg")

        df = pd.DataFrame(finnhub_client.stock_candles(app.vars['ticker'],
                                'D', app.vars['_from'] , app.vars['to']))

        df['date'] = pd.to_datetime(df['t'], unit='s')
        df.rename(columns={'o':'open', 'c':'close', 'h':'high', 'l':'low'},
         inplace=True)

        inc = df.close > df.open
        dec = df.open > df.close
        w = 12*60*60*1000 # half day in ms

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        p = figure(x_axis_type="datetime", tools=TOOLS,
         plot_width=1000, title = "{} Candlestick".format(app.vars['ticker']))
        p.grid.grid_line_alpha=0.3

        p.segment(df.date, df.high, df.date, df.low, color="black")
        p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
        p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
        p.xaxis.formatter=DatetimeTickFormatter(days=['%Y/%m/%d'])

        script, div = components(p)
    return render_template('graph.html', script=script, div=div)

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
