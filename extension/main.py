import requests, json

starting_armour = {
  "tier": "burning",
  "type": "aurora",
  "piece": "boots",
  "attr1": ["mana_regeneration", 2, 5],
  "attr2": ["mana_pool", 2, 5]
}

types = ["aurora", "crimson", "fervor", "hollow", "terror"]

attribute1_prices = [[]]
attribute2_prices = [[]]

for i in range(starting_armour["attr1"][2]):
    
  level_prices = []

  for type in types:
    armour_tag = (type+"_"+starting_armour["piece"]).upper()
    print(armour_tag, starting_armour['attr1'][0], i+1)

    url = f"https://sky.coflnet.com/api/auctions/tag/{armour_tag}/active/bin?{starting_armour['attr1'][0]}={str(i+1)}"
    response = requests.request("GET", url)

    response = [{
      "attributes" : product["nbtData"]["data"]["attributes"]
    }]

    level_prices += response.json()

  attribute1_prices.append(level_prices)

with open("data.json", "w") as file:
  json.dump(attribute1_prices, file, indent=4)
