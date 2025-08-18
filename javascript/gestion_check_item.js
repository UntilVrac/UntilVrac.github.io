let checkItem = document.getElementById("checkTrans");
let inputCheck = document.getElementById("inputTrans");
let cross = document.getElementById("fermer");

let checkActive = "/images/check_active.svg";
let checkDesactive = "/images/check_desactive.svg";

function desactiverCheck() {
    checkItem.src = checkDesactive;
    inputCheck.value = "False";
}

function activerCheck() {
    checkItem.src = checkActive;
    inputCheck.value = "True";
}

function check() {
    if (inputCheck.value == "True") {
        desactiverCheck();
    }
    else {
        activerCheck();
    }
}

desactiverCheck();
checkItem.addEventListener("click", check);
cross.addEventListener("click", desactiverCheck);

console.log('script "gestion_check_item" chargé');