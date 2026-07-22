"""Plain-English metric explanations for API responses."""

VOLATILITY = (
    "Measures how violently your portfolio's value swings up and down over a year. "
    "Lower means a smoother, more predictable ride; higher means greater ups and downs."
)

SHARPE = (
    "Shows how much excess return you get for every unit of risk you take. "
    "A Sharpe ratio above 1.0 means your returns justify the rollercoaster."
)

SORTINO = (
    "Similar to the Sharpe Ratio, but only penalizes your portfolio for downward drops, "
    "ignoring healthy upside swings."
)

VAR = (
    "The estimated maximum dollar amount (or percentage) you could lose on a typical "
    "bad day/month with 95% or 99% confidence."
)

CVAR = (
    "Your average expected loss on absolute worst-case days—tells you what happens when "
    "market drops go beyond normal bad days."
)

MAX_DRAWDOWN = (
    "The worst top-to-bottom crash your portfolio experienced from its highest point "
    "before recovering."
)

CORRELATION = (
    "Tracks how closely your assets move together (from -1.0 to +1.0). Assets close to "
    "+1.0 fall together; assets near 0 or negative cushion each other's falls."
)

HHI = (
    "A score measuring whether your money is evenly spread out or concentrated in too "
    "few holdings. High HHI means single-stock risk."
)

BETA = (
    "Compares your portfolio's reactivity to the broader market. A Beta of 1.2 means if "
    "the S&P 500 moves up or down 10%, your portfolio tends to move 12%."
)

HEALTH = (
    "A single overall composite score evaluating how well-balanced, risk-adjusted, and "
    "resilient your portfolio is against market shocks."
)

ANNUALIZED_RETURN = (
    "Your portfolio's average yearly return over the selected lookback window, "
    "annualized from daily compounded growth."
)

BENCHMARK = (
    "Sector ETF benchmark stats (annualized return, volatility, and Sharpe) for "
    "comparing your portfolio against a representative industry basket."
)
