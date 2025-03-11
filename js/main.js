var startLevel = parseInt(document.querySelector("#startingLevel").value)
var endLevel = parseInt(document.querySelector("#endingLevel").value)
var attribute = document.querySelector("#attributeSelector").value
var running = false
var prices = [[]]

function formatNumber(num) {
    if (num >= 1_000_000_000) {
        return `${(num / 1_000_000_000).toFixed(2)}b`;
    } else if (num >= 1_000_000) {
        return `${(num / 1_000_000).toFixed(2)}m`;
    } else if (num >= 1_000) {
        return `${(num / 1_000).toFixed(2)}k`;
    } else {
        return num.toString();
    }
}

async function calculatePrices() {
    prices = [[]]
    for (var i = 0; i < 10; i++) {
        let result = await (await fetch("https://sky.coflnet.com/api/auctions/tag/ATTRIBUTE_SHARD/active/bin?"+attribute+"="+(i+1))).text();
        prices.push(JSON.parse(result))
    }
    prices[startLevel].push({
        "startingBid": 0, 
        "uuid": "starting",
        "nbtData" : {
            "data": {
                "attributes": {
                    [attribute]: startLevel
                }
            }
        }
    })
    prices[startLevel].sort((a, b) => a.startingBid - b.startingBid);
    console.log(prices[startLevel])
}

function cost(l, stack=[]) {
    let rl = stack.slice()
    let shard;
    if (l == 1) {
        if (prices[1].length == 0) return []
        shard = prices[1].shift()
        rl.push(shard)
        return rl
    }
    let t1 = cost(l-1, rl)
    let t2 = cost(l-1, rl)
    let compareStack = t1.concat(t2);
    let ranOut = t1.length == 0 || t2.length == 0
    let noCurrent = prices[l].length == 0

    let sum = compareStack.reduce((acc, item) => acc + item.startingBid, 0)

    if (ranOut && !noCurrent) { 
        rl.push(prices[l].shift())
        compareStack.forEach((i) => {
            let tier = i["nbtData"]["data"]["attributes"][attribute]
            prices[tier].push(i)
            prices[tier].sort((a, b) => a.startingBid - b.startingBid);
        })
        return rl
    } if (noCurrent && !ranOut) {
        return compareStack
    } if (noCurrent && ranOut) {
        return []
    } if (prices[l][0]["startingBid"] <= sum) {
        rl.push(prices[l].shift())
        compareStack.forEach((i) => {
            let tier = i["nbtData"]["data"]["attributes"][attribute]
            prices[tier].push(i)
            prices[tier].sort((a, b) => a.startingBid - b.startingBid);
        })
        return rl
    }
    return compareStack
}

function copyAuctionId(string) {
    console.log(string)
    navigator.clipboard.writeText(string);
  } 

document.querySelector("#attributeSelector").addEventListener("change", (input) => {
    attribute = input.target.value
})

document.querySelector("#startingLevel").addEventListener("input", (input) => {
    startLevel = parseInt(input.target.value)
    document.querySelector('#startingLevelDisplay').textContent =  'Starting Level: '+input.target.value
})

document.querySelector("#endingLevel").addEventListener("input", (input) => {
    endLevel = parseInt(input.target.value)
    document.querySelector('#endingLevelDisplay').textContent =  'Ending Level: '+input.target.value
})

document.querySelector("#calculateButton").onclick = async () => {
    if (endLevel <= startLevel) {alert("Invalid ending level!"); return false;}
    if (running == true) return false;
    document.querySelector("#resultsContainer").innerHTML = ""
    running = true
    prices=  [[]];
    await calculatePrices();
    let result = await cost(endLevel);
    result.sort((a, b) => a.startingBid - b.startingBid);
    if (result.length == 0) {
        document.querySelector("#resultsContainer").innerHTML = "Could not find a way to reach desired level!"
    } else {
        let sum = result.reduce((acc, item) => acc + item.startingBid, 0)
        let sumElement = document.createElement("h2")
        sumElement.textContent = "Total Cost: "+formatNumber(sum)
        sumElement.classList.add("costSum")
        document.querySelector("#resultsContainer").appendChild(sumElement)
        result.forEach((book) => {
            let bookElement = document.createElement("h3")
            let tier = book["nbtData"]["data"]["attributes"][attribute]
            bookElement.setAttribute("copyString", "/viewauction "+book.uuid)
            if (book.startingBid == 0) return;
            if (attribute == "mending") {
                bookElement.textContent = "VITALITY "+tier+" @"+(formatNumber(book.startingBid))+": "+"/viewauction "+book.uuid
            }else {
                bookElement.textContent = attribute.toUpperCase()+" "+tier+" @"+(formatNumber(book.startingBid))+": "+"/viewauction "+book.uuid
            }
            let copybutton = document.createElement("button");
            let copyicon = document.createElement('i');
            copyicon.classList.add("ti")
            copyicon.classList.add("ti-copy")

            copybutton.addEventListener('click', (input) => {
                let node = input.target.parentElement
                if (node.tagName != "H3") node = node.parentElement;
                copyAuctionId(node.getAttribute("copyString"))
            })
            copybutton.appendChild(copyicon)
            bookElement.appendChild(copybutton)
            document.querySelector("#resultsContainer").appendChild(bookElement)
            document.querySelector("#resultsContainer").appendChild(document.createElement("br"))
        })
    }
    running = false
}