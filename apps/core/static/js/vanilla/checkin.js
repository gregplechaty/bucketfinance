console.log('check js form')


function sumColumn(elementList, inputType) {
    let sum = 0;
    for (i=0; i < elementList.length; i++) {
        if (inputType === 'textContent' && elementList[i].textContent !== '') {
            sum = parseFloat(sum) + parseFloat(elementList[i].textContent);
        } else if (inputType === 'value'  && elementList[i].value !== '') {
            console.log('value value...', elementList[i].value)
            sum = parseFloat(sum) + parseFloat(elementList[i].value);
        };
         if (typeof sum === "number") {
            sum = sum.toFixed(2);
        }
    };
    return sum;
}

function previousAmount() {
    let elementList = document.querySelectorAll("td[name=lastAmount]");
    document.querySelector("td[name=previousSum]").textContent = sumColumn(elementList,'textContent');
}

function addOrRemove() {
    let elementList = document.querySelectorAll("input[sumCalc=addOrRemove]");
    document.querySelector("td[name=addOrRemoveSum]").textContent = sumColumn(elementList,'value');
};

function newAmount() {
    let elementList = document.querySelectorAll("tbody");
    for (let row of elementList) {
        let lastAmount = row.querySelector("td[name=lastAmount]").textContent;
        let addOrRemoveSum = row.querySelector("input[sumCalc=addOrRemove]").value;
        (addOrRemoveSum === '' ? addOrRemoveSum = 0 : null)
        sum = parseFloat(lastAmount) + parseFloat(addOrRemoveSum);
        //console.log('lookiehere:', lastAmount, addOrRemoveSum, sum)
        row.querySelector("td[name=newAmount]").textContent = sum;
    }
    
    let resultRow = document.querySelector("tfoot > tr");
    //console.log(resultRow);
    let lastAmountFooter = resultRow.querySelector("td[name=previousSum]").textContent;
    let addOrRemoveSumFooter = resultRow.querySelector("td[name=addOrRemoveSum]").textContent;
    let sumFooter = parseFloat(lastAmountFooter) + parseFloat(addOrRemoveSumFooter);
    sumFooter = sumFooter.toFixed(2);
    //console.log('let\'s try this', lastAmountFooter, addOrRemoveSumFooter, sumFooter)
    resultRow.querySelector("td[name=newAmountSum]").textContent = sumFooter;
};

function submitShowHide() {
    const balanceDifference = document.querySelector("#balanceDifference").textContent;
    const addRemoveSum = document.querySelector("td[name=addOrRemoveSum]").textContent;
    let submitButton = document.querySelector("#form_submit");
    if (balanceDifference !== addRemoveSum && submitButton) {
        submitButton.remove();
    }
    if (balanceDifference === addRemoveSum && !submitButton) {
        console.log('now shoot, what do we do now?');
        formNode = document.querySelector("form");
        let input = document.createElement("input");
        input.value = "Submit";
        input.id = "form_submit";
        input.type = "submit";
        formNode.appendChild(input); // put it into the DOM
    }
}

function render() {
    previousAmount();
    addOrRemove();
    newAmount();
    submitShowHide();
}

render();