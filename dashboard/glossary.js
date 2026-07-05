/* ==========================================================================
   GLOSSARY — plain-English explanations for every metric on the dashboard.
   Written for someone brand-new to markets. No jargon without a definition.

   Each entry:
     term  — the human name
     one   — a single-sentence "what is it"
     what  — what it actually measures, in plain words
     read  — how to read the number / signal you're seeing
     why   — why it matters to YOU as a decision-maker
     scale — (optional) quick reference for typical values

   Used by index.html: every indicator, fundamental, and verdict has an "ⓘ"
   that opens the matching entry. Nothing on the dashboard is a bare number.
   ========================================================================== */
const GLOSSARY = {

  /* ---------- the big picture ---------- */
  verdict: {
    term: "Technical rating (Strong Buy … Strong Sell)",
    one: "A single scorecard that blends ~16 standard indicators into one word.",
    what: "We compute the indicators professional chart-readers use, turn each into a Buy, Sell, or Neutral vote, then tally the votes. More buy votes → a bullish rating; more sell votes → bearish.",
    read: "Strong Buy / Buy = most indicators lean up right now. Neutral = mixed, no clear edge. Sell / Strong Sell = most lean down. It describes the CURRENT technical posture, not a prediction or a recommendation.",
    why: "It's a fast, unemotional read of 'what is the chart saying today' so you don't have to eyeball a dozen indicators yourself. It is one input — pair it with the news and fundamentals below before forming a view.",
    scale: "Score runs -1 (all sell) to +1 (all buy). ≥ +0.5 Strong Buy · +0.15 Buy · middle Neutral · -0.15 Sell · ≤ -0.5 Strong Sell."
  },
  moving_averages_rating: {
    term: "Moving-averages rating",
    one: "The verdict from trend indicators only (the 10 moving averages).",
    what: "Counts how many of the 10 moving averages the price is currently ABOVE (bullish) vs BELOW (bearish).",
    read: "Price above most of its averages = uptrend = bullish tally. Below most = downtrend = bearish tally.",
    why: "Isolates the trend picture from the momentum picture. When this and the oscillator rating disagree, the stock is in transition — worth a closer look."
  },
  oscillators_rating: {
    term: "Oscillators rating",
    one: "The verdict from momentum indicators only (RSI, MACD, Stochastic, etc.).",
    what: "Counts buy vs sell votes across the momentum oscillators — tools that measure speed and stretch rather than trend.",
    read: "Bullish tally = momentum building. Bearish = momentum fading or overextended.",
    why: "Momentum often turns BEFORE the trend does, so this can give an early warning that a trend is tiring."
  },

  /* ---------- momentum oscillators ---------- */
  rsi: {
    term: "RSI — Relative Strength Index (14)",
    one: "A 0–100 speedometer of recent buying vs selling pressure.",
    what: "Compares the size of recent up-days to recent down-days over the last 14 sessions. High = buyers have been dominating; low = sellers have.",
    read: "Above 70 = 'overbought' (risen fast, may be due for a pause/pullback). Below 30 = 'oversold' (fallen fast, may be due for a bounce). 40–60 = neutral.",
    why: "It flags when a move has gone too far, too fast in either direction. Overbought isn't a sell signal by itself — strong stocks can stay overbought for weeks — but it tells you the easy part of the move may be over.",
    scale: "0 ——[30 oversold]—— 50 ——[70 overbought]—— 100"
  },
  macd: {
    term: "MACD — Moving Average Convergence Divergence",
    one: "Measures whether short-term momentum is speeding up or slowing down vs the longer term.",
    what: "Subtracts a 26-day average from a 12-day average (the 'MACD line'), then compares it to its own 9-day average (the 'signal line'). It's the classic trend-momentum tool.",
    read: "MACD line ABOVE its signal line = bullish (momentum improving). BELOW = bearish (momentum deteriorating). A cross from below to above is a common bullish trigger; the reverse is bearish.",
    why: "It catches shifts in momentum early and works in trending markets — one of the most-watched signals on Wall Street, so it can be partly self-fulfilling."
  },
  stochastic: {
    term: "Stochastic %K (14,3)",
    one: "Shows where today's close sits within the recent high-low range.",
    what: "0% = closing at the bottom of the last 14 days' range; 100% = closing at the very top. It measures 'closing strength'.",
    read: "Above 80 = closing near the highs (overbought). Below 20 = closing near the lows (oversold). Turning up from below 20 is an early bounce signal.",
    why: "Great for spotting exhaustion in sideways/range-bound stocks, where price keeps bouncing between a floor and a ceiling."
  },
  cci: {
    term: "CCI — Commodity Channel Index (20)",
    one: "Measures how far price has strayed from its recent average.",
    what: "Zero = price is right at its 20-day average. Big positive/negative readings mean price is unusually far above/below normal.",
    read: "Above +100 = strong up-move (can mean overbought OR the start of a powerful trend). Below -100 = strong down-move. Between = normal.",
    why: "Highlights unusually strong thrusts — useful for catching the start of a breakout or spotting an overstretched move."
  },
  williams_r: {
    term: "Williams %R (14)",
    one: "Another overbought/oversold gauge, scaled from 0 to -100.",
    what: "Like Stochastic upside-down: measures where the close sits in the recent range. -100 = bottom of range, 0 = top.",
    read: "Above -20 = overbought (near recent highs). Below -80 = oversold (near recent lows).",
    why: "A fast, sensitive read on short-term extremes — often used to time entries within a bigger trend."
  },
  momentum: {
    term: "Momentum (10-day)",
    one: "Simply: is the price higher or lower than it was 10 days ago?",
    what: "Today's price minus the price 10 sessions back. Positive = rising over the period; negative = falling.",
    read: "Positive and growing = accelerating uptrend. Negative and falling = accelerating downtrend. Fading toward zero = the move is losing steam.",
    why: "The simplest momentum check there is. 'The trend is your friend' — momentum tells you if the trend still has energy."
  },

  /* ---------- trend / moving averages ---------- */
  moving_average: {
    term: "Moving average (SMA / EMA)",
    one: "The average price over the last N days — a smoothed line that shows the underlying trend.",
    what: "SMA = simple average of the last N closes. EMA = exponential, which weights recent days more so it reacts faster. Common windows: 10/20/50/100/200 days.",
    read: "Price ABOVE the average = bullish for that timeframe; BELOW = bearish. Short averages (10/20) show near-term mood; long ones (200) show the primary trend.",
    why: "Trend is the single biggest driver of returns. A stock above its rising 200-day average is in a healthy long-term uptrend; below a falling 200-day is a long-term downtrend. The averages also often act as support/resistance (see below).",
    scale: "Short-term: 10/20-day · Medium: 50-day · Long-term: 100/200-day"
  },
  sma: {
    term: "SMA — Simple Moving Average",
    one: "The plain average of the last N daily closes.",
    what: "Add up the last N closing prices and divide by N. A steady, slower-moving trend line.",
    read: "Price above the SMA = uptrend for that window; below = downtrend. The 50-day and 200-day SMAs are the most-watched.",
    why: "The 50-day crossing above the 200-day is the famous 'golden cross' (bullish); crossing below is a 'death cross' (bearish). Big funds watch these levels."
  },
  ema: {
    term: "EMA — Exponential Moving Average",
    one: "A moving average that reacts faster because it weights recent days more heavily.",
    what: "Like an SMA but the most recent prices count for more, so it hugs the price more closely and turns sooner.",
    read: "Same as SMA — price above = bullish, below = bearish — but the EMA signals trend changes earlier (and gives more false alarms).",
    why: "Traders use EMAs when they want to react quickly; investors prefer SMAs for a calmer, less twitchy trend read."
  },
  adx: {
    term: "ADX — Average Directional Index (14)",
    one: "Measures how STRONG the trend is — not its direction.",
    what: "A 0–100 reading of trend strength. It says nothing about up or down, only how forceful and sustained the move is.",
    read: "Below 20 = weak / no real trend (choppy, range-bound). 20–25 = a trend is forming. Above 25 = strong trend. Above 40 = very strong.",
    why: "It tells you whether trend-following signals (like moving-average crosses) are trustworthy right now. In a low-ADX chop, breakouts often fail; in high-ADX, trends tend to persist.",
    scale: "0 ——[20 weak]——[25 trending]——[40 strong]—— 100"
  },
  trend: {
    term: "Trend direction",
    one: "Our plain-English label: Uptrend, Downtrend, or Sideways.",
    what: "Derived from where price sits relative to its 50-day and 200-day averages. Above both = Uptrend. Below both = Downtrend. In between = Sideways/transitional.",
    read: "Uptrend = higher highs, buyers in control. Downtrend = lower lows, sellers in control. Sideways = no one in control; range-trading conditions.",
    why: "Most strategies work with the trend, not against it. Knowing the regime tells you whether to lean on breakout signals (trend) or bounce signals (range)."
  },
  golden_cross: {
    term: "Golden cross / Death cross",
    one: "When the 50-day average crosses the 200-day average.",
    what: "Golden cross = 50-day rises above the 200-day (bullish long-term shift). Death cross = 50-day falls below the 200-day (bearish shift).",
    read: "These are slow, big-picture signals — they confirm a trend change rather than predict it.",
    why: "Widely covered in the media and watched by large investors, so they can move sentiment even though they lag the actual turn."
  },

  /* ---------- levels, range, volatility ---------- */
  support_resistance: {
    term: "Support & Resistance",
    one: "Price floors (support) and ceilings (resistance) where moves often stall.",
    what: "Support = a level where buyers have historically stepped in and stopped declines. Resistance = a level where sellers have historically capped rallies. We estimate them from pivot math on the recent range.",
    read: "Approaching resistance from below = expect a possible stall or pullback. Approaching support from above = expect a possible bounce. A decisive BREAK through either is significant — resistance broken can become new support.",
    why: "They're natural places to watch for entries, exits, and risk levels. 'Buy near support, watch for rejection at resistance' is a core idea in technical trading."
  },
  pivot: {
    term: "Pivot point",
    one: "A reference midpoint for the day, derived from yesterday's high/low/close.",
    what: "The average of the prior day's high, low, and close. Support and resistance levels are calculated around it.",
    read: "Trading above the pivot = mildly bullish bias for the session; below = mildly bearish. It's a day-trader's anchor.",
    why: "Gives a quick, objective 'line in the sand' for the day without any opinion baked in."
  },
  range_52w: {
    term: "52-week range & percentile",
    one: "Where today's price sits between its one-year low and high.",
    what: "The lowest and highest price over the past year, and where the current price falls between them (0th percentile = at the low, 100th = at the high).",
    read: "Near the high (80th+ percentile) = strong stock, but less 'room' and possibly stretched. Near the low (under 20th) = weak or beaten-down; could be value or a falling knife.",
    why: "Context for whether you're buying strength or weakness. New 52-week highs often keep going (momentum); new lows often keep falling — until they don't."
  },
  volatility: {
    term: "Volatility (ATR-based)",
    one: "How much this stock typically moves in a day.",
    what: "Based on ATR (Average True Range) — the average daily high-to-low travel — expressed as a % of price. We label it Low, Normal, or High.",
    read: "High volatility = bigger daily swings (bigger potential gains AND losses; size positions smaller). Low = calmer, steadier.",
    why: "Tells you how much 'noise' to expect and how to size risk. A 2% move in a low-vol stock is a big deal; in a high-vol name it's just Tuesday."
  },
  atr: {
    term: "ATR — Average True Range",
    one: "The average distance price travels in a single day, in currency terms.",
    what: "Averages the daily high-to-low range (accounting for gaps) over 14 days. A raw measure of movement, not direction.",
    read: "A larger ATR means wider daily swings. Often used to set stop-losses (e.g. 2× ATR below entry) so normal wiggles don't stop you out.",
    why: "Turns 'this stock is jumpy' into an actual number you can size trades and risk around."
  },
  bollinger: {
    term: "Bollinger Bands %B",
    one: "Shows where price sits inside its volatility envelope.",
    what: "Bands are drawn 2 standard deviations above/below the 20-day average. %B tells you where price is: 0 = lower band, 1 = upper band, 0.5 = middle.",
    read: "Near 1 (upper band) = stretched high / strong. Near 0 (lower band) = stretched low / weak. Bands squeezing tight often precede a big move.",
    why: "Frames whether today's price is 'normal' or an extreme relative to its own recent volatility."
  },
  obv: {
    term: "OBV — On-Balance Volume",
    one: "Tracks whether volume is flowing into or out of the stock.",
    what: "Adds the day's volume when price closes up, subtracts it when price closes down, and keeps a running total.",
    read: "Rising OBV = buying pressure (accumulation). Falling OBV = selling pressure (distribution). If price rises but OBV doesn't, the rally may lack conviction.",
    why: "Volume is the fuel behind price. OBV helps you see if a move is backed by real participation or is running on fumes."
  },

  /* ---------- fundamentals ---------- */
  pe: {
    term: "P/E ratio (trailing)",
    one: "How many dollars you pay for each $1 of the company's past-year profit.",
    what: "Price per share ÷ earnings per share over the last 12 months. A basic valuation gauge.",
    read: "A high P/E (say 40+) means the market expects strong growth — you're paying up. A low P/E (under ~12) can mean cheap value OR a troubled business. Always compare within the same industry.",
    why: "The quickest sense of whether a stock is 'expensive' or 'cheap' relative to what it actually earns. Context is everything — a 30 P/E is cheap for fast growth, dear for a utility."
  },
  forward_pe: {
    term: "Forward P/E",
    one: "P/E based on expected NEXT-year profits instead of past profits.",
    what: "Price ÷ analysts' forecast earnings for the year ahead.",
    read: "If forward P/E is well below trailing P/E, the market expects profits to grow. If higher, it expects profits to shrink.",
    why: "Stocks are priced on the future, so forward P/E is often the more relevant valuation — but it relies on forecasts, which can be wrong."
  },
  market_cap: {
    term: "Market capitalization",
    one: "The total dollar value of all the company's shares — its 'size'.",
    what: "Share price × number of shares outstanding. Above ~$200B = mega-cap, $10–200B = large-cap, $2–10B = mid-cap, under $2B = small-cap.",
    read: "Bigger caps are generally more stable and liquid; smaller caps move more and are riskier but can grow faster.",
    why: "Size shapes risk, liquidity, and how much a stock can realistically grow from here."
  },
  profit_margins: {
    term: "Profit margin",
    one: "How many cents of profit the company keeps from each $1 of sales.",
    what: "Net profit ÷ revenue, as a %. A 25% margin means 25¢ of every sales dollar becomes profit.",
    read: "Higher = more efficient / more pricing power. Compare within an industry — software margins dwarf grocery margins by nature.",
    why: "High, stable margins usually signal a strong competitive position ('moat'). Falling margins are an early warning."
  },
  revenue_growth: {
    term: "Revenue growth",
    one: "How fast the company's sales are increasing year over year.",
    what: "The % change in revenue vs the same period last year.",
    read: "Strong positive growth = expanding business. Slowing or negative = maturing or struggling.",
    why: "Growth is a primary driver of stock returns, especially for younger companies where profits are still small."
  },
  dividend_yield: {
    term: "Dividend yield",
    one: "The annual cash payout to shareholders as a % of the share price.",
    what: "Yearly dividends per share ÷ share price. A $2 dividend on a $100 stock = 2% yield.",
    read: "Higher yield = more income, but a very high yield (8%+) can signal the market expects a cut. Many high-growth stocks pay nothing and reinvest instead.",
    why: "Matters if you want income. Steady, growing dividends also signal management confidence and financial health."
  },
  beta: {
    term: "Beta",
    one: "How much the stock moves relative to the overall market.",
    what: "Beta 1.0 = moves with the market. 1.5 = 50% bigger swings than the market. 0.5 = half as jumpy. Below 0 = tends to move opposite.",
    read: "High beta = amplifies both up and down markets (aggressive). Low beta = steadier, more defensive.",
    why: "Tells you how a stock will likely behave when the whole market rallies or sells off — key for managing portfolio risk."
  },

  /* ---------- concepts ---------- */
  overbought_oversold: {
    term: "Overbought / Oversold",
    one: "Shorthand for 'risen too far, too fast' vs 'fallen too far, too fast'.",
    what: "Momentum tools like RSI flag when a move looks stretched relative to recent history.",
    read: "Overbought = vulnerable to a pause or pullback (NOT an automatic sell). Oversold = candidate for a bounce (NOT an automatic buy). Strong trends can stay overbought/oversold for a long time.",
    why: "Helps you avoid chasing a move at its most extended point and spot potential mean-reversion opportunities."
  },
  bullish_bearish: {
    term: "Bullish / Bearish",
    one: "Bullish = expecting prices to rise. Bearish = expecting them to fall.",
    what: "A 'bull' charges upward; a 'bear' swipes downward. Applied to signals, sentiment, or a whole market.",
    read: "A bullish signal leans toward upside; a bearish one toward downside. 'Risk-on' markets are bullish; 'risk-off' are bearish/defensive.",
    why: "The basic vocabulary for describing which way the odds are tilting."
  }
};

