import requests

startLevel = 3
endLevel = 5
attribute = "dominance"

prices = [[]]

for i in range(10):
    url = f"https://sky.coflnet.com/api/auctions/tag/ATTRIBUTE_SHARD/active/bin?{attribute}={str(i+1)}"
    response = requests.request("GET", url)
    prices.append(response.json())

prices[startLevel].append({
    "startingBid": 0, 
    "uuid": "starting",
    "nbtData" : {
        "data": {
            "attributes": {
                attribute: startLevel
            }
        }
    }
})

print(prices)

prices[startLevel] = sorted(prices[startLevel], key=lambda x: x["startingBid"])

def cost(l, stack=[]):
    global prices
    rl = stack.copy()
    if l == 1:
        if prices[1] == []:
            return []
        shard = prices[1].pop(0)
        rl.append(shard)
        return rl
    
    t1 = cost(l-1, rl)
    t2 = cost(l-1, rl)
    compareStack = t1+t2
    ranOut = t1 == [] or t2 == []
    noCurrent = prices[l] == []
    if ranOut and not noCurrent:
        rl.append(prices[l].pop(0))
        for i in compareStack:
            tier = i["nbtData"]["data"]["attributes"][attribute]
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
            tier = i["nbtData"]["data"]["attributes"][attribute]
            prices[tier].append(i)
            prices[tier] = sorted(prices[tier], key=lambda x: x["startingBid"])
        return rl
    else:
        return compareStack

def filterOutBaseAttr(x):
    return x["uuid"] != "starting"

result = cost(endLevel)
result = list(filter(filterOutBaseAttr, result))
finalCost = sum(item["startingBid"] for item in (result))
for auction in result:
    tier = auction["nbtData"]["data"]["attributes"][attribute]
    price = auction["startingBid"]
    print(f"{attribute.upper()} {str(tier)} {str(price/1000000)}M: /viewauction {auction['uuid']}")
print(f"TOTAL COST: {str(finalCost/1000000)}M")