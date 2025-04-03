var startLevel = 1
var endLevel = 1
var attribute = undefined
var running = false
var prices = [[]]
let piece = "helmet"
let types = ["aurora", "crimson", "fervor", "hollow", "terror"]
let useArmour = false
let result

const sleep = ms => new Promise(r => setTimeout(r, ms));

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
    for (var i = 0; i < endLevel; i++) {
        prices.push([])
    }
    let url = `https://auction-api-production-4ce9.up.railway.app/?attribute=["${attribute}",1,${endLevel}]&piece=${piece.toUpperCase()}`
    if (!useArmour) url = `https://auction-api-production-4ce9.up.railway.app/?attribute=["${attribute}",1,${endLevel}]`
    let data = await (await fetch(url)).json();
    data["auctions"].forEach((auction) => {
        let level = auction["attributes"][attribute]
        prices[level].push(auction)
    })

    prices[startLevel].push({
        "attributes": { [attribute]: startLevel },
        "startingBid": 0, 
        "uuid": "starting",
        "type": "starting_piece"
    });
    prices[startLevel].sort((a, b) => a.startingBid - b.startingBid);
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

function copyAuctionId(string) {
    navigator.clipboard.writeText(string);
}

function renderResults(result, attribute) {
    let sum = result.reduce((acc, item) => acc + item.startingBid, 0)
    let total = sum;
    let sumElement = document.createElement("h2")
    sumElement.textContent = "Total Cost: "+formatNumber(sum)
    sumElement.classList.add("costSum")
    document.querySelector("#resultsContainer").appendChild(sumElement)
    result.forEach((book) => {
        let bookElement = document.createElement("p")
        let tier = book["attributes"][attribute]
        bookElement.setAttribute("copyString", "/viewauction "+book.uuid)
        if (book.startingBid == 0) return;
        if (attribute == "mending") {
            bookElement.innerHTML = book["type"]+" /W VITALITY "+tier+" @"+(formatNumber(book.startingBid))+": "+"<br><span> /viewauction "+book.uuid+"</span>"
        }else {
            bookElement.innerHTML = book["type"]+" /W "+attribute.toUpperCase()+" "+tier+" @"+(formatNumber(book.startingBid))+": "+"<br><span>/viewauction "+book.uuid+"</span>"
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

        let crossOutCheckbox = document.createElement("input")
        crossOutCheckbox.type = "checkbox"
        crossOutCheckbox.classList.add("resultTextCheckbox")
        bookElement.appendChild(crossOutCheckbox)
        bookElement.setAttribute('price', book.startingBid)

        crossOutCheckbox.onclick = (event) => {
            let span = event.target.parentElement.querySelector("span")
            let price = parseInt(span.parentElement.getAttribute('price'))
            console.log(sum, price)
            if (event.target.checked) {
                sum = sum - price
                document.querySelector("h2").textContent = "Total Cost: "+formatNumber(total)+" ("+formatNumber(sum)+" left)"
                span.style.textDecoration = "line-through";
                span.parentElement.style.color = "#FF6F61";
            } else {
                sum = sum + price
                document.querySelector("h2").textContent = "Total Cost: "+formatNumber(total)
                if (sum != total) {
                    document.querySelector("h2").textContent += " ("+formatNumber(sum)+" left)"
                }
                span.style.textDecoration = "none";
                span.parentElement.style.color = "white";
            }
        }

        document.querySelector("#resultsContainer").appendChild(bookElement)
        document.querySelector("#resultsContainer").appendChild(document.createElement("br"))
    })
}

document.querySelector("#attributeSelector").addEventListener("sl-select", (event) => {
    attribute = event.detail.item.value
    document.querySelector("#dropdownOption").textContent = event.detail.item.textContent
})

document.querySelector("#armourType").addEventListener("sl-select", (event) => {
    piece = event.detail.item.value
    document.querySelector("#armourTypeDropdownOption").textContent = event.detail.item.textContent
})

document.querySelector("#useArmour").addEventListener("change", (input) => {
    useArmour = input.target.checked
    console.log(useArmour)
    if (useArmour) {
        document.querySelector("#armourType").style.visibility = "visible";
    } else {
        document.querySelector("#armourType").style.visibility = "hidden";
    }
})

document.querySelector("#startingLevel").addEventListener("input", (input) => {
    startLevel = parseInt(input.target.value)
    input.target.label = "Starting Level: "+startLevel
})

document.querySelector("#endingLevel").addEventListener("input", (input) => {
    endLevel = parseInt(input.target.value)
    input.target.label = "Ending Level: "+endLevel
})

document.querySelector("#calculateButton").onclick = async () => {
    if (endLevel <= startLevel || attribute == undefined) {alert("Invalid attribute or ending level!"); return false;}
    if (running == true) return false;
    running = true
    prices=  [[]];
    document.querySelector("#resultsContainer").innerHTML = ""
    await calculatePrices();
    result = await cost(endLevel, prices, attribute);
    let item = "attribute_shard"
    if (useArmour) {
        item = piece
    }
    result.sort((a, b) => a.startingBid - b.startingBid);
    document.querySelector("#resultsContainer").innerHTML = ""
    if (result.length == 0) {
        document.querySelector("#resultsContainer").innerHTML = "Could not find a way to reach desired level!"
    } else {
        renderResults(result, attribute)
    }
    running = false
}