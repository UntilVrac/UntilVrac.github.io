function setFilterCouleur() {
    filterCouleur.innerHTML = '<option value="0">--sélectionner une couleur--</option>';
    var ton = filterTon.value;
    var listeOptions = [];
    if (ton == defaut[2]) {
        listeOptions = listeCouleurs;
    }
    else {
        listeOptions = dictCouleurs[ton];
    }
    for (var i=0; i<listeOptions.length; i++) {
        var opt = document.createElement("option");
        opt.value = listeOptions[i][0];
        opt.appendChild(document.createTextNode(listeOptions[i][1]));
        filterCouleur.appendChild(opt);
    }
}

setFilterCouleur();
if (couleurFilter != "0") {
    var del = document.getElementById("del" + indexFilterCouleurs);
    del.classList.remove("hide");
    del.classList.add("show");
    filterCouleur.value = couleurFilter;
}
filterTon.addEventListener("input", setFilterCouleur);

filterTon.addEventListener("input", setFilterCouleur);


console.log('script "gestion_listes_deroulantes_couleurs" chargé');