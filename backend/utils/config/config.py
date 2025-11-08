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

METRICS_CONCEPTS_OLD = {
    # CONSOLIDATED BALANCE SHEETS
    "CashAndCashEquivalents": ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents"],
    "TotalCurrentAssets": ["AssetsCurrent", "CurrentAssets"],
    "TotalAssets": ["Assets"],
    "TotalCurrentLiabilities": ["LiabilitiesCurrent", "CurrentLiabilities"],
    "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndFinanceLeasesNoncurrent"],
    "ShortTermDebt": ["DebtCurrent", "LongTermDebtCurrent", "LongTermDebtAndFinanceLeasesCurrent"],
    "InterestExpense": ["InterestExpense"],
    "TotalLiabilities": ["Liabilities"],
    "StockholdersEquity": ["StockholdersEquity"],
    "DividendsPaid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "DividendsPaid"],
    "TotalLiabilitiesAndEquities": ["LiabilitiesAndStockholdersEquity"],
    
    # CONSOLIDATED STATEMENTS OF OPERATIONS
    "Revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "Revenue"],
    "CostOfRevenue": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfRevenue", "CostOfSales"],
    "ResearchAndDevelopment": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost", "LaborAndRelatedExpense"],
    "SalesAndMarketing": ["SellingAndMarketingExpense", "MarketingAndAdvertisingExpense"],
    "GAndA": ["GeneralAndAdministrativeExpense"],
    "Restructuring": ["RestructuringCharges", "RestructuringAndOtherExpenses"],
    "StockBasedCompensation": ["ShareBasedCompensation", "AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue"],
    "TotalOperatingExpenses": ["OperatingExpenses", "CostsAndExpenses"],
    "OperatingIncome": ["OperatingIncomeLoss"],
    "NetIncome": ["NetIncomeLoss", "ProfitLoss"],
    "BasicEPS": ["EarningsPerShareBasic", "BasicEarningsLossPerShare"],
    "DilutedEPS": ["EarningsPerShareDiluted", "DilutedEarningsLossPerShare"],
    
    # CONSOLIDATED STATEMENTS OF CASH FLOWS
    "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
    "CapitalExpenditures": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "StockBuybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "DepreciationAmortization": ["DepreciationAndAmortization", "DepreciationDepletionAndAmortization"],
    "SharesOutstanding": ["CommonStockSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic", "EntityCommonStockSharesOutstanding", "NumberOfSharesOutstanding"]
}

# Metrics Structs 
METRICS_CONCEPTS = {
    # Balance Sheet
    "TotalCurrentAssets": ["AssetsCurrent"],
    "TotalCash" : ["CashAndCashEquivalentsAtCarryingValue"],
    "TotalAssets": ["Assets"],
    "ShortTermDebt": ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"],
    "TotalCurrentLiabilities": ["LiabilitiesCurrent"],
    "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "TotalLiabilities": ["Liabilities"], 
    "StockholdersEquity": ["StockholdersEquity"],
    
    # Operations / Income Statement
    "Revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
    "ResearchAndDevelopment": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    "SalesAndMarketing": ["SellingAndMarketingExpense"],
    "GAndA": ["GeneralAndAdministrativeExpense"],
    "SalesMarketingAdministrativeExpenses": ["SellingGeneralAndAdministrativeExpense"],
    "CostOfRevenue": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold","CostOfRevenue"],
    "GrossProfit": ["GrossProfit"],
    "TotalOperatingExpenses": ["CostsAndExpenses", "OperatingExpenses"],
    "OperatingIncome": ["OperatingIncomeLoss"],
    "NonOperatingIncomeExpense": ["NonoperatingIncomeExpense"],
    "DepreciationAmortization": ["DepreciationAmortization", "DepreciationDepletionAndAmortization"],
    "NetIncome": ["NetIncomeLoss", "ProfitLoss"],
    "BasicEps": ["EarningsPerShareBasic", "BasicEarningsLossPerShare"],
    "DilutedEps": ["EarningsPerShareDiluted", "DilutedEarningsLossPerShare"],
    "SharesOutstandingBasic": ["WeightedAverageNumberOfSharesOutstandingBasic"],
    "SharesOutstandingDiluted": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "SharesOutstanding": ["CommonStockSharesOutstanding", "NumberOfSharesOutstanding"],
    
    # Cashflow
    "StockBasedCompensation": ["ShareBasedCompensation"],
    "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
    "DividendsPaid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "StockBuybacks": ["PaymentsForRepurchaseOfCommonStock"], 
    "CapitalExpenditures": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], # "PaymentsToAcquireProductiveAssets", "CapitalExpenditures"
    "InterestExpense": ["InterestExpense"]
    #"InterestPaid": ["CashPaidForInterest"], #TODO: Unsure and unnecessary
}

