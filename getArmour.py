from includeArmour import getPrices, cost, format_number, filterOutBaseAttr
import requests

starting_armour = {
  "type": "crimson",
  "piece": "boots",
  "attr1": ["dominance", 0, 5],
  "attr2": ["veteran", 0, 5],
}

cheapest = {
  "starting_armour": {},
  "attr1_upgrades": [],
  "attr2_upgrades": [],
  'total': 0
}

attribute1_prices = getPrices(starting_armour, starting_armour["attr1"])
attribute2_prices = getPrices(starting_armour, starting_armour["attr2"])

url = f"https://sky.coflnet.com/api/auctions/tag/{(starting_armour['type']+'_'+starting_armour['piece']).upper()}/active/bin?{starting_armour['attr1'][0]}=1-{starting_armour['attr1'][2]}&{starting_armour['attr2'][0]}=1-{starting_armour['attr2'][2]}"
response = requests.request("GET", url).json()

for armour in response:
  starting_armour["attr1"] = [starting_armour["attr1"][0], int(armour["flatNbt"][starting_armour["attr1"][0]]), starting_armour["attr1"][2]]
  starting_armour["attr2"] = [starting_armour["attr2"][0], int(armour["flatNbt"][starting_armour["attr2"][0]]), starting_armour["attr2"][2]]
  total = armour["startingBid"]

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

  results1 = cost(starting_armour["attr1"][2], attribute1_prices, starting_armour["attr1"][0])
  results1 = list(filter(filterOutBaseAttr, results1))

  for i in results1:
    total += int(i['startingBid'])

  results2 = cost(starting_armour["attr2"][2], attribute2_prices, starting_armour["attr2"][0])
  results2 = list(filter(filterOutBaseAttr, results2))
  for i in results2:
    total += int(i['startingBid'])

  if total < cheapest['total'] or cheapest['total'] == 0:
    cheapest["starting_armour"] = armour
    cheapest["attr1_upgrades"] = results1
    cheapest["attr2_upgrades"] = results2
    cheapest['total'] = total

starting = cheapest["starting_armour"]
total = starting["startingBid"]
print(f"Starting Armour: {starting['tag']} w/ {starting_armour['attr1'][0]} {starting['flatNbt'][starting_armour['attr1'][0]]} & {starting_armour['attr2'][0]} {starting['flatNbt'][starting_armour['attr2'][0]]}")
print("Price: "+format_number(total))

print(f"{starting_armour['attr1'][0]} {starting_armour['attr1'][1]} > {starting_armour['attr1'][2]}")
for i, result in enumerate(cheapest["attr1_upgrades"]):
  total += int(result['startingBid'])
  print(f"{i+1}. {result['type']} with {starting_armour['attr1'][0]} {result['attributes'][starting_armour['attr1'][0]]}@{format_number(result['startingBid'])}: /viewauction {result['uuid']}")
print()

print(f"{starting_armour['attr2'][0]} {starting_armour['attr2'][1]} > {starting_armour['attr2'][2]}")
for i, result in enumerate(cheapest["attr2_upgrades"]):
  total += int(result['startingBid'])
  print(f"{i+1}. {result['type']} with {starting_armour['attr2'][0]} {result['attributes'][starting_armour['attr2'][0]]}@{format_number(result['startingBid'])}: /viewauction {result['uuid']}")
print("Total: "+format_number(total))