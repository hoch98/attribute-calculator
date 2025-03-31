from includeArmour import getPrices, cost, format_number, filterOutBaseAttr

starting_armour = {
  "tier": "burning",
  "type": "aurora",
  "piece": "chestplate",
  "attr1": ["mana_pool", 6, 8],
  "attr2": ["mending", 6, 6],
}

attribute1_prices = getPrices(starting_armour, starting_armour["attr1"])
attribute2_prices = getPrices(starting_armour, starting_armour["attr2"])

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

attribute2_prices[starting_armour["attr2"][1]].append(
  {
    "attributes": {
      starting_armour["attr2"][0]: starting_armour["attr2"][1]
    },
    "startingBid": 0,
    "uuid": "starting",
    "type": (starting_armour["type"]+"_"+starting_armour["piece"]).upper()
  }
)

attribute1_prices[starting_armour["attr1"][1]] = sorted(attribute1_prices[starting_armour["attr1"][1]], key=lambda x: x["startingBid"])
attribute2_prices[starting_armour["attr2"][1]] = sorted(attribute2_prices[starting_armour["attr2"][1]], key=lambda x: x["startingBid"])

total = 0

results = cost(starting_armour["attr1"][2], attribute1_prices, starting_armour["attr1"][0])
results = list(filter(filterOutBaseAttr, results))

print(f"{starting_armour['attr1'][0]} {starting_armour['attr1'][1]} > {starting_armour['attr1'][2]}")
for i, result in enumerate(results):
  total += int(result['startingBid'])
  print(f"{i+1}. {result['type']} with {starting_armour['attr1'][0]} {result['attributes'][starting_armour['attr1'][0]]}@{format_number(result['startingBid'])}: /viewauction {result['uuid']}")
print()

results = cost(starting_armour["attr2"][2], attribute2_prices, starting_armour["attr2"][0])
results = list(filter(filterOutBaseAttr, results))

print(f"{starting_armour['attr2'][0]} {starting_armour['attr2'][1]} > {starting_armour['attr2'][2]}")
for i, result in enumerate(results):
  total += int(result['startingBid'])
  print(f"{i+1}. {result['type']} with {starting_armour['attr2'][0]} {result['attributes'][starting_armour['attr2'][0]]}@{format_number(result['startingBid'])}: /viewauction {result['uuid']}")
print()
print("Total: "+format_number(total))