"""
indian_markets.py
Utilities for detecting and handling Indian stock market tickers.
Supports both NSE (.NS) and BSE (.BO) listed companies.
Covers 150+ popular Indian companies across all sectors.
"""

import yfinance as yf

# ── Curated NSE ticker map for popular Indian companies ──────────────────────
# Key = common name/alias → Value = NSE ticker (with .NS suffix)
INDIA_NAME_TO_TICKER: dict[str, str] = {
    # ── Conglomerates / Blue-chips ────────────────────────────────────────────
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "ril": "RELIANCE.NS",
    "tata": "TCS.NS",
    "tcs": "TCS.NS",
    "tata consultancy": "TCS.NS",
    "tata consultancy services": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hcl": "HCLTECH.NS",
    "hcl tech": "HCLTECH.NS",
    "hcltech": "HCLTECH.NS",
    "hcl technologies": "HCLTECH.NS",
    "tech mahindra": "TECHM.NS",
    "techm": "TECHM.NS",
    "mphasis": "MPHASIS.NS",
    "ltimindtree": "LTIM.NS",
    "lti mindtree": "LTIM.NS",
    "lti": "LTIM.NS",
    "persistent": "PERSISTENT.NS",
    "persistent systems": "PERSISTENT.NS",
    "coforge": "COFORGE.NS",
    "hexaware": "HEXT.NS",
    "oracle financial": "OFSS.NS",
    "ofss": "OFSS.NS",

    # ── Banking & Finance ─────────────────────────────────────────────────────
    "nippon": "NAM-INDIA.NS",
    "nippon india": "NAM-INDIA.NS",
    "nippon life": "NAM-INDIA.NS",
    "nippon amc": "NAM-INDIA.NS",
    "nam-india": "NAM-INDIA.NS",
    "namindia": "NAM-INDIA.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfcbank": "HDFCBANK.NS",
    "hdfc": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icicibank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "state bank": "SBIN.NS",
    "state bank of india": "SBIN.NS",
    "sbin": "SBIN.NS",
    "axis bank": "AXISBANK.NS",
    "axisbank": "AXISBANK.NS",
    "kotak": "KOTAKBANK.NS",
    "kotak bank": "KOTAKBANK.NS",
    "kotak mahindra": "KOTAKBANK.NS",
    "kotakbank": "KOTAKBANK.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bajfinance": "BAJFINANCE.NS",
    "bajaj finserv": "BAJAJFINSV.NS",
    "bajajfinsv": "BAJAJFINSV.NS",
    "indusind bank": "INDUSINDBK.NS",
    "indusindbk": "INDUSINDBK.NS",
    "yes bank": "YESBANK.NS",
    "yesbank": "YESBANK.NS",
    "bandhan bank": "BANDHANBNK.NS",
    "bandhan": "BANDHANBNK.NS",
    "idfc first": "IDFCFIRSTB.NS",
    "idfcfirstb": "IDFCFIRSTB.NS",
    "federal bank": "FEDERALBNK.NS",
    "federalbnk": "FEDERALBNK.NS",
    "pnb": "PNB.NS",
    "punjab national bank": "PNB.NS",
    "bank of baroda": "BANKBARODA.NS",
    "bob": "BANKBARODA.NS",
    "canara bank": "CANBK.NS",
    "canbk": "CANBK.NS",
    "union bank": "UNIONBANK.NS",
    "shriram finance": "SHRIRAMFIN.NS",
    "shriramfin": "SHRIRAMFIN.NS",
    "muthoot finance": "MUTHOOTFIN.NS",
    "muthootfin": "MUTHOOTFIN.NS",
    "hdfc amc": "HDFCAMC.NS",
    "hdfcamc": "HDFCAMC.NS",
    "sbi cards": "SBICARD.NS",
    "sbicard": "SBICARD.NS",
    "manappuram": "MANAPPURAM.NS",
    "cholamandalam": "CHOLAFIN.NS",
    "cholafin": "CHOLAFIN.NS",
    "microfinance": "CreditAccess",
    "creditaccess": "CREDITACC.NS",
    "piramal": "PVRL.NS",
    "piramal enterprises": "PEL.NS",
    "pel": "PEL.NS",
    "l&t finance": "LTF.NS",
    "ltf": "LTF.NS",

    # ── Insurance ────────────────────────────────────────────────────────────
    "hdfc life": "HDFCLIFE.NS",
    "hdfclife": "HDFCLIFE.NS",
    "sbi life": "SBILIFE.NS",
    "sbilife": "SBILIFE.NS",
    "icici lombard": "ICICIGI.NS",
    "icicigi": "ICICIGI.NS",
    "icici prudential": "ICICIPRULI.NS",
    "icicipruli": "ICICIPRULI.NS",
    "max life": "MAXLIFE",
    "lic": "LICI.NS",
    "lici": "LICI.NS",
    "star health": "STARHEALTH.NS",
    "go digit": "GODIGIT.NS",
    "niacl": "NIACL.NS",

    # ── Auto ─────────────────────────────────────────────────────────────────
    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",
    "tata motors": "TATAMOTORS.NS",
    "tatamotors": "TATAMOTORS.NS",
    "mahindra": "M&M.NS",
    "m&m": "M&M.NS",
    "hero motocorp": "HEROMOTOCO.NS",
    "heromotoco": "HEROMOTOCO.NS",
    "hero": "HEROMOTOCO.NS",
    "bajaj auto": "BAJAJ-AUTO.NS",
    "bajajauto": "BAJAJ-AUTO.NS",
    "eicher motors": "EICHERMOT.NS",
    "eichermot": "EICHERMOT.NS",
    "royal enfield": "EICHERMOT.NS",
    "tvs motor": "TVSMOTOR.NS",
    "tvsmotor": "TVSMOTOR.NS",
    "ashok leyland": "ASHOKLEY.NS",
    "ashokley": "ASHOKLEY.NS",
    "force motors": "FORCEMOT.NS",
    "motherson": "MOTHERSON.NS",
    "bosch": "BOSCHLTD.NS",
    "boschltd": "BOSCHLTD.NS",
    "mrf": "MRF.NS",
    "apollo tyres": "APOLLOTYRE.NS",
    "ceat tyres": "CEATLTD.NS",
    "ola electric": "OLAELEC.NS",

    # ── Pharma & Healthcare ───────────────────────────────────────────────────
    "sun pharma": "SUNPHARMA.NS",
    "sunpharma": "SUNPHARMA.NS",
    "sun pharmaceutical": "SUNPHARMA.NS",
    "dr reddy": "DRREDDY.NS",
    "dr. reddys": "DRREDDY.NS",
    "drreddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "divi's": "DIVISLAB.NS",
    "divis": "DIVISLAB.NS",
    "divislab": "DIVISLAB.NS",
    "lupin": "LUPIN.NS",
    "aurobindo": "AUROPHARMA.NS",
    "auropharma": "AUROPHARMA.NS",
    "biocon": "BIOCON.NS",
    "zydus": "ZYDUSLIFE.NS",
    "zyduslife": "ZYDUSLIFE.NS",
    "alkem": "ALKEM.NS",
    "torrent pharma": "TORNTPHARM.NS",
    "torntpharm": "TORNTPHARM.NS",
    "ipca": "IPCALAB.NS",
    "abbott india": "ABBOTINDIA.NS",
    "abbotindia": "ABBOTINDIA.NS",
    "pfizer india": "PFIZER.NS",
    "pfizer": "PFIZER.NS",
    "apollo hospitals": "APOLLOHOSP.NS",
    "apollohosp": "APOLLOHOSP.NS",
    "apollo": "APOLLOHOSP.NS",
    "fortis": "FORTIS.NS",
    "max healthcare": "MAXHEALTH.NS",
    "maxhealth": "MAXHEALTH.NS",
    "narayana hrudayalaya": "NH.NS",
    "nh": "NH.NS",
    "manipal": "MEDANTA.NS",
    "medanta": "MEDANTA.NS",
    "aster dm": "ASTERDM.NS",
    "asterdm": "ASTERDM.NS",

    # ── Energy / Oil & Gas / Power ────────────────────────────────────────────
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "power grid": "POWERGRID.NS",
    "powergrid": "POWERGRID.NS",
    "adani green": "ADANIGREEN.NS",
    "adanigreen": "ADANIGREEN.NS",
    "adani ports": "ADANIPORTS.NS",
    "adaniports": "ADANIPORTS.NS",
    "adani enterprises": "ADANIENT.NS",
    "adanient": "ADANIENT.NS",
    "adani total gas": "ATGL.NS",
    "atgl": "ATGL.NS",
    "adani power": "ADANIPOWER.NS",
    "adanipower": "ADANIPOWER.NS",
    "adani wilmar": "AWL.NS",
    "awl": "AWL.NS",
    "adani": "ADANIENT.NS",
    "tata power": "TATAPOWER.NS",
    "tatapower": "TATAPOWER.NS",
    "coal india": "COALINDIA.NS",
    "coalindia": "COALINDIA.NS",
    "bpcl": "BPCL.NS",
    "bharat petroleum": "BPCL.NS",
    "ioc": "IOC.NS",
    "indian oil": "IOC.NS",
    "hpcl": "HPCL.NS",
    "hindustan petroleum": "HPCL.NS",
    "gail": "GAIL.NS",
    "petronet lng": "PETRONET.NS",
    "petronet": "PETRONET.NS",
    "jsw energy": "JSWENERGY.NS",
    "jswenergy": "JSWENERGY.NS",
    "torrent power": "TORNTPOWER.NS",
    "torntpower": "TORNTPOWER.NS",
    "nhpc": "NHPC.NS",
    "sjvn": "SJVN.NS",
    "abb india": "ABB.NS",
    "abb": "ABB.NS",
    "siemens": "SIEMENS.NS",
    "thermax": "THERMAX.NS",
    "bhel": "BHEL.NS",
    "bharat heavy electricals": "BHEL.NS",
    "cesc": "CESC.NS",
    "npcil": "NPCIL.NS",
    "ireda": "IREDA.NS",

    # ── FMCG / Consumer ───────────────────────────────────────────────────────
    "hindustan unilever": "HINDUNILVR.NS",
    "hul": "HINDUNILVR.NS",
    "hindunilvr": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "nestle india": "NESTLEIND.NS",
    "nestleind": "NESTLEIND.NS",
    "britannia": "BRITANNIA.NS",
    "dabur": "DABUR.NS",
    "marico": "MARICO.NS",
    "godrej consumer": "GODREJCP.NS",
    "godrejcp": "GODREJCP.NS",
    "colgate": "COLPAL.NS",
    "colpal": "COLPAL.NS",
    "emami": "EMAMILTD.NS",
    "emamiltd": "EMAMILTD.NS",
    "jyothy labs": "JYOTHYLAB.NS",
    "jyothylab": "JYOTHYLAB.NS",
    "vbl": "VBL.NS",
    "varun beverages": "VBL.NS",
    "united spirits": "MCDOWELL-N.NS",
    "radico": "RADICO.NS",
    "tata consumer": "TATACONSUM.NS",
    "tataconsum": "TATACONSUM.NS",
    "bajaj consumer": "BAJAJCON.NS",
    "patanjali": "PATANJALI.NS",
    "dmart": "DMART.NS",
    "avenue supermarts": "DMART.NS",
    "avenue": "DMART.NS",
    "zomato": "ZOMATO.NS",
    "swiggy": "SWIGGY.NS",
    "nykaa": "NYKAA.NS",
    "fss nykaa": "NYKAA.NS",
    "meesho": "MEESHO.NS",

    # ── Telecom / Media / Internet ────────────────────────────────────────────
    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "bhartiartl": "BHARTIARTL.NS",
    "jio": "RELIANCE.NS",
    "vodafone idea": "IDEA.NS",
    "vi": "IDEA.NS",
    "idea": "IDEA.NS",
    "bsnl": "BSNL.NS",
    "zee entertainment": "ZEEL.NS",
    "zeel": "ZEEL.NS",
    "sun tv": "SUNTV.NS",
    "suntv": "SUNTV.NS",
    "dish tv": "DISHTV.NS",
    "dishtv": "DISHTV.NS",
    "hathway": "HATHWAY.NS",
    "siti networks": "SITINET.NS",
    "indiamart": "INDIAMART.NS",
    "info edge": "NAUKRI.NS",
    "naukri": "NAUKRI.NS",
    "infoedge": "NAUKRI.NS",
    "justdial": "JUSTDIAL.NS",
    "paytm": "PAYTM.NS",
    "one97": "PAYTM.NS",
    "policybazaar": "POLICYBZR.NS",
    "policybzr": "POLICYBZR.NS",
    "mobikwik": "MBL.NS",
    "ixigo": "IXIGO.NS",
    "ola": "OLAELEC.NS",
    "mmt": "MAKEMYTRIP",

    # ── Cement / Infra / Construction ────────────────────────────────────────
    "ultratech cement": "ULTRACEMCO.NS",
    "ultracemco": "ULTRACEMCO.NS",
    "ultratech": "ULTRACEMCO.NS",
    "grasim": "GRASIM.NS",
    "l&t": "LT.NS",
    "larsen": "LT.NS",
    "larsen & toubro": "LT.NS",
    "larsen and toubro": "LT.NS",
    "lt": "LT.NS",
    "shree cement": "SHREECEM.NS",
    "shreecem": "SHREECEM.NS",
    "ambuja cement": "AMBUJACEM.NS",
    "ambujacem": "AMBUJACEM.NS",
    "acc cement": "ACC.NS",
    "acc": "ACC.NS",
    "ramco cement": "RAMCOCEM.NS",
    "jk cement": "JKCEMENT.NS",
    "dalmia bharat": "DALBHARAT.NS",
    "dalbharat": "DALBHARAT.NS",
    "ncc": "NCC.NS",
    "rites": "RITES.NS",
    "ircon": "IRCON.NS",
    "gmr airports": "GMRINFRA.NS",
    "gmrinfra": "GMRINFRA.NS",
    "irb infra": "IRB.NS",
    "irb": "IRB.NS",
    "knr constructions": "KNRCON.NS",
    "dilip buildcon": "DBL.NS",
    "ashoka buildcon": "ASHOKA.NS",
    "psp projects": "PSPPROJECT.NS",
    "capacit'e": "CAPACITE.NS",

    # ── Steel / Metals / Mining ───────────────────────────────────────────────
    "tata steel": "TATASTEEL.NS",
    "tatasteel": "TATASTEEL.NS",
    "jsw steel": "JSWSTEEL.NS",
    "jswsteel": "JSWSTEEL.NS",
    "hindalco": "HINDALCO.NS",
    "vedanta": "VEDL.NS",
    "vedl": "VEDL.NS",
    "sail": "SAIL.NS",
    "steel authority": "SAIL.NS",
    "nalco": "NALCO.NS",
    "national aluminium": "NALCO.NS",
    "nmdc": "NMDC.NS",
    "hindustan zinc": "HINDZINC.NS",
    "hindzinc": "HINDZINC.NS",
    "jindal steel": "JINDALSTEL.NS",
    "jindalstel": "JINDALSTEL.NS",
    "jsw": "JSWSTEEL.NS",
    "ratnamani metals": "RATNAMANI.NS",
    "sandur manganese": "SANDUMA.NS",

    # ── Chemicals / Specialty ─────────────────────────────────────────────────
    "pidilite": "PIDILITIND.NS",
    "pidilitind": "PIDILITIND.NS",
    "asian paints": "ASIANPAINT.NS",
    "asianpaint": "ASIANPAINT.NS",
    "berger paints": "BERGEPAINT.NS",
    "bergepaint": "BERGEPAINT.NS",
    "kansai nerolac": "KANSAINER.NS",
    "navin fluorine": "NAVINFLUOR.NS",
    "navinfluor": "NAVINFLUOR.NS",
    "aarti industries": "AARTIIND.NS",
    "aartiind": "AARTIIND.NS",
    "srf": "SRF.NS",
    "laxmi organic": "LXCHEM.NS",
    "lxchem": "LXCHEM.NS",
    "tata chemicals": "TATACHEM.NS",
    "tatachem": "TATACHEM.NS",
    "deepak nitrite": "DEEPAKNTR.NS",
    "deepakntr": "DEEPAKNTR.NS",
    "clean science": "CLEAN.NS",
    "solar industries": "SOLARINDS.NS",
    "solarinds": "SOLARINDS.NS",
    "finolex industries": "FINPIPE.NS",
    "prince pipes": "PRINCEPIPE.NS",

    # ── Capital Goods / Defence ───────────────────────────────────────────────
    "bharat electronics": "BEL.NS",
    "bel": "BEL.NS",
    "hal": "HAL.NS",
    "hindustan aeronautics": "HAL.NS",
    "bfl": "BFL.NS",
    "bharat forge": "BHARATFORG.NS",
    "bharatforg": "BHARATFORG.NS",
    "cg power": "CGPOWER.NS",
    "cgpower": "CGPOWER.NS",
    "hitachi energy": "POWERINDIA.NS",
    "bharat dynamics": "BDL.NS",
    "bdl": "BDL.NS",
    "mazagon dock": "MAZDOCK.NS",
    "mazdock": "MAZDOCK.NS",
    "cochin shipyard": "COCHINSHIP.NS",
    "cochinship": "COCHINSHIP.NS",
    "garden reach": "GRSE.NS",
    "grse": "GRSE.NS",
    "astra microwave": "ASTRAMICRO.NS",
    "paras defence": "PARASDEFE.NS",
    "data patterns": "DATAPATTNS.NS",

    # ── Retail / Consumer Discretionary ──────────────────────────────────────
    "titan": "TITAN.NS",
    "trent": "TRENT.NS",
    "kalyan jewellers": "KALYANKJIL.NS",
    "kalyankjil": "KALYANKJIL.NS",
    "pcjeweller": "PCJEWELLER.NS",
    "vedant fashions": "MANYAVAR.NS",
    "manyavar": "MANYAVAR.NS",
    "aditya birla fashion": "ABFRL.NS",
    "abfrl": "ABFRL.NS",
    "page industries": "PAGEIND.NS",
    "pageind": "PAGEIND.NS",
    "relaxo footwear": "RELAXO.NS",
    "bata india": "BATAIND.NS",
    "bataind": "BATAIND.NS",
    "shoppers stop": "SHOPERSTOP.NS",
    "shoperstop": "SHOPERSTOP.NS",
    "westlife": "WESTLIFE.NS",
    "restaurant brands": "RBA.NS",
    "devyani international": "DEVYANI.NS",
    "sapphire foods": "SAPPHIRE.NS",
    "jubilant foodworks": "JUBLFOOD.NS",
    "jublfood": "JUBLFOOD.NS",
    "dominos india": "JUBLFOOD.NS",

    # ── Real Estate ───────────────────────────────────────────────────────────
    "dlf": "DLF.NS",
    "godrej properties": "GODREJPROP.NS",
    "godrejprop": "GODREJPROP.NS",
    "oberoi realty": "OBEROIRLTY.NS",
    "oberoirlty": "OBEROIRLTY.NS",
    "prestige estates": "PRESTIGE.NS",
    "prestige": "PRESTIGE.NS",
    "brigade enterprises": "BRIGADE.NS",
    "brigade": "BRIGADE.NS",
    "sobha": "SOBHA.NS",
    "puravankara": "PURVA.NS",
    "lodha": "LODHA.NS",
    "macrotech": "LODHA.NS",
    "phoenix mills": "PHOENIXLTD.NS",
    "phoenixltd": "PHOENIXLTD.NS",
    "embassy reit": "EMBASSY.NS",
    "mindspace reit": "MINDSPACE.NS",

    # ── Logistics / Aviation ──────────────────────────────────────────────────
    "interglobe aviation": "INDIGO.NS",
    "indigo": "INDIGO.NS",
    "spicejet": "SPICEJET.NS",
    "air india": "AIRINDIA.NS",
    "blue dart": "BLUEDART.NS",
    "bluedart": "BLUEDART.NS",
    "container corporation": "CONCOR.NS",
    "concor": "CONCOR.NS",
    "gati": "GATI.NS",
    "tvs supply chain": "TVSSCL.NS",
    "tvsscl": "TVSSCL.NS",
    "mahindra logistics": "MAHLOG.NS",

    # ── Indices (informational, not analyzable but shown in tape) ─────────────
    "nifty": "^NSEI",
    "nifty 50": "^NSEI",
    "sensex": "^BSESN",
    "bank nifty": "^NSEBANK",
    "nifty bank": "^NSEBANK",
}

