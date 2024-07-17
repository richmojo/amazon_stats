def create_fees(data, fba=False):
    fees = []
    for asin, details in data.items():
        new_dict = {}
        new_dict["id_type"] = "ASIN"
        new_dict["id_value"] = asin
        new_dict["price"] = details.get("cost", 0)

        if fba:
            new_dict["is_fba"] = True

        if new_dict["price"] == 0:
            continue

        fees.append(new_dict)

    return fees
