let panneauAdd = document.getElementById("panneau_add");
let fermer = document.getElementById("fermer");
let ajouter = document.getElementById("ajouter");
panneauAdd.classList.add("hide");

function clearAdd() {
    for (var i=1; i<=nAdd; i++) {
        document.getElementById("add" + i).value = defautAdd[i];
    }
}

function showAdd() {
    if (panneauAdd.classList.contains("hide")) {
        panneauAdd.classList.remove("hide");
    }
}

function hideAdd() {
    clearAdd();
    if (!panneauAdd.classList.contains("hide")) {
        panneauAdd.classList.add("hide");
    }
}

ajouter.addEventListener("click", showAdd);
fermer.addEventListener("click", hideAdd);

console.log('script "gestion_panneau_add" chargé');