import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import logging
import warnings

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings('ignore')


def func_powerlaw(x, a, b, c):
    return a * np.exp(-b * x) + c


def get_token_frequency(contract_transactions: list, total_supply: int):
    token_list = [transaction["token_id"]
                  for transaction in contract_transactions]

    token_occurrence = {token_id: 0 for token_id in range(total_supply)}

    for token_id in token_list:
        token_occurrence[token_id] += 1

    token_frequency = {count: 0 for count in range(
        max(token_occurrence.values())+1)}

    for count in token_occurrence.values():
        token_frequency[count] += 1

    xdata = np.array(list(range(0, max(token_occurrence.values())+1)))
    ydata = np.array(list(token_frequency.values()))

    return xdata, ydata


def fit_powerlaw_model(xdata: list, ydata: list, contract_address: str) -> dict:
    # fit model
    popt, pcov = curve_fit(func_powerlaw, xdata, ydata)

    # calc r squared
    ydata_fit = func_powerlaw(xdata, *popt)
    ss_res = sum((ydata_fit-ydata)**2)
    ss_tot = sum((ydata-np.mean(ydata))**2)
    r_squared = 1-(ss_res/ss_tot)

    # calc standard deviation errors of parameters
    perr = np.sqrt(np.diag(pcov))

    return {
        "contract_address": contract_address,
        "popt": list(popt),
        "r_squared": r_squared,
        "standard deviation error": {
            "a": perr[0],
            "b": perr[1],
            "c": perr[2]
        }
    }


def create_contract_powerlaw_fit_chart(contract_transactions: list, contract_address: str, total_supply: int, file_path: str):
    xdata, ydata = get_token_frequency(contract_transactions, total_supply)
    fit = fit_powerlaw_model(xdata, ydata, contract_address)

    plt.figure(figsize=(12, 6))
    plt.plot(xdata, ydata, 'b-', label='data')
    plt.plot(xdata, func_powerlaw(xdata, *np.array(fit["popt"])), 'r-',
             label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(np.array(fit["popt"])))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(
        f"Research Question Token Evolution: Contract Powerlaw Fit\nContract: {contract_address}", {"fontsize": 10})
    plt.tight_layout()
    plt.legend()
    plt.savefig(
        f"{file_path}/cotract_powerlaw_fit_{contract_address}.png", format="PNG")

    logging.info("Contract Powerlaw Fit Chart created")


def fit_contract_powerlaw(contract_transactions: list, contract_address: str, total_supply: int) -> dict:
    xdata, ydata = get_token_frequency(contract_transactions, total_supply)

    fit = fit_powerlaw_model(xdata, ydata, contract_address)

    return fit


def fit_contract_list_powerlaw(transactions: list, contracts: list, contract_list: list) -> list:
    contract_fit_list = []

    for contract_address in [c["address"] for c in contract_list if c["collected"]]:
        contract_transactions = [
            t for t in transactions if t["contract_address"] == contract_address]

        contract_data = [
            c for c in contracts if c["contract_address"] == contract_address][0]

        total_supply = contract_data["total_supply"]

        if len(contract_transactions) != 0:
            try:
                contract_fit = fit_contract_powerlaw(
                    contract_transactions, contract_address, total_supply)

                contract_fit_list.append(contract_fit)

                logging.info(f"Contract Powerlaw Fit done: {contract_address}")
            except:
                logging.error(
                    f"Contract Powerlaw Fit error: {contract_address}")

    return contract_fit_list


def evaluate_contract_list_fit(contract_list_fit: list) -> dict:
    min_r_squared = 1
    max_r_squared = 0
    r_squared_list = []

    for contract_fit in contract_list_fit:
        if contract_fit["r_squared"] < min_r_squared:
            min_r_squared = contract_fit["r_squared"]
        if contract_fit["r_squared"] > max_r_squared:
            max_r_squared = contract_fit["r_squared"]
        r_squared_list.append(contract_fit["r_squared"])

    average_r_squared = sum(r_squared_list) / len(r_squared_list)

    percentile_25 = np.percentile(r_squared_list, 25)
    percentile_75 = np.percentile(r_squared_list, 75)
    percentile_95 = np.percentile(r_squared_list, 95)

    return {
        "contract_count": len(contract_list_fit),
        "min_r_squared": min_r_squared,
        "max_r_squared": max_r_squared,
        "average_r_squared": average_r_squared,
        "25th_percentile": percentile_25,
        "75th_percentile": percentile_75,
        "95th_percentile": percentile_95
    }


def create_contract_list_fit_chart(contract_list_fit_evaluation: dict, file_path: str):
    x_labels = [k for k, v in contract_list_fit_evaluation.items() if k !=
                "contract_count"]

    data = [round(v, 4) for k, v in contract_list_fit_evaluation.items() if k !=
            "contract_count"]

    x = np.arange(6)
    width = 0.3

    plt.figure(figsize=(12, 6))
    plt.bar(x, data, width)
    plt.xticks(x, x_labels)

    for i in range(len(x)):
        plt.text(i, data[i]/2, data[i], ha="center")

    plt.ylabel("r_squared")
    plt.title(f"Research Question Token Evolution: Contract List Powerlaw Fit (contract_count: {contract_list_fit_evaluation['contract_count']})", {
        "fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_list_power_law_fit.png", format="PNG")
    
    logging.info("Contract List Powerlaw Fit Chart created")
