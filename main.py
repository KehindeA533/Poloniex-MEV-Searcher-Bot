# Step 0: Gather Correct Coins
import func_arbitrage
import json
import time

# Global Variable
coin_price_url = "https://poloniex.com/public?command=returnTicker"

'''
    Step 0: Finding coins which can be traded
    Exchange: Poloniex
    https://docs.legacy.poloniex.com/#public-http-api-methods
'''


def step_0():

    # Extract list of conis and prices from Exchange
    coin_json = func_arbitrage.get_coin_ticker(coin_price_url)
    # print(coin_json) # Raw Data

    # Loop through each objects and find the tradeable pairs
    coin_list = func_arbitrage.collect_tradables(coin_json)

    # Return list of tradeable coins
    return coin_list


""" 
    Step 1: Structuring Triangular Pairs
    Calculation Only
"""


def step_1(coin_list):

    # Structure the list tradeable triangular arbitrqage pairs
    structured_list = func_arbitrage.structure_triangular_pairs(coin_list)

    # Save structured list
    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(structured_list, fp)


""" 
    Step 2: Calculate Surface Arbitrage Opporunities
    Exchange: Poloniex
    https://docs.legacy.poloniex.com/#public-http-api-methods
"""


def step_2():

    # Get Structured Pairs
    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)
        # print(structured_pairs) # JSON tri pairs

        # Get Latest surface Prices
        prices_json = func_arbitrage.get_coin_ticker(
            coin_price_url)  # not actually the prices

        # Loop Through and Structure Price Information
        # while True:
        #     time.sleep(0.5)
        for t_pair in structured_pairs:
            prices_dict = func_arbitrage.get_price_for_tri_pair(
                t_pair, prices_json)  # Prices
            #    print(prices_dict)
            surface_arb = func_arbitrage.calc_tri_surface_arb(
                t_pair,  prices_dict)
            # if len(surface_arb) > 0:
            # print(surface_arb)


""" MAIN """
if __name__ == "__main__":
    coin_list = step_0()
    structured_pairs = step_1(coin_list)
    step_2()
