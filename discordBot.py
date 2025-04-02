import interactions
from interactions import Embed
import requests, json

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

  attribute1_prices = []
  for i in range(attributeData[2]+1):
     attribute1_prices.append([])

  attributeName = attributeData[0]
  url = f'https://auction-api-production-4ce9.up.railway.app/?attribute=["{attributeName}",{attributeData[1]},{attributeData[2]}]&piece={starting_armour["piece"].upper()}'
  
  if not starting_armour["use_armour"]: url = f'https://auction-api-production-4ce9.up.railway.app/?attribute=["{attributeName}",{attributeData[1]},{attributeData[2]}]'
  response = requests.request("GET", url).json()

  for auction in response["auctions"]:
    level = auction["attributes"][attributeName]
    attribute1_prices[level].append(auction)

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


bot = interactions.Client(token="<token>")
attribute_types = ["arachno", "arachno_resistance", "attack_speed", "blazing", "blazing_fortune", "blazing_resistance", "breeze", "combo", "deadeye", "dominance", "double_hook", "elite", "ender", "ender_resistance", "experience", "fisherman", "fishing_experience", "fishing_speed", "fortitude", "hunter", "ignition", "infection", "life_recovery", "life_regeneration", "lifeline", "magic_find", "mana_pool", "mana_regeneration", "mana_steal", "midas_touch", "speed", "trophy_hunter", "undead", "undead_resistance", "veteran", "mending", "warrior"]
pieces = ["helmet", "chestplate", "leggings", "boots"]

@bot.command(
    name="attributeupgrade",
    description="Upgrading attributes",
    scope=1234101581000212480,
    options = [
        interactions.Option(
            name="attribute",
            description="What attribute to upgrade",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="starting_level",
            description="Upgrade starting level",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="ending_level",
            description="Upgrade ending level",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="armour",
            description="Armour piece to upgrade",
            type=interactions.OptionType.STRING,
            required=False,
            choices = [
                interactions.Choice(name=attr, value=attr) for attr in pieces
            ]
        )
    ]
)

async def upgrades(ctx: interactions.CommandContext, attribute:str, starting_level:int, ending_level: int, **kwargs):
    if attribute.lower() == "vitality" or attribute.lower() == "vit": attribute = "mending"
    if attribute.lower() not in attribute_types:
        embed = Embed(title="Could not find attribute `"+attribute+"`, please try again.")

        await ctx.send(embeds=embed)
        return
    
    description = ""
    use_armour = "armour" in kwargs.keys()
    if attribute.lower() == "vitality": attribute = "mending"

    starting_armour = {
        "use_armour": use_armour,
        "type": "donmata",
        "piece": kwargs["armour"] if use_armour else "no",
        "attr1": [attribute.lower(), starting_level, ending_level],
    }
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
    results = sorted(results, key=lambda x: x["startingBid"])

    total = 0
    for i, result in enumerate(results):
        total += int(result['startingBid'])
        description += f"{i+1}. {result['type']} with {starting_armour['attr1'][0]} {result['attributes'][starting_armour['attr1'][0]]}@{format_number(result['startingBid'])}\n > /viewauction {result['uuid']} \n"
    description += "\n"+f"**Total: {format_number(total)} (not including fusion cost)**"
    if len(results) == 0:
       description = "Couldn't find a way to reach that level :/"

    title = f"Upgrade `{attribute.upper()} {starting_level} > {ending_level}`"
    if use_armour:
        title = f"Upgrade `{attribute.upper()} {starting_level} > {ending_level}` for {kwargs['armour']}"

    embed = Embed(title=title,
                      description=description, colour=0x00b0f4)

    await ctx.send(embeds=embed)

bot.start()