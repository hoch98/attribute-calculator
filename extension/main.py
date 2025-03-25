import requests, json

starting_armour = {
  "tier": "burning",
  "type": "aurora",
  "piece": "boots",
  "attr1": ["dominance", 2, 10],
  "attr2": ["mending", 2, 10]
}

types = ["aurora", "crimson", "fervor", "hollow", "terror"]

attribute1_prices = [[]]
attribute2_prices = [[]]

for i in range(starting_armour["attr1"][2]):
    
  level_prices1 = []
  level_prices2 = []

  for type in types:
    armour_tag = (type+"_"+starting_armour["piece"]).upper()
    print(armour_tag, starting_armour['attr1'][0], i+1)

    url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{starting_armour['attr1'][0]}={str(i+1)}"
    response = requests.request("GET", url)

    response = [{
      "attributes" : product["nbtData"]["data"]["attributes"],
      "startingBid": product["startingBid"],
      "uuid": product["uuid"],
      "type": armour_tag
    } for product in response.json()]

    level_prices1 += response

    print(armour_tag, starting_armour['attr2'][0], i+1)

    url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{starting_armour['attr2'][0]}={str(i+1)}"
    response = requests.request("GET", url)
    new_response = []

    for product in response.json():
      if product not in level_prices1:
        new_response.append({
          "attributes" : product["nbtData"]["data"]["attributes"],
          "startingBid": product["startingBid"],
          "uuid": product["uuid"],
          "type": armour_tag
        })

    level_prices2 += new_response

  #attribute shards

  url = f"https://sky.coflnet.com/api/auctions/tag/ATTRIBUTE_SHARD/active/bin?{starting_armour['attr1'][0]}={str(i+1)}"
  response = requests.request("GET", url)
  level_prices1 += [
    {
      "attributes": {
        starting_armour["attr1"][0]: i+1
      },
      "startingBid": product["startingBid"],
      "uuid": product["uuid"],
      "type": "ATTRIBUTE_SHARD"
    } for product in response.json()
  ]

  url = f"https://sky.coflnet.com/api/auctions/tag/ATTRIBUTE_SHARD/active/bin?{starting_armour['attr2'][0]}={str(i+1)}"
  response = requests.request("GET", url)
  level_prices2 += [
    {
      "attributes": {
        starting_armour["attr2"][0]: i+1
      },
      "startingBid": product["startingBid"],
      "uuid": product["uuid"],
      "type": "ATTRIBUTE_SHARD"
    } for product in response.json()
  ]

  attribute1_prices.append(level_prices1)
  attribute2_prices.append(level_prices2)

def cost(l, prices, attribute, stack=[]):
    rl = stack.copy()
    if l == 1:
        if prices[1] == []:
            return []
        shard = prices[1].pop(0)
        rl.append(shard)
        return rl
    
    t1 = cost(l-1, prices, attribute, rl)
    t2 = cost(l-1, prices, attribute, rl)
    compareStack = t1+t2
    ranOut = t1 == [] or t2 == []
    noCurrent = prices[l] == []
    if ranOut and not noCurrent:
        rl.append(prices[l].pop(0))
        for i in compareStack:
            tier = i["attributes"][attribute]
            prices[tier].append(i)
            prices[tier] = sorted(prices[tier], key=lambda x: x["startingBid"])
        return rl
    if noCurrent and not ranOut:
        return compareStack
    if noCurrent and ranOut:
        return []
    if prices[l][0]["startingBid"] <= sum(item["startingBid"] for item in (compareStack)):
        rl.append(prices[l].pop(0))
        for i in compareStack:
            tier = i["attributes"][attribute]
            prices[tier].append(i)
            prices[tier] = sorted(prices[tier], key=lambda x: x["startingBid"])
        return rl
    else:
        return compareStack

print(cost(starting_armour["attr1"][2], attribute1_prices, starting_armour["attr1"][0]))
print(cost(starting_armour["attr2"][2], attribute2_prices, starting_armour["attr2"][0]))
