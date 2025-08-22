function show_cross(e) {
    i = this.id.substring(this.id.length - 1);
    if (document.getElementById("filter" + i).value != defaut[i]) {
        var item = document.getElementById("del" + i);
        item.classList.remove("hide");
        item.classList.add("show");
    }
    else {
        i = this.id.substring(this.id.length - 1);
        var item = document.getElementById("del" + i);
        item.classList.remove("show");
        item.classList.add("hide");
    }
}

function hide_cross(e) {
    this.classList.remove("show");
    this.classList.add("hide");
    i = this.id.substring(this.id.length - 1);
    var item = document.getElementById("filter" + i);
    item.value = defaut[i];
    if (i == indexFilterTon) {
        document.getElementById("filter" + (indexFilterTon + 1)).value = 0;
        var del = document.getElementById("filter" + (indexFilterTon + 1));
        del.classList.remove("show");
        del.classList.add("hide");
        setFilterCouleur();
    }
    else if (i == indexFilterCategories) {
        document.getElementById("filter" + (indexFilterCategories + 1)).value = 0;
        var del = document.getElementById("del" + (indexFilterCategories + 1));
        del.classList.remove("show");
        del.classList.add("hide");
        setFilterCategorie();
    }
}

// for (var i=1; i<=defaut.length; i++) {
//     document.getElementById("filter" + i).addEventListener("input", show_cross);
//     var del = document.getElementById("del" + i);
//     del.addEventListener("click", hide_cross);
//     if (document.getElementById("filter" + i).value != defaut[i]) {
//         del.classList.remove("hide");
//         del.classList.add("show");
//     }
// }

function addEventListenerForFiltres(n) {
    for (var i=1; i<=n; i++) {
        document.getElementById("filter" + i).addEventListener("input", show_cross);
        var del = document.getElementById("del" + i);
        del.addEventListener("click", hide_cross);
        if (document.getElementById("filter" + i).value != defaut[i]) {
            del.classList.remove("hide");
            del.classList.add("show");
        }
    }
}


console.log('script "gestion_filtres" chargé');