/* ==========================================================================
   MARKET CONCEPTS — for someone with ZERO knowledge. What the board numbers
   even ARE, and what they mean. Surfaced as ⓘ on the Markets board + an
   "About this" teach-first block when you open any index/asset.
   ========================================================================== */
Object.assign(GLOSSARY, {
  index: {
    term: "Stock-market index",
    one: "A single number that tracks a whole basket of stocks, so you can see how a market is doing at a glance.",
    what: "Instead of checking hundreds of companies one by one, an index bundles them into one figure. When someone says 'the market went up today', they almost always mean an index — like the S&P 500 or the Nifty — rose.",
    read: "The index LEVEL (say 7,499) is just a running score — it is NOT a price in dollars or rupees, and the raw size of the number doesn't really matter. What matters is the % change day-to-day and the direction over weeks and months.",
    why: "It's the fastest read on whether stocks are broadly rising or falling, and on the overall mood of investors.",
    scale: "Watch the % change and the trend — not the raw level."
  },
  sp500: {
    term: "S&P 500 (the US market's scoreboard)",
    one: "The 500 biggest US public companies, rolled into one number.",
    what: "A 'market-cap-weighted' index (bigger companies count more) spanning tech, banks, healthcare, energy and more — Apple, Microsoft and Nvidia are among the largest members. It's the benchmark most US investors and funds measure themselves against.",
    read: "Up = large US companies broadly rose that day. A steadily rising S&P over months is the sign of a healthy 'bull' (upward) market.",
    why: "When people ask 'how did the market do?', this is usually the answer. It's the world's most-watched equity gauge.",
    scale: "For an index, a ±0.5% day is normal; ±1–2% is a notable move."
  },
  nasdaq: {
    term: "Nasdaq Composite (the tech gauge)",
    one: "A US index dominated by technology and high-growth companies.",
    what: "Heavy in tech — Apple, Nvidia, Microsoft, Amazon — so it tends to swing more than the S&P 500. When you hear 'tech led the market', this is where it shows up.",
    read: "When the Nasdaq outpaces the Dow, growth/tech is leading and investors are feeling bold ('risk-on'). When it lags, the mood is turning cautious.",
    why: "The quickest gauge of appetite for high-growth tech and AI names."
  },
  dow: {
    term: "Dow Jones (the old-economy blue-chips)",
    one: "30 large, well-established US companies.",
    what: "An older, narrower index of 30 big 'blue-chip' names, leaning more 'old economy' (industrials, banks, consumer) than the tech-heavy Nasdaq.",
    read: "When the Dow leads and the Nasdaq lags, money is rotating toward safer, established firms — often a more cautious signal.",
    why: "A traditional pulse of big, stable American business."
  },
  nifty: {
    term: "Nifty 50 (India's benchmark)",
    one: "The 50 biggest companies on India's National Stock Exchange (NSE).",
    what: "India's equivalent of the S&P 500 — includes Reliance, HDFC Bank, TCS and Infosys. It's the headline gauge for 'how did the Indian market do today'.",
    read: "Up = Indian large-caps broadly rose. Watch it alongside the Sensex; they usually move together.",
    why: "The single most-watched number for Indian equities."
  },
  sensex: {
    term: "Sensex (India's other headline index)",
    one: "30 large companies on the Bombay Stock Exchange (BSE).",
    what: "The older sibling of the Nifty — 30 blue-chips instead of 50. The Nifty and Sensex almost always move in the same direction.",
    read: "If the Nifty and Sensex ever diverge noticeably, look at which sectors are driving each. Otherwise, treat them as the same signal.",
    why: "Widely quoted in Indian media as the market's daily temperature."
  },
  banknifty: {
    term: "Bank Nifty (India's banking sector)",
    one: "An index of India's biggest banks.",
    what: "Tracks the leading NSE-listed banks (HDFC Bank, ICICI, SBI and others). Banks lend to businesses and consumers, so they're the backbone of the economy.",
    read: "Bank Nifty leading the market = confidence in the domestic economy. Lagging = caution about growth or bad loans.",
    why: "A strong banking sector usually means a strong, credit-fuelled economy — so it's a key 'internal' health check for India."
  },
  points_vs_price: {
    term: "Why an index is in 'points', not money",
    one: "An index level is a calculated score, not a price you can pay.",
    what: "Nifty at 24,006 or the S&P at 7,499 are index 'points' — a measure of the whole basket. You can't buy '24,006' of anything; the number just tracks the group.",
    read: "Don't compare an index level to a stock price, and don't read meaning into the raw size. Only the % change and the trend matter.",
    why: "Clears up the most common beginner confusion — an index level and a share price are completely different things."
  },
  percent_change: {
    term: "The % change (how big was the move?)",
    one: "How much a value rose or fell versus the day before.",
    what: "+1% means it's 1% higher than yesterday's close. Green/plus = up, red/minus = down. How BIG a % is depends on the asset.",
    read: "For a broad index: ±0.5% is a normal day, ±1–2% is notable, ±3%+ is a big, news-driven move. For Bitcoin, even 5% is routine. So always judge the % against what's normal for that thing.",
    why: "The % is how you compare moves across very different assets — an index, a single stock, gold, crypto — on the same footing.",
    scale: "Index: ±0.5% normal · ±1–2% notable · ±3%+ big.  Crypto: far larger swings are normal."
  },
  usdinr: {
    term: "USD / INR (the rupee's exchange rate)",
    one: "How many Indian rupees it takes to buy one US dollar.",
    what: "USD/INR = 95 means $1 costs ₹95. Crucially: when this number goes UP, the rupee is getting WEAKER (each dollar costs more rupees); when it goes down, the rupee is stronger.",
    read: "A rising number (weaker rupee) makes imports — oil, electronics, foreign travel, education abroad — more expensive and adds to inflation. It helps exporters (like IT firms) who earn in dollars.",
    why: "A core gauge of India's economic health, and something that hits your everyday cost of living directly.",
    scale: "Number UP = rupee weaker · number DOWN = rupee stronger."
  },
  gold_asset: {
    term: "Gold (the 'safe haven')",
    one: "Gold, priced per ounce in US dollars — where money hides when it's nervous.",
    what: "Investors buy gold when they're fearful or expect inflation to erode cash. Gold pays no interest, so when interest rates rise, gold becomes relatively less attractive (cash and bonds now pay you to wait).",
    read: "Gold rising often signals fear or inflation worries. Gold falling while interest rates rise is the textbook reaction.",
    why: "A barometer of fear, and a hedge many people hold to balance out riskier assets like stocks."
  },
  crude_asset: {
    term: "Crude oil (the economy's lifeblood)",
    one: "Oil, priced per barrel — it feeds into the cost of almost everything.",
    what: "Oil powers transport, factories and shipping, so its price ripples into the cost of goods everywhere. Wars and supply cuts push it up; slowing demand pushes it down.",
    read: "Rising oil = inflation pressure, and real pain for oil IMPORTERS like India (costlier fuel, weaker rupee). Falling oil = relief for importers and for inflation.",
    why: "One of the biggest single swing factors for inflation and for the world economy — and it hits India hard."
  },
  bitcoin_asset: {
    term: "Bitcoin (high-risk digital asset)",
    one: "The largest cryptocurrency — very high risk, very high volatility.",
    what: "A digital currency with no central bank behind it; its price is driven purely by demand, sentiment and interest rates. It swings far more violently than stocks.",
    read: "Bitcoin usually trades 'risk-on' — it rises when investors are bold and falls hard when they're fearful or when interest rates climb. A day of ±2% is calm for Bitcoin; 10%+ moves happen.",
    why: "A pure gauge of speculative risk appetite — when crypto diverges from stocks (like today), it's a warning sign worth noting.",
    scale: "Calm day ±2% · big day 10%+ — much wilder than stocks."
  },
  ethereum_asset: {
    term: "Ether / Ethereum (the #2 crypto)",
    one: "The second-largest cryptocurrency, powering the Ethereum network.",
    what: "Like Bitcoin, but tied to a platform used to build apps and 'smart contracts'. It's often even more volatile than Bitcoin.",
    read: "Usually moves in the same direction as Bitcoin and overall crypto risk appetite.",
    why: "A read on the broader crypto market beyond Bitcoin alone."
  },
  vix: {
    term: "VIX (the market's 'fear gauge')",
    one: "How much turbulence investors expect in the near future.",
    what: "The VIX rises when investors are scared and paying up for protection, and falls when they're calm. It's derived from options prices on the S&P 500.",
    read: "Below ~15 = calm/complacent; 20–30 = nervous; above 30 = fear; 40+ = panic. A LOW VIX during bad news can mean the market is underestimating the risk.",
    why: "A quick emotional read on the market — and a low VIX during a hot inflation scare (like today) is a notable disconnect.",
    scale: "<15 calm · 20–30 nervous · 30+ fear · 40+ panic"
  },
  risk_on_off: {
    term: "Risk-on vs Risk-off",
    one: "Two words that capture the market's whole mood.",
    what: "'Risk-on' = investors feeling bold: money flows into stocks (especially tech) and crypto. 'Risk-off' = investors playing safe: money flows into cash, government bonds, and often gold and the US dollar.",
    read: "Nasdaq up + crypto up + VIX low = risk-on. Stocks down + bonds/gold/dollar up = risk-off.",
    why: "Tells you, in two words, why unrelated assets are moving together — and which way the herd is leaning today."
  },
  yields: {
    term: "Bond yields (the hidden hand)",
    one: "The interest rate a government pays to borrow money.",
    what: "When bond yields rise, borrowing gets more expensive across the whole economy, and stocks — especially expensive, fast-growing tech — tend to fall, because safe bonds now pay you more to wait.",
    read: "Rising yields = headwind for stocks, gold and crypto. Falling yields = tailwind.",
    why: "Often the real reason behind a big market move, even when the headlines point elsewhere."
  },
  bull_bear_market: {
    term: "Bull market vs Bear market",
    one: "A 'bull' market trends up over time; a 'bear' market trends down.",
    what: "Rule of thumb: a bear market is a drop of 20%+ from the highs; a bull market is a sustained rise. Named for how the animals strike — a bull thrusts UP with its horns, a bear swipes DOWN with its paw.",
    read: "In a bull market, dips tend to get bought (buyers step in). In a bear market, rallies tend to get sold. The regime shapes how every individual move behaves.",
    why: "The single biggest piece of context for understanding any day's action."
  }
});

