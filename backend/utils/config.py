import pandas as pd

# Arguments
CACHE_SIZE = 128
MIN_ANNUAL_DELTA_DAYS = int(365 * 0.9)
MAX_ANNUAL_DELTA_DAYS = int(365 * 1.1)
MIN_QUARTER_DELTA_DAYS = int(90 * 0.9)
MAX_QUARTER_DELTA_DAYS = int(90 * 1.1)

HEADERS = {
    'User-Agent': 'FinDataFetcher/1.0 (contact@example.com)',
    'Accept': 'application/json'
}

# Metrics Structs 
METRICS_CONCEPTS = {
    # Balance Sheet
    "TotalCurrentAssets": ["AssetsCurrent"],
    "CashAndCashEquivalents" : ["CashAndCashEquivalentsAtCarryingValue"],
    "TotalAssets": ["Assets"],
    "ShortTermDebt": ["LongTermDebtCurrent", "DebtCurrent"],
    "TotalCurrentLiabilities": ["LiabilitiesCurrent"],
    "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "TotalLiabilities": ["Liabilities"], 
    "StockholdersEquity": ["StockholdersEquity"],
    
    # Operations / Income Statement
    "Revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
    "ResearchAndDevelopment": ["ResearchAndDevelopmentExpense"],
    #"SalesAndMarketing": ["SellingAndMarketingExpense"],
    #"GAndA": ["GeneralAndAdministrativeExpense"],
    "CostOfRevenue": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold","CostOfRevenue"],
    "GrossProfit": ["GrossProfit"],
    "TotalOperatingExpenses": ["CostsAndExpenses", "OperatingExpenses"],
    "OperatingIncome": ["OperatingIncomeLoss"],
    "NonOperatingIncomeExpense": ["NonoperatingIncomeExpense"],
    "DepreciationAmortization": ["DepreciationAmortization", "Depreciation", "DepreciationDepletionAndAmortization"],
    "NetIncome": ["ProfitLoss", "NetIncomeLoss"],
    "BasicEps": ["EarningsPerShareBasic", "BasicEarningsLossPerShare"],
    "DilutedEps": ["EarningsPerShareDiluted", "DilutedEarningsLossPerShare"],
    "SharesOutstandingBasic": ["WeightedAverageNumberOfSharesOutstandingBasic"],
    "SharesOutstandingDiluted": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "SharesOutstanding": ["CommonStockSharesOutstanding", "NumberOfSharesOutstanding"],
    
    # Cashflow
    "StockBasedCompensation": ["ShareBasedCompensation"],
    "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
    "TotalCash": ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "DividendsPaid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "StockBuybacks": ["PaymentsForRepurchaseOfCommonStock"], 
    "CapitalExpenditures": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], # "PaymentsToAcquireProductiveAssets", "CapitalExpenditures"
    #"InterestPaid": ["CashPaidForInterest"], #TODO: Unsure and unnecessary
}

COMPANY_TAG_OVERRIDES = {
    "AAPL": {
        "Revenue": ["Revenues"],  
        "OperatingIncome": ["OperatingIncomeLoss"]
    },
    "TSLA": {
        "CapitalExpenditures": ["CapitalExpendituresAndInvestments"]
    },
}