YFINANCE_METRICS = {
    # Balance Sheet
    "TotalCurrentAssets": ["Current Assets"],
    "TotalCash": ["Cash And Cash Equivalents"],
    "TotalAssets": ["Total Assets"],
    "ShortTermDebt": ["Current Debt"],  # or Current Debt And Capital Lease Obligation
    "TotalCurrentLiabilities": ["Current Liabilities"],
    "LongTermDebt": ["Long Term Debt"],
    "TotalLiabilities": ["Total Liabilities Net Minority Interest"],  # best approximation
    "StockholdersEquity": ["Stockholders Equity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    
    # Operations / Income Statement
    "Revenue": ["Total Revenue"],
    "ResearchAndDevelopment": ["Research And Development"],
    "CostOfRevenue": ["Cost Of Revenue"],
    "GrossProfit": ["Gross Profit"],
    "TotalOperatingExpenses": ["Total Expenses"],
    "OperatingIncome": ["Operating Income"],
    "NonOperatingIncomeExpense": ["Other Non Operating Income Expenses"],
    "DepreciationAmortization": ["Depreciation Amortization Depletion", "Depreciation And Amortization"],
    "NetIncome": ["Net Income"],
    "BasicEps": ["Basic EPS"],
    "DilutedEps": ["Diluted EPS"],
    "SharesOutstandingBasic": ["Basic Average Shares"],
    "SharesOutstandingDiluted": ["Diluted Average Shares"],
    "SharesOutstanding": [],  # sometimes not directly available
    
    # Cashflow
    "StockBasedCompensation": ["Stock Based Compensation"],
    "OperatingCashFlow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
    #"TotalCash": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
    "DividendsPaid": ["Cash Dividends Paid", "Common Stock Dividend Paid"],
    "StockBuybacks": ["Repurchase Of Capital Stock", "Common Stock Payments"],
    "CapitalExpenditures": ["Capital Expenditure", "Purchase Of PPE"],
    # Optional / advanced
    "FreeCashFlow": ["Free Cash Flow"],  # if you want to add
}


COMPANY_TAG_OVERRIDES = {
    "AAPL": {
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
    #     "columns": ["OperatingIncome", "TotalDebt", "StockholdersEquity", "TotalCash", "TaxRate"],
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
        "columns": ["OperatingIncome", "InterestExpense"],
        "func": lambda op_inc, interest: op_inc.div(interest.replace(0, pd.NA)) if interest is not None else pd.NA,
        "result_col": "InterestCoverage",
    },
    {
        "columns": ["LongTermDebt", "ShortTermDebt", "TotalCash", "OperatingIncome", "DepreciationAmortization"],
        "func": lambda ltd, std, cash, op_inc, dep: (
            (ltd.add(std, fill_value=0) - cash).div((op_inc + dep.fillna(0)).replace(0, pd.NA))
        ),
        "result_col": "NetDebtToEBITDA",
    },


    # -----------------------------------
    # CASH FLOW YIELDS
    # -----------------------------------
    {
        "columns": ["FreeCashFlow", "MarketCap"],
        "func": lambda fcf, mc: fcf.div(mc.replace(0, pd.NA)).mul(100),
        "result_col": "FCFYield",
    },
    {
        "columns": ["StockBasedCompensation", "FreeCashFlow", "MarketCap"],
        "func": lambda sbc, fcf, mc: (fcf.sub(sbc, fill_value=0)).div(mc.replace(0, pd.NA)).mul(100),
        "result_col": "SBCAdjustedFCFYield",
    },

    # -----------------------------------
    # VALUATION
    # -----------------------------------
    {
        "columns": ["MarketCap", "NetIncome"],
        "func": lambda mc, ni: mc.div(ni.replace(0, pd.NA)),
        "result_col": "PERatio",
    },

    {
        "columns": ["MarketCap", "ShortTermDebt", "LongTermDebt", "TotalCash", "OperatingIncome", "DepreciationAmortization"],
        "func": lambda mc, short_debt, long_debt, cash, op_inc, dep: (
            (mc + short_debt + long_debt - cash).div((op_inc + dep.fillna(0)).replace(0, pd.NA))
        ),
        "result_col": "EVToEBITDA",
    },
    {
        "columns": ["MarketCap", "TotalAssets", "TotalLiabilities"],
        "func": lambda mc, assets, liab: mc.div((assets - liab).replace(0, pd.NA)),
        "result_col": "PriceToBook",
    },
    # {
    #     "columns": ["PERatio", "EPSGrowth"],
    #     "func": lambda pe, growth: pe.div(growth.replace(0, pd.NA)).round(2),
    #     "result_col": "PEGRatio",
    # },
    {
        "columns": ["MarketCap", "ShortTermDebt", "LongTermDebt", "TotalCash", "Revenue"],
        "func": lambda mc, short_debt, long_debt, cash, rev: ((mc + short_debt + long_debt - cash).div(rev.replace(0, pd.NA))).round(2),
        "result_col": "EVToSales",
    }
]

