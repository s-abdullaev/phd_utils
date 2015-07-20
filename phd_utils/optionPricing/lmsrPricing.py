class LmsrPricing(object):
  def __init__(self, portfolio=[]):
    self.portfolio=portfolio
    self.rangeOfEvents=range(50,150,5)
    self.b=100.0
    self.writer=pd.ExcelWriter('lmsr_results_b100.xlsx')

  def putToPortfolio(self, opt):
    self.portfolio.append(opt);

  def payoff(self, portfolio=None):
    if portfolio==None: portfolio=self.portfolio

    payoffs={}
    for St in self.rangeOfEvents:
      payoffs[St]=0
      for opt in portfolio:
        payoffs[St]+=opt.payoff(St)

    return payoffs

  def lmsr(self, payoffs):
    vals=np.array(payoffs.values())
    return self.b * log(sum(np.exp(vals/self.b)))

  def price(self, opt):
    tempPort=self.portfolio[:]
    tempPort.append(opt)

    tempPayoffs=self.payoff(tempPort)
    return self.lmsr(tempPayoffs)-self.lmsr(self.payoff())

  def optionChain(self):
    d={'Strikes': range(50,151,5),'BLSCall':[], 'BLSPut':[], 'CallBids': [], 'CallAsks': [], 'PutBids':[], 'PutAsks': []}
    BidOpts=[OptionContract(k, True) for k in d['Strikes']]
    AskOpts=[OptionContract(k, False) for k in d['Strikes']]

    for opt in BidOpts: d['BLSCall'].append(opt.blsCall())
    for opt in BidOpts: d['BLSPut'].append(opt.blsPut())
    for opt in BidOpts: d['CallAsks'].append(abs(self.price(opt)))
    for opt in AskOpts: d['CallBids'].append(abs(self.price(opt)))
    for opt in BidOpts: d['PutAsks'].append(max(abs(self.price(opt))+opt.discK()-opt.S0,0))
    for opt in AskOpts: d['PutBids'].append(max(abs(self.price(opt))+opt.discK()-opt.S0,0))

    return pd.DataFrame(d)

  def saveOptionChain(self, sheetname):
    df=self.optionChain()
    df.to_excel(self.writer, sheetname,'','%.2f')
    print 'saved to sheet %s' % sheetname
    self.makePlot(sheetname, df)
    print 'created figure %s' % sheetname

  def makePlot(self, name, df):
    yticks = np.arange(0, 60, 5)
    xticks = np.arange(50,150,25)
    #fig.subplots_adjust(bottom=0.2)
    # quotes=[(x[0], x[1], x[2], x[1], x[2]) for x in df[['Strikes', 'CallAsks', 'CallBids']].values]

    plt.figure(num=None, figsize=(12, 5))
    ax=plt.subplot(1,2,1)
    # candlestick_ohlc(ax, quotes, width=0.6)
    # ax.autoscale_view()
    plt.plot(df['Strikes'].values, df['BLSCall'].values,'b-', label="Black-Schole Price")
    plt.plot(df['Strikes'].values, df['CallAsks'].values,'r--', label="Ask", linewidth=1)
    plt.plot(df['Strikes'].values, df['CallBids'].values,'g--', label="Bid", linewidth=1)

    legend = ax.legend(loc='upper right', shadow=True)
    plt.xlabel('Strikes')
    plt.ylabel('Call Prices')
    plt.xlim(50,150)
    plt.ylim(0,60)
    plt.grid(True)

    ax=plt.subplot(1,2,2)
    # candlestick_ohlc(ax, quotes, width=0.6)
    # ax.autoscale_view()
    plt.plot(df['Strikes'].values, df['BLSPut'].values,'b-', label="Black-Schole Price")
    plt.plot(df['Strikes'].values, df['PutAsks'].values,'r--', label="Ask", linewidth=1)
    plt.plot(df['Strikes'].values, df['PutBids'].values,'g--', label="Bid", linewidth=1)

    plt.xlabel('Strikes')
    plt.ylabel('Put Prices')
    plt.xlim(50,150)
    plt.ylim(0,60)
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(name, dpi=300)
    plt.close('all')

  def flushWriter(self):
    self.writer.save()