/* ==========================================================================
   MACRO & WORLD CONCEPTS — the ideas world-news stories teach. Referenced by
   each story's `concepts` chips (📚) so the news doubles as a course.
   ========================================================================== */
Object.assign(GLOSSARY, {
  inflation: {
    term: "Inflation",
    one: "The rate at which prices rise — money quietly losing its buying power.",
    what: "Measured by tracking the cost of a basket of everyday goods and services over time. 2% a year is what most central banks aim for; 4%+ starts to hurt; deflation (falling prices) brings its own problems.",
    read: "Rising inflation → central banks lean toward RAISING interest rates → borrowing costs up, stocks/gold/crypto usually pressured. Falling inflation → room to cut rates → usually good for assets.",
    why: "It's the single force behind most central-bank decisions, market swings, and your own cost of living. Most big market stories eventually trace back to inflation.",
    scale: "~2% target · 3–4% uncomfortable · 5%+ alarm bells"
  },
  interest_rates: {
    term: "Interest rates (the policy rate)",
    one: "The price of borrowing money, set at its base level by the central bank.",
    what: "The central bank sets a baseline rate that ripples into every loan, mortgage, and bond. Raising it cools spending and inflation; cutting it stimulates growth.",
    read: "Rates UP = headwind for stocks (especially growth/tech), gold and crypto, and stronger home currency. Rates DOWN = tailwind for risk assets.",
    why: "The gravity of finance: nearly every asset's value is priced against 'what could I safely earn in interest instead?'"
  },
  central_bank: {
    term: "Central bank (Fed / RBI / ECB)",
    one: "The institution that controls a country's money — its interest rates and currency stability.",
    what: "The US Federal Reserve ('Fed'), Reserve Bank of India (RBI), European Central Bank (ECB) etc. They set policy rates, manage inflation, backstop banks in crises, and often manage the currency.",
    read: "Markets parse every word central bankers say ('hawkish' = leaning to higher rates, 'dovish' = lower). A surprise from a big central bank moves every market on earth.",
    why: "No single actor moves markets more. Understanding what the Fed/RBI want is half of understanding any market day."
  },
  bond_market: {
    term: "Bonds & yields",
    one: "Loans to governments/companies that trade like assets; the 'yield' is the interest rate they pay.",
    what: "When you buy a bond you're lending money. Yields move opposite to bond prices: strong demand pushes yields down, fear of inflation or oversupply pushes them up.",
    read: "Rising yields = money can earn more 'safely' → expensive stocks, gold, and crypto look less attractive. Falling yields = the reverse. The 10-year US Treasury yield is the world's reference rate.",
    why: "The bond market is bigger than the stock market and often the real reason stocks move — even when headlines say otherwise."
  },
  tariffs: {
    term: "Tariffs & trade deals",
    one: "Taxes on imported goods — the main lever countries pull in trade disputes.",
    what: "A tariff makes foreign goods pricier, protecting local producers but raising costs for consumers and importers. Trade deals lower or remove them in exchange for access.",
    read: "New tariffs → exporters to that market get hurt, domestic rivals helped, prices rise (inflationary). A trade deal → exporters rally, currencies often strengthen.",
    why: "For India, US tariff decisions directly hit IT, pharma and textiles exporters — and the July-24-style deadlines you see in the news set real market catalysts."
  },
  sanctions: {
    term: "Sanctions & export controls",
    one: "Economic weapons: cutting a country or company off from money, goods, or technology.",
    what: "Sanctions block trade/finance with a target (e.g. Russia); export controls stop specific tech (e.g. advanced chips) from being sold to rivals. Both reshape global supply chains.",
    read: "Watch who's targeted and what's restricted: energy sanctions move oil; chip controls move semiconductor stocks; retaliation risk keeps markets nervous.",
    why: "They're how modern great-power conflict is fought — and they regularly reroute the flows of oil, chips, and money that markets price."
  },
  gdp: {
    term: "GDP & economic growth",
    one: "The total value of everything a country produces — the broadest economic scorecard.",
    what: "Gross Domestic Product. Its growth rate tells you if an economy is expanding (jobs, profits, tax revenue) or shrinking (recession = two negative quarters, roughly).",
    read: "India growing ~6–8% = world-leading. US ~2–3% = healthy. Below 0 = recession. Faster growth generally supports stocks and the currency.",
    why: "Growth is the tide that lifts (or drops) all boats — company profits, employment, and market confidence all ride on it."
  },
  fiscal_vs_monetary: {
    term: "Fiscal vs monetary policy",
    one: "The two levers that steer an economy: government spending/taxes vs central-bank interest rates.",
    what: "Fiscal = what the government does (budgets, taxes like GST, subsidies, infrastructure). Monetary = what the central bank does (rates, money supply). They can push together or against each other.",
    read: "Big spending + low rates = strong stimulus (watch inflation). Tight budget + high rates = braking hard (watch growth).",
    why: "Knowing which lever is being pulled tells you whether policy is helping or fighting the market you're watching."
  },
  supply_chain: {
    term: "Supply chains & chokepoints",
    one: "The global web that makes and moves everything — and the narrow points where it can break.",
    what: "Modern products cross many borders before reaching you. Chokepoints (Strait of Hormuz for oil, Taiwan for chips, Suez for shipping) concentrate risk: one disruption ripples worldwide.",
    read: "A chokepoint threat = prices of whatever flows through it spike (oil, freight, chips), inflation risk rises, and 'de-risking' (moving factories) accelerates.",
    why: "Most surprise inflation and many geopolitical market shocks are supply-chain stories at heart — including what India pays for oil."
  },
  fii_flows: {
    term: "FII/FPI flows (foreign money in India)",
    one: "Foreign investors' money moving into or out of Indian stocks and bonds.",
    what: "FII/FPI = Foreign Institutional/Portfolio Investors. Their buying pushes Indian markets and the rupee up; their selling ('outflows') pressures both. Driven largely by US interest rates and global risk appetite.",
    read: "High US rates or global fear → money flows OUT of emerging markets like India (rupee weakens, Nifty pressured). US rate cuts or optimism → flows return.",
    why: "One of the biggest day-to-day drivers of the Nifty, Sensex and USD/INR — India's markets breathe with global money."
  },
  crude_geopolitics: {
    term: "Oil & geopolitics (India's exposure)",
    one: "Why wars and chokepoints far away change what India pays at the pump.",
    what: "India imports ~85% of its oil, priced in dollars. Any supply threat (Hormuz, Russia sanctions, OPEC cuts) raises crude — which widens India's import bill, weakens the rupee, and fuels inflation.",
    read: "Crude UP = bad for India (inflation, rupee, current-account deficit); great for oil producers. Crude DOWN = a broad tax cut for the Indian economy.",
    why: "The single most direct line from world geopolitics to Indian household budgets and the Nifty."
  },
  currency_strength: {
    term: "Currency strength (why the rupee moves)",
    one: "What makes a currency rise or fall against the dollar — and who wins each way.",
    what: "A currency strengthens when money flows in (exports, investment, high local rates) and weakens when money flows out (imports, foreign selling, higher US rates). Central banks smooth the moves with reserves.",
    read: "Weak rupee: imports/fuel/foreign travel cost more, but IT exporters earn more per dollar. Strong rupee: the reverse. USD/INR rising = rupee weakening.",
    why: "The exchange rate is the price of your economy in the world's money — it touches inflation, corporate profits, and your cost of living."
  }
});