# All known NSE-suffix tickers that are definitely Indian
NSE_SUFFIX = ".NS"
BSE_SUFFIX = ".BO"

# Known NSE stock symbols (without suffix) for instant detection
_KNOWN_NSE_SYMBOLS = {
    "RELIANCE", "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM",
    "MPHASIS", "LTIM", "PERSISTENT", "COFORGE", "OFSS",
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK",
    "BAJFINANCE", "BAJAJFINSV", "INDUSINDBK", "BANDHANBNK",
    "YESBANK", "IDFCFIRSTB", "FEDERALBNK", "PNB", "BANKBARODA",
    "CANBK", "UNIONBANK", "SHRIRAMFIN", "MUTHOOTFIN", "HDFCAMC",
    "SBICARD", "LICI", "HDFCLIFE", "SBILIFE", "ICICIGI", "ICICIPRULI",
    "MARUTI", "TATAMOTORS", "HEROMOTOCO", "EICHERMOT", "TVSMOTOR",
    "ASHOKLEY", "MOTHERSON", "BOSCHLTD", "MRF", "APOLLOTYRE",
    "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP",
    "LUPIN", "AUROPHARMA", "BIOCON", "ZYDUSLIFE", "ALKEM",
    "TORNTPHARM", "FORTIS", "MAXHEALTH", "NH", "MEDANTA", "ASTERDM",
    "ONGC", "NTPC", "POWERGRID", "ADANIGREEN", "ADANIPORTS",
    "ADANIENT", "TATAPOWER", "COALINDIA", "BPCL", "IOC", "HPCL",
    "GAIL", "PETRONET", "JSWENERGY", "TORNTPOWER", "NHPC", "SJVN",
    "ABB", "SIEMENS", "THERMAX", "BHEL", "IREDA",
    "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
    "MARICO", "GODREJCP", "COLPAL", "EMAMILTD", "VBL", "TATACONSUM",
    "DMART", "ZOMATO", "NYKAA", "SWIGGY",
    "BHARTIARTL", "IDEA", "ZEEL", "SUNTV", "NAUKRI", "INDIAMART",
    "JUSTDIAL", "PAYTM", "POLICYBZR", "IXIGO",
    "ULTRACEMCO", "GRASIM", "LT", "SHREECEM", "AMBUJACEM", "ACC",
    "RAMCOCEM", "JKCEMENT", "DALBHARAT", "NCC", "RITES", "IRCON",
    "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "NALCO",
    "NMDC", "HINDZINC", "JINDALSTEL",
    "PIDILITIND", "ASIANPAINT", "BERGEPAINT", "SRF", "AARTIIND",
    "NAVINFLUOR", "TATACHEM", "DEEPAKNTR", "CLEAN", "SOLARINDS",
    "BEL", "HAL", "BHARATFORG", "CGPOWER", "BDL", "MAZDOCK",
    "COCHINSHIP", "GRSE",
    "TITAN", "TRENT", "KALYANKJIL", "MANYAVAR", "ABFRL", "PAGEIND",
    "RELAXO", "BATAIND", "JUBLFOOD", "DEVYANI",
    "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE",
    "SOBHA", "LODHA", "PHOENIXLTD",
    "INDIGO", "SPICEJET", "BLUEDART", "CONCOR",
    "M&M", "BAJAJ-AUTO", "NAM-INDIA",
    "ATGL", "ADANIPOWER", "AWL", "STARHEALTH", "GODIGIT",
    "LTF", "CHOLAFIN", "MANAPPURAM",
    "OLAELEC", "TVSSCL",
}


