import requests
import json

# Extract list of conis and prices from Exchange ## Make a get request ##
# Retrieves summary information for each currency pair listed on the exchange. 
def get_coin_ticker(url): #(Exchange url)
    req = requests.get(url)
    json_resp = json.loads(req.text)
    return json_resp
    # print(json_resp) # Raw Data


# Loop through each objects and find the tradeable pairs & remove "isFrozen" & "postOnly" pairs
def collect_tradables(coin_obj): #structure_tradables
    coin_list = []
    for pairs in coin_obj:
        # print(coin) # Individual currency pair listed on the exchange
        is_frozen = coin_obj[pairs]["isFrozen"] #  	Indicates if this market is currently trading or not.
        is_post_only = coin_obj[pairs]["postOnly"] #  Indicates that orders posted to the market (new or move) must be non-matching orders (no taker orders). Any orders that would match will be rejected.
        highest_bid_not_zero = float(coin_obj[pairs]["highestBid"])
        lowestAsk_not_zero = float(coin_obj[pairs]["highestBid"])
        is_post_only = coin_obj[pairs]["postOnly"]
        
        if is_frozen == "0" and is_post_only == "0" and highest_bid_not_zero > 0 and lowestAsk_not_zero > 0:
            coin_list.append(pairs)
    return coin_list 
    # print(coin_list) # "isFrozen" & "postOnly" free pairs

# structure Arbitrage Pairs
def structure_triangular_pairs(coin_list):
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:] # Adjustables #
    
    # Get Pair A
    for pair_a in pairs_list: #Loop through data => make into a list
        pair_a_split = pair_a.split("_") # Split currency pair by "_" # List of Array [0, 1]
        a_base = pair_a_split[0] # Base is [0]
        a_quote = pair_a_split[1] # Quote is [1]
        # print(a_base, a_quote) #[A_Base, A_Quote]

        # Assign Pair A to a list
        a_pair_list = [a_base, a_quote]

        # Get Pair B
        for pair_b in pairs_list: # Keep in mind nested for loop
            pair_b_split = pair_b.split("_") # Split currency pair by "_" # List of Array [0, 1]
            b_base = pair_b_split[0] # Base is [0]
            b_quote = pair_b_split[1] # Quote is [1] 
            # print("B " + b_base, b_quote) #[B_Base, B_Quote]
            
            # Checkinng for Pair B
            if pair_a != pair_b:
                if b_base in a_pair_list or b_quote in a_pair_list: # loop through to see if any pair B have a common token with A
                    
                    # Get Pair C
                     for pair_c in pairs_list: # Keep in mind nested for loop
                        pair_c_split = pair_c.split("_") # Split currency pair by "_" # List of Array [0, 1]
                        c_base = pair_c_split[0] # Base is [0]
                        c_quote = pair_c_split[1] # Quote is [1] 
                        # print("C " + c_base, c_quote) #  [C_Base, C_Quote]

                        #Count the number of matcheing c items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            counts_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    counts_c_base += 1

                            counts_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    counts_c_quote += 1

                            # Determining Triangular Match
                            if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                                # print(pair_a, pair_b, pair_c) unfilter Tri pairs
                                combined = pair_a + "," + pair_b + "," + pair_c  # combined tri pair with ,
                                unique_item = "".join(sorted(combine_all))
                                
                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined,
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)

    return triangular_pairs_list
    # print(len(triangular_pairs_list))
    # print(triangular_pairs_list[0:3])

# Structure Prices                        
def get_price_for_tri_pair(t_pair, prices_json):
    
    # Extract Pair Info
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Price Information for Given Pairs
    pair_a_ask = float(prices_json[pair_a]["lowestAsk"]) #float to convert from string to int
    pair_a_bid = float(prices_json[pair_a]["highestBid"])
    # print(pair_a, pair_a_ask, pair_a_bid) # Pair A Ask & Bid price
    pair_b_ask = float(prices_json[pair_b]["lowestAsk"])
    pair_b_bid = float(prices_json[pair_b]["highestBid"])
    # print(pair_b, pair_b_ask, pair_b_bid) # Pair B Ask & Bid price
    pair_c_ask = float(prices_json[pair_c]["lowestAsk"])
    pair_c_bid = float(prices_json[pair_c]["highestBid"])
    # print(pair_c, pair_c_ask, pair_c_bid) # Pair C Ask & Bid price
    

    # Output Dictionary
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid,
        "pair_a_ask": t_pair["pair_a"] + " " + pair_a_ask,
        "pair_a_bid": t_pair["pair_a"] + " " + pair_a_bid,
        "pair_b_ask": t_pair["pair_b"] + " " + pair_b_ask,
        "pair_b_bid": t_pair["pair_b"] + " " + pair_b_bid,
        "pair_c_ask": t_pair["pair_c"] + " " + pair_c_ask,
        "pair_c_bid": t_pair["pair_c"] + " " + pair_c_bid
    }