/* Which market concept explains a given board ticker (for the 'About this' teach block). */
const CONCEPT_FOR_TICKER = {
  "^GSPC": "sp500", "^IXIC": "nasdaq", "^DJI": "dow",
  "^NSEI": "nifty", "^BSESN": "sensex", "^NSEBANK": "banknifty",
  "BTC-USD": "bitcoin_asset", "ETH-USD": "ethereum_asset",
  "GC=F": "gold_asset", "CL=F": "crude_asset", "INR=X": "usdinr",
};
function conceptForTicker(ticker) {
  return CONCEPT_FOR_TICKER[(ticker || "").toUpperCase()] || null;
}

/* Map an indicator/fundamental name coming from the data to a glossary key. */
function glossaryKey(name, explicit) {
  if (explicit && GLOSSARY[explicit]) return explicit;
  const n = (name || "").toLowerCase();
  if (n.startsWith("rsi")) return "rsi";
  if (n.startsWith("macd")) return "macd";
  if (n.startsWith("stoch")) return "stochastic";
  if (n.startsWith("cci")) return "cci";
  if (n.startsWith("williams")) return "williams_r";
  if (n.startsWith("momentum")) return "momentum";
  if (n.startsWith("sma")) return "sma";
  if (n.startsWith("ema")) return "ema";
  if (n.includes("market cap")) return "market_cap";
  if (n.includes("p/e (fwd") || n.includes("forward")) return "forward_pe";
  if (n.includes("p/e")) return "pe";
  if (n.includes("margin")) return "profit_margins";
  if (n.includes("rev growth") || n.includes("revenue")) return "revenue_growth";
  if (n.includes("div yield") || n.includes("dividend")) return "dividend_yield";
  if (n.includes("beta")) return "beta";
  return null;
}