def is_indian_ticker(ticker: str) -> bool:
    """Return True if the ticker is identified as an Indian stock."""
    t = ticker.upper().strip()
    if t.endswith(NSE_SUFFIX) or t.endswith(".BO"):
        return True
    # Bare symbol that matches known NSE list
    if t in _KNOWN_NSE_SYMBOLS:
        return True
    return False


def _yfinance_resolve(query: str) -> str | None:
    """
    Try to resolve an unknown Indian company name via yfinance.
    Appends .NS and verifies that yfinance returns valid data.
    Returns the canonical ticker on success, None on failure.
    """
    # Normalise to a likely NSE symbol: uppercase, spaces → nothing
    candidate = query.upper().replace(" ", "")
    candidates = [
        f"{candidate}.NS",
        f"{candidate}.BO",
    ]
    for sym in candidates:
        try:
            info = yf.Ticker(sym).fast_info
            # fast_info has last_price if data is available
            price = getattr(info, "last_price", None)
            if price is not None and price > 0:
                return sym
        except Exception:
            pass
    return None


def resolve_indian_ticker(ticker: str) -> str:
    """
    Given a raw input (company name, bare NSE symbol, or full ticker),
    return the canonical yfinance-compatible ticker string.

    Resolution order:
    1. Static name map   (e.g. "reliance" → "RELIANCE.NS")
    2. Already has .NS / .BO suffix → return as-is
    3. Bare symbol in known NSE set → append .NS
    4. yfinance dynamic lookup — validates the ticker returns real data
    5. Fall through → return input unchanged (US stock or unknown)

    Examples:
        "reliance"        → "RELIANCE.NS"
        "HDFC Bank"       → "HDFCBANK.NS"
        "Zomato"          → "ZOMATO.NS"
        "RELIANCE.NS"     → "RELIANCE.NS"
        "TCS.BO"          → "TCS.BO"
        "AAPL"            → "AAPL"
    """
    t_lower = ticker.lower().strip()

    # 1. Check name map first (handles "Reliance Industries", "HDFC Bank" etc.)
    if t_lower in INDIA_NAME_TO_TICKER:
        return INDIA_NAME_TO_TICKER[t_lower]

    t_upper = ticker.upper().strip()

    # 2. Already has suffix → return as-is
    if t_upper.endswith(NSE_SUFFIX) or t_upper.endswith(".BO"):
        return t_upper

    # 3. Bare symbol in the known NSE list → append .NS
    if t_upper in _KNOWN_NSE_SYMBOLS:
        return f"{t_upper}{NSE_SUFFIX}"

    # 4. Dynamic yfinance resolution for unknown Indian companies
    #    Only attempt this for queries that look like Indian names
    #    (heuristic: contains no dots, not a 4-5 char all-caps US ticker
    #     that doesn't end in .NS/.BO)
    is_likely_indian_query = (
        "." not in t_upper and
        len(t_upper.replace(" ", "")) >= 3 and
        # If it's a short all-caps ticker like "AAPL", skip yfinance probe
        # because it wastes time. Only probe if there's a space or it's longer.
        (" " in ticker or len(t_upper) > 5)
    )
    if is_likely_indian_query:
        resolved = _yfinance_resolve(ticker)
        if resolved:
            return resolved

    # 5. Not identified as Indian → return unchanged (assumed US ticker)
    return ticker.strip()