# Calculate Surface Rate Arbitrage Opportunity
def calc_tri_surface_arb(t_pair, prices_dict):
    
    # Set Variables
    starting_amount = 1000  # Adjustables #
    min_surface_rate = 0 # initial Captial ()
    surface_dict = {} # list of tri pair data
    contract_2 = "" 
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    # Extract Pair Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Price Information
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]
    # print(t_pair["b_base"], b_ask)
    # Set directions and loop through
    direction_list = ["forward", "reverse"]
    for direction in direction_list:

        # Set additional varaiables for swap infirmation (which token/rate is been swap first and so forth)
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
        If we are swapping the coin on the left (base) to the right (quote) then * (1/ Ask)
        If we are swapping the coin on the right (quote) to the left (base) then * Bid
        """

        # Assume starting with a_base and swapping for a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_ask
            direction_trade_1 = "base_to_quote"

        # Assume starting with a_Quote and swapping for a_quote
        if direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = "quote_to_base"

        # Place first trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount * swap_1_rate
        # print(direction, pair_a, starting_amount, acquired_coin_t1)

        """  FORWARD  """
        # SCENARIO 1 Check if a_quote (acquired_coin) matches b_quote
        if direction == "forward":
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 2 Check if a_quote (acquired_coin) matches b_quote
        if direction == "forward": #53. 2:52
            if a_quote == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask # Delete listing from 
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 3 Check if a_quote (acquired_coin) matches c_quote
        if direction == "forward":
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base" # "base_to_quote" ??????
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 4 Check if a_quote (acquired_coin) matches c_base
        if direction == "forward": 
            if a_quote == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        """  REVERSE  """
        # SCENARIO 1 Check if a_base (acquired_coin) matches b_quote
        if direction == "reverse":
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 2 Check if a_base (acquired_coin) matches b_quote
        if direction == "reverse": 
            if a_base == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask 
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 3 Check if a_base (acquired_coin) matches c_quote
        if direction == "reverse":
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base" # "base_to_quote" ??????
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # SCENARIO 4 Check if a_base (acquired_coin) matches c_base
        if direction == "reverse": 
            if a_base == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

    # if acquired_coin_t3 > starting_amount:
    #             print("------------------------")
    #             print({
    #                 "askA": a_ask,
    #                 "askB": b_ask,
    #                 "askC": c_ask,
    #                 "bidA": a_bid,
    #                 "bidB": b_bid,
    #                 "bidC": c_bid,
    #                 "startingAmount" : starting_amount, 
    #                 "acquiredAmount": acquired_coin_t3,
    #                 "direction": direction, 
    #                 "pair_a": pair_a, 
    #                 "pair_b": pair_b, 
    #                 "pair_c": pair_c,
    #             })
    #             print("------------------------")    

            # print(direction, pair_a, pair_b, pair_c, starting_amount, acquired_coin_t3)

        """ PROFIT LOSS OUTPUT"""

        # Profit and Loss Calculation  
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_percent = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Trade Description
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1} {swap_2}."
        trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2} {swap_3}"
        trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3} {swap_1}."

        # if profit_loss > 0:
        #     print("------------------------")  
        #     print(trade_description_1)
        #     print(trade_description_2)
        #     print(trade_description_3)

        # Output Results
        if profit_loss_percent > min_surface_rate:
            surface_dict = {
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "starting_amount": starting_amount,
                "acquired_coin_t1": acquired_coin_t1,
                "acquired_coin_t2": acquired_coin_t2,
                "acquired_coin_t3": acquired_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "profit_loss": profit_loss,
                "profit_loss_perc": profit_loss_percent,
                "direction": direction,
                "trade_description_1": trade_description_1,
                "trade_description_2": trade_description_2,
                "trade_description_3": trade_description_3
            }

            return surface_dict

    return surface_dict