console.log('check js form')


function sumColumn(elementList, inputType) {
    let sum = 0;
    for (i=0; i < elementList.length; i++) {
        if (inputType === 'textContent' && elementList[i].value !== '') {
            sum = parseFloat(sum) + parseFloat(elementList[i].textContent);
        } else if (inputType === 'value'  && elementList[i].value !== '') {
            sum = parseFloat(sum) + parseFloat(elementList[i].value);
        };
        sum = sum.toFixed(2)
    };
    return sum;
}

function previousAmount() {
    let elementList = document.querySelectorAll("td[name=lastAmount]");
    document.querySelector("td[name=previousSum]").textContent = sumColumn(elementList,'textContent');
}

function addOrRemove() {
    let elementList = document.querySelectorAll("input[name=addOrRemove]");
    document.querySelector("td[name=addOrRemoveSum]").textContent = sumColumn(elementList,'value');
};

function newAmount() {
    let elementList = document.querySelectorAll("tbody");
    for (let row of elementList) {
        let lastAmount = row.querySelector("td[name=lastAmount]").textContent;
        let addOrRemoveSum = row.querySelector("input[name=addOrRemove]").value;
        sum = parseFloat(lastAmount) + parseFloat(addOrRemoveSum);
        row.querySelector("td[name=newAmount]").textContent = sum;
    }
    
    let resultRow = document.querySelector("tfoot > tr");
    console.log(resultRow);
    let lastAmountFooter = resultRow.querySelector("td[name=previousSum]").textContent;
    let addOrRemoveSumFooter = resultRow.querySelector("td[name=addOrRemoveSum]").textContent;
    let sumFooter = parseFloat(lastAmountFooter) + parseFloat(addOrRemoveSumFooter);
    console.log('let\'s try this', lastAmountFooter, addOrRemoveSumFooter, sumFooter)
    resultRow.querySelector("td[name=newAmountSum]").textContent = sumFooter;
};


function render() {
    previousAmount();
    addOrRemove();
    newAmount();
}

render();