def get_currency_symbol(ticker: str) -> str:
    """Return '₹' for Indian tickers, '$' for everything else."""
    t = ticker.upper().strip()
    if t.endswith(NSE_SUFFIX) or t.endswith(".BO"):
        return "₹"
    if t in _KNOWN_NSE_SYMBOLS:
        return "₹"
    return "$"


# ── Indian ticker tape symbols ───────────────────────────────────────────────
INDIAN_TAPE_SYMBOLS = [
    "^NSEI",          # NIFTY 50
    "^BSESN",         # SENSEX
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "BHARTIARTL.NS",
    "WIPRO.NS",
    "SBIN.NS",
    "ZOMATO.NS",
    "ADANIENT.NS",
]

# ── Indian peer map for popular NSE stocks ───────────────────────────────────
INDIA_PEER_MAP: dict[str, list[str]] = {
    "RELIANCE.NS": ["ONGC.NS", "BPCL.NS"],
    "TCS.NS":      ["INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
    "INFY.NS":     ["TCS.NS", "HCLTECH.NS", "WIPRO.NS"],
    "WIPRO.NS":    ["TCS.NS", "TECHM.NS", "HCLTECH.NS"],
    "HCLTECH.NS":  ["TCS.NS", "WIPRO.NS", "MPHASIS.NS"],
    "TECHM.NS":    ["WIPRO.NS", "HCLTECH.NS", "MPHASIS.NS"],
    "MPHASIS.NS":  ["COFORGE.NS", "PERSISTENT.NS", "TECHM.NS"],
    "PERSISTENT.NS":["MPHASIS.NS", "COFORGE.NS", "LTIM.NS"],
    "HDFCBANK.NS": ["ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "ICICIBANK.NS":["HDFCBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "SBIN.NS":     ["HDFCBANK.NS", "AXISBANK.NS", "PNB.NS"],
    "AXISBANK.NS": ["ICICIBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"],
    "KOTAKBANK.NS":["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS"],
    "BAJFINANCE.NS":["BAJAJFINSV.NS", "HDFCBANK.NS", "SHRIRAMFIN.NS"],
    "MARUTI.NS":   ["TATAMOTORS.NS", "M&M.NS", "EICHERMOT.NS"],
    "TATAMOTORS.NS":["MARUTI.NS", "M&M.NS", "TVSMOTOR.NS"],
    "SUNPHARMA.NS":["DRREDDY.NS", "CIPLA.NS", "LUPIN.NS"],
    "DRREDDY.NS":  ["SUNPHARMA.NS", "CIPLA.NS", "AUROPHARMA.NS"],
    "CIPLA.NS":    ["SUNPHARMA.NS", "DRREDDY.NS", "LUPIN.NS"],
    "BHARTIARTL.NS":["RELIANCE.NS", "IDEA.NS"],
    "HINDUNILVR.NS":["ITC.NS", "NESTLEIND.NS", "DABUR.NS"],
    "ITC.NS":      ["HINDUNILVR.NS", "BRITANNIA.NS", "DABUR.NS"],
    "LT.NS":       ["ULTRACEMCO.NS", "GRASIM.NS", "NCC.NS"],
    "TATASTEEL.NS":["JSWSTEEL.NS", "HINDALCO.NS", "SAIL.NS"],
    "ADANIGREEN.NS":["NTPC.NS", "TATAPOWER.NS", "JSWEN ERGY.NS"],
    "ADANIPORTS.NS":["LT.NS", "CONCOR.NS"],
    "BAJFINANCE.NS":["BAJAJFINSV.NS", "HDFCBANK.NS"],
    "NTPC.NS":     ["POWERGRID.NS", "TATAPOWER.NS", "NHPC.NS"],
    "ONGC.NS":     ["BPCL.NS", "COALINDIA.NS", "IOC.NS"],
    "ZOMATO.NS":   ["SWIGGY.NS", "JUBLFOOD.NS", "DEVYANI.NS"],
    "DLF.NS":      ["GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"],
    "ASIANPAINT.NS":["BERGEPAINT.NS", "PIDILITIND.NS"],
    "TITAN.NS":    ["KALYANKJIL.NS", "MANYAVAR.NS", "TRENT.NS"],
    "APOLLOHOSP.NS":["FORTIS.NS", "MAXHEALTH.NS", "NH.NS"],
}