CUSTOM_METRICS = [
    # -----------------------------------
    # CASH FLOW
    # -----------------------------------
    {
        "columns": ["OperatingCashFlow", "CapitalExpenditures"],
        "func": lambda ocf, capex: ocf.sub(capex, fill_value=0),
        "result_col": "FreeCashFlow",
    },

    # -----------------------------------
    # PROFITABILITY MARGINS
    # -----------------------------------
    {
        "columns": ["Revenue", "CostOfRevenue"],
        "func": lambda rev, cor: (rev.sub(cor, fill_value=0)).div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "GrossMargin",
    },
    {
        "columns": ["OperatingIncome", "Revenue"],
        "func": lambda op_inc, rev: op_inc.div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "OperatingMargin",
    },
    {
        "columns": ["NetIncome", "Revenue"],
        "func": lambda net_inc, rev: net_inc.div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "ProfitMargin",
    },

    # -----------------------------------
    # RETURNS
    # -----------------------------------
    {
        "columns": ["OperatingIncome", "TotalAssets", "TotalCurrentLiabilities"],
        "func": lambda op_inc, assets, curr_liab: op_inc.div((assets - curr_liab).replace(0, pd.NA)).mul(100),
        "result_col": "ROCE",
    },
    {
        "columns": ["NetIncome", "TotalAssets"],
        "func": lambda net_inc, assets: net_inc.div(assets.replace(0, pd.NA)).mul(100),
        "result_col": "ROA",
    },
    {
        "columns": ["NetIncome", "StockholdersEquity"],
        "func": lambda net_inc, equity: net_inc.div(equity.replace(0, pd.NA)).mul(100),
        "result_col": "ROE",
    },
    #{
    #     "columns": ["OperatingIncome", "TotalDebt", "StockholdersEquity", "CashAndCashEquivalents", "TaxRate"],
    #     "func": lambda op_inc, debt, equity, cash, tax: (
    #         (op_inc * (1 - tax.fillna(0))).div((debt + equity - cash).replace(0, pd.NA)).mul(100)
    #     ),
    #     "result_col": "ROIC",
    # },

    # -----------------------------------
    # LEVERAGE / COVERAGE
    # -----------------------------------
    {
        "columns": ["LongTermDebt", "ShortTermDebt", "StockholdersEquity"],
        "func": lambda ltd, std, equity: (ltd.add(std, fill_value=0)).div(equity.replace(0, pd.NA)),
        "result_col": "DebtToEquity",
    },
    # InterestPaid not in METRICS_CONCEPTS → skip if missing
    {
        "columns": ["OperatingIncome", "InterestPaid"],
        "func": lambda op_inc, interest: op_inc.div(interest.replace(0, pd.NA)) if interest is not None else pd.NA,
        "result_col": "InterestCoverage",
    },
    {
        "columns": ["LongTermDebt", "ShortTermDebt", "CashAndCashEquivalents", "OperatingIncome", "DepreciationAmortization"],
        "func": lambda ltd, std, cash, op_inc, dep: (
            (ltd.add(std, fill_value=0) - cash).div((op_inc + dep.fillna(0)).replace(0, pd.NA))
        ),
        "result_col": "NetDebtToEBITDA",
    },


    # -----------------------------------
    # CASH FLOW YIELDS
    # -----------------------------------
    # {
    #     "columns": ["FreeCashFlow", "TotalAssets"],
    #     "func": lambda fcf, assets: fcf.div(assets.replace(0, pd.NA)).mul(100),
    #     "result_col": "FCFYield",
    # },
    # {
    #     "columns": ["StockBasedCompensation", "FreeCashFlow", "TotalAssets"],
    #     "func": lambda sbc, fcf, assets: (fcf.add(sbc, fill_value=0)).div(assets.replace(0, pd.NA)).mul(100),
    #     "result_col": "SBCAdjustedFCFYield",
    # },

    # -----------------------------------
    # VALUATION
    # -----------------------------------
    # {
    #     "columns": ["MarketCap", "NetIncome"],
    #     "func": lambda mc, ni: mc.div(ni.replace(0, pd.NA)),
    #     "result_col": "PERatio",
    # },
    # placeholders for ratios computed from other inputs if available
    # {
    #     "columns": ["MarketCap", "TotalDebt", "CashAndCashEquivalents", "OperatingIncome", "DepreciationAmortization"],
    #     "func": lambda mc, debt, cash, op_inc, dep: (
    #         (mc + debt - cash).div((op_inc + dep.fillna(0)).replace(0, pd.NA))
    #     ),
    #     "result_col": "EVToEBITDA",
    # },
    # {
    #     "columns": ["MarketCap", "TotalAssets", "TotalLiabilities"],
    #     "func": lambda mc, assets, liab: mc.div((assets - liab).replace(0, pd.NA)),
    #     "result_col": "PriceToBook",
    # }
    # {
    #     "columns": ["PERatio", "EPSGrowth"],
    #     "func": lambda pe, growth: pe.div(growth.replace(0, pd.NA)).round(2),
    #     "result_col": "PEGRatio",
    # },
    # {
    #     "columns": ["MarketCap", "TotalDebt", "CashAndCashEquivalents", "Revenue"],
    #     "func": lambda mc, debt, cash, rev: ((mc + debt - cash).div(rev.replace(0, pd.NA))).round(2),
    #     "result_col": "EVToSales",
    # }
]

