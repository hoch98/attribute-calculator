import requests, json, time

starting_armour = {
  "tier": "burning",
  "type": "crimson",
  "piece": "chestplate",
  "attr1": ["dominance", 2, 3],
}

def filterOutBaseAttr(x):
    return x["uuid"] != "starting"

def format_number(num):
  if num >= 1_000_000_000:
    return f"{num / 1_000_000_000:.2f}b"
  elif num >= 1_000_000:
    return f"{num / 1_000_000:.2f}m"
  elif num >= 1_000:
    return f"{num / 1_000:.2f}k"
  else:
    return str(num)

def getPrices(starting_armour, attributeData):

  attribute1_prices = [[]]
  types = ["aurora", "crimson", "fervor", "hollow", "terror"]

  for i in range(attributeData[2]):
      
    level_prices1 = []

    for armourType in types:
      armour_tag = (armourType+"_"+starting_armour["piece"]).upper()

      url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{attributeData[0]}={str(i+1)}"
      response = requests.request("GET", url)
      try:
        response.json()
      except:
        print("ran out of requests, continuing after 30 seconds")
        time.sleep(30)
        url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{attributeData[0]}={str(i+1)}"
        response = requests.request("GET", url)

      response = [{
        "attributes" : product["nbtData"]["data"]["attributes"],
        "startingBid": product["startingBid"],
        "uuid": product["uuid"],
        "type": armour_tag
      } for product in response.json()]

      level_prices1 += response

    #attribute shards

    url = f"https://sky.coflnet.com/api/auctions/tag/ATTRIBUTE_SHARD/active/bin?{attributeData[0]}={str(i+1)}"
    response = requests.request("GET", url)
    level_prices1 += [
      {
        "attributes": {
          attributeData[0]: i+1
        },
        "startingBid": product["startingBid"],
        "uuid": product["uuid"],
        "type": "ATTRIBUTE_SHARD"
      } for product in response.json()
    ]

    attribute1_prices.append(level_prices1)

  return attribute1_prices

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

def run():

  attribute1_prices = getPrices(starting_armour, starting_armour["attr1"])

  attribute1_prices[starting_armour["attr1"][1]].append(
    {
      "attributes": {
        starting_armour["attr1"][0]: starting_armour["attr1"][1]
      },
      "startingBid": 0,
      "uuid": "starting",
      "type": (starting_armour["type"]+"_"+starting_armour["piece"]).upper()
    }
  )

  attribute1_prices[starting_armour["attr1"][1]] = sorted(attribute1_prices[starting_armour["attr1"][1]], key=lambda x: x["startingBid"])

  results = cost(starting_armour["attr1"][2], attribute1_prices, starting_armour["attr1"][0])
  results = list(filter(filterOutBaseAttr, results))

  total = 0
  for i, result in enumerate(results):
    total += int(result['startingBid'])
    print(f"{i+1}. {result['type']} with {starting_armour['attr1'][0]} {result['attributes'][starting_armour['attr1'][0]]}@{format_number(result['startingBid'])}: /viewauction {result['uuid']}")

  print(format_number(total))