function setFilterCategorie() {
    filterSousCategorie.innerHTML = '<option value="0">--sélectionner une sous-catégorie--</option>';
    var cat = filterCategorie.value;
    var listeOptions = [];
    if (cat == 0) {
        listeOptions = listeCategories;
    }
    else {
        listeOptions = dictCategories[cat];
    }
    for (var i=0; i<listeOptions.length; i++) {
        var opt = document.createElement("option");
        opt.value = listeOptions[i][0];
        opt.appendChild(document.createTextNode(listeOptions[i][1]));
        filterSousCategorie.appendChild(opt);
    }
    filterSousCategorie.value = 0;
}

setFilterCategorie();
if (categorieFilter != "0") {
    var del = document.getElementById("del" + indexFilterSousCategories);
    del.classList.remove("hide");
    del.classList.add("show");
    filterSousCategorie.value = categorieFilter;
}

filterCategorie.addEventListener("input", setFilterCategorie);


console.log('script "gestion_listes_deroulantes_categories" chargé');