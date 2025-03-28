import requests, json, time

starting_armour = {
  "tier": "burning",
  "type": "crimson",
  "piece": "chestplate",
  "attr1": ["dominance", 2, 5],
  "attr2": ["mending", 2, 5]
}

def format_number(num):
  if num >= 1_000_000_000:
    return f"{num / 1_000_000_000:.2f}b"
  elif num >= 1_000_000:
    return f"{num / 1_000_000:.2f}m"
  elif num >= 1_000:
    return f"{num / 1_000:.2f}k"
  else:
    return str(num)

types = ["aurora", "crimson", "fervor", "hollow", "terror"]

attribute1_prices = [[]]

for i in range(starting_armour["attr1"][2]):
    
  level_prices1 = []

  for type in types:
    armour_tag = (type+"_"+starting_armour["piece"]).upper()
    print(armour_tag, starting_armour['attr1'][0], i+1)

    url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{starting_armour['attr1'][0]}={str(i+1)}"
    response = requests.request("GET", url)
    try:
      response.json()
    except:
      print("ran out of requests, continuing after a minute")
      time.sleep(60)
      url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{starting_armour['attr1'][0]}={str(i+1)}"
      response = requests.request("GET", url)

    response = [{
      "attributes" : product["nbtData"]["data"]["attributes"],
      "startingBid": product["startingBid"],
      "uuid": product["uuid"],
      "type": armour_tag
    } for product in response.json()]

    level_prices1 += response

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

  attribute1_prices.append(level_prices1)

attribute1_prices[starting_armour["attr1"][1]].append(
  {
    "attributes": {
      starting_armour["attr1"][0]: starting_armour["attr1"][1]
    },
    "startingBid": 0,
    "uuid": "starting armour",
    "type": (type+"_"+starting_armour["piece"]).upper()
  }
)

attribute1_prices[starting_armour["attr1"][1]] = sorted(attribute1_prices[starting_armour["attr1"][1]], key=lambda x: x["startingBid"])

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

results =  cost(starting_armour["attr1"][2], attribute1_prices, starting_armour["attr1"][0])

total = 0
for result in results:
  total += int(result['startingBid'])
  print(f"{result['type']} with {starting_armour['attr1'][0]} {result['attributes'][starting_armour['attr1'][0]]}@{result['startingBid']}: {result['uuid']}")

print(format_number(total))

with open("data.json", "w") as file:
   json.dump(attribute1_prices, file, indent=2)