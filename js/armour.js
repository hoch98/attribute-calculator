let armourType = undefined
let armourPiece = undefined
let attribute1 = {
    "name": undefined,
    "targetLevel": 1
}
let attribute2 = {
    "name": undefined,
    "targetLevel": 1
}

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

function copyAuctionId(string) {
    navigator.clipboard.writeText(string);
}

function renderResults(result, attribute) {
    let sum = result.reduce((acc, item) => acc + item.startingBid, 0)
    let sumElement = document.createElement("h2")
    sumElement.textContent = `${attribute.toUpperCase()}: `+formatNumber(sum)
    sumElement.classList.add("costSum")
    document.querySelector("#resultsContainer").appendChild(sumElement)
    result.forEach((book) => {
        let bookElement = document.createElement("p")
        let tier = book["attributes"][attribute]
        bookElement.setAttribute("copyString", "/viewauction "+book.uuid)
        if (book.startingBid == 0) return;
        if (attribute == "mending") {
            bookElement.innerHTML = book["type"]+" W/ VITALITY "+tier+" @"+(formatNumber(book.startingBid))+": "+"<br><span> /viewauction "+book.uuid+"</span>"
        }else {
            bookElement.innerHTML = book["type"]+" W/ "+attribute.toUpperCase()+" "+tier+" @"+(formatNumber(book.startingBid))+": "+"<br><span>/viewauction "+book.uuid+"</span>"
        }
        let copybutton = document.createElement("button");
        let copyicon = document.createElement('sl-icon');

        copyicon.setAttribute("name", "copy")

        copybutton.addEventListener('click', (input) => {
            let node = input.target.parentElement
            if (node.tagName != "P") node = node.parentElement;
            copyAuctionId(node.getAttribute("copyString"))
        })
        copybutton.appendChild(copyicon)
        bookElement.appendChild(copybutton)

        document.querySelector("#resultsContainer").appendChild(bookElement)
        document.querySelector("#resultsContainer").appendChild(document.createElement("br"))
    })
}

async function getPrices(attribute, endLevel, piece) {
    let prices = [[]]
    for (var i = 0; i < endLevel; i++) {
        prices.push([])
    }
    let url = `https://auction-api-production-4ce9.up.railway.app/?attribute=["${attribute}",1,${endLevel}]&piece=${piece.toUpperCase()}`
    let data = await (await fetch(url)).json();
    data["auctions"].forEach((auction) => {
        let level = auction["attributes"][attribute]
        prices[level].push(auction)
    })
    return prices
}

function cost(l, prices, attribute,  stack=[]) {
    let rl = stack.slice()
    let shard;
    if (l == 1) {
        if (prices[1].length == 0) return []
        shard = prices[1].shift()
        rl.push(shard)
        return rl
    }
    let t1 = cost(l-1, prices, attribute, rl)
    let t2 = cost(l-1, prices, attribute, rl)
    let compareStack = t1.concat(t2);
    let ranOut = t1.length == 0 || t2.length == 0
    let noCurrent = prices[l].length == 0

    let sum = compareStack.reduce((acc, item) => acc + item.startingBid, 0)

    if (ranOut && !noCurrent) { 
        rl.push(prices[l].shift())
        compareStack.forEach((i) => {
            let tier = i["attributes"][attribute]
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
            let tier = i["attributes"][attribute]
            prices[tier].push(i)
            prices[tier].sort((a, b) => a.startingBid - b.startingBid);
        })
        return rl
    }
    return compareStack
}

document.querySelector("#armourType1").addEventListener("sl-select", (event) => {
    armourType = event.detail.item.value
    document.querySelector("#armourTypeDropdownOption1").textContent = event.detail.item.textContent
})

document.querySelector("#armourType").addEventListener("sl-select", (event) => {
    armourPiece = event.detail.item.value
    document.querySelector("#armourTypeDropdownOption").textContent = event.detail.item.textContent
})

document.querySelector("#attributeSelector").addEventListener("sl-select", (event) => {
    attribute1.name = event.detail.item.value
    document.querySelector("#dropdownOption").textContent = event.detail.item.textContent
})

document.querySelector("#attributeSelector2").addEventListener("sl-select", (event) => {
    attribute2.name = event.detail.item.value
    document.querySelector("#dropdownOption2").textContent = event.detail.item.textContent
})

document.querySelector("#targetLevel").addEventListener("input", (input) => {
    attribute1.targetLevel = parseInt(input.target.value)
    input.target.label = "Target Level: "+attribute1.targetLevel
})

document.querySelector("#targetLevel2").addEventListener("input", (input) => {
    attribute2.targetLevel = parseInt(input.target.value)
    input.target.label = "Target Level: "+attribute2.targetLevel
})

document.querySelector("#calculateButton").onclick = async () => {
    if (attribute1.name == attribute2.name || armourType == undefined ||armourPiece == undefined || attribute1.name == undefined || attribute2.name == undefined) {alert("Invalid attributes or armour piece!"); return false;}
    let armourTag = armourType+"_"+armourPiece

    let cheapest = {
        "starting_armour": {},
        "attr1_upgrades": [],
        "attr2_upgrades": [],
        'total': 0
    }

    let attr1_prices = await getPrices(attribute1.name, attribute1.targetLevel, armourPiece)
    let attr2_prices = await getPrices(attribute2.name, attribute2.targetLevel, armourPiece)

    let url = `https://auction-api-production-4ce9.up.railway.app/?attribute=["${attribute1.name}",1,${attribute1.targetLevel}]&attribute2=["${attribute2.name}",1,${attribute2.targetLevel}]&piece=${armourTag.toUpperCase()}&onlyArmour=TRUE`
    let data = await (await fetch(url)).json();

    if (data["auctions"].length == 0) {
        document.querySelector("#resultsContainer").innerHTML = "Couldn't not find a starting armour :/"
        return false;
    }

    (async () => {
        for (var i = 0; i < data["auctions"].length; i++) {
            let auction = data["auctions"][i];
            let attr1_copy = [...attr1_prices]
            let attr2_copy = [...attr2_prices]
    
            attr1_copy[auction["attributes"][attribute1.name]].push({
                "attributes": auction["attributes"],
                "startingBid": auction["startingBid"], 
                "uuid": "starting",
                "type": "starting_piece"
            });
    
            attr2_copy[auction["attributes"][attribute2.name]].push({
                "attributes": auction["attributes"],
                "startingBid": auction["startingBid"], 
                "uuid": "starting",
                "type": "starting_piece"
            });
    
            attr1_copy[auction["attributes"][attribute1.name]].sort((a, b) => a.startingBid - b.startingBid);
            attr2_copy[auction["attributes"][attribute2.name]].sort((a, b) => a.startingBid - b.startingBid);
    
            let result1 = await cost(attribute1.targetLevel, attr1_copy, attribute1.name);
            let result2 = await cost(attribute2.targetLevel, attr2_copy, attribute2.name);
            if (result1.length == 0 || result2.length == 0) {console.log("no"); return false};
            let sum1 = result1.reduce((acc, item) => acc + item.startingBid, 0)
            let sum2 = result2.reduce((acc, item) => acc + item.startingBid, 0)
            let total = sum1+sum2+auction["startingBid"]
            if (total < cheapest.total || cheapest.total === 0) {
                cheapest.total = total
                cheapest.attr1_upgrades = result1
                cheapest.attr2_upgrades = result2
                cheapest.starting_armour = auction
            }
        }
    })().then((out) => {
        if (cheapest.attr1_upgrades.length != 0) {
            let starting_armour = cheapest.starting_armour
            document.querySelector("#resultsContainer").innerHTML = `<h1>Total Cost: ${formatNumber(cheapest.total)}</h1><h2>Starting Armour: </h2>`
            let bookElement = document.createElement("p")
            bookElement.setAttribute("copyString", "/viewauction "+starting_armour.uuid)
            if (starting_armour.startingBid == 0) return;
            bookElement.innerHTML = `${starting_armour["type"]} w/ ${attribute1.name.toUpperCase()} ${starting_armour["attributes"][attribute1.name]} & ${attribute2.name.toUpperCase()} ${starting_armour["attributes"][attribute2.name]} @ ${formatNumber(starting_armour["startingBid"])}:`+"<br><span> /viewauction "+starting_armour.uuid+"</span>"

            let copybutton = document.createElement("button");
            let copyicon = document.createElement('sl-icon');

            copyicon.setAttribute("name", "copy")

            copybutton.addEventListener('click', (input) => {
                let node = input.target.parentElement
                if (node.tagName != "P") node = node.parentElement;
                copyAuctionId(node.getAttribute("copyString"))
            })
            copybutton.appendChild(copyicon)
            bookElement.appendChild(copybutton)

            document.querySelector("#resultsContainer").appendChild(bookElement)
            document.querySelector("#resultsContainer").appendChild(document.createElement("br"))
            renderResults(cheapest.attr1_upgrades, attribute1.name)
            renderResults(cheapest.attr2_upgrades, attribute2.name)
        } else {

            document.querySelector("#resultsContainer").innerHTML = "Couldn't find a way to reach desired level :/"
        }
    })

}