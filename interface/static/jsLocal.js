function deleteUser() {
        var item = document.getElementById("popup");
        item.setAttribute("style", "visibility: visible; position: fixed; width: 300px; top: 50%; left: 50%; margin-top: -100px; margin-left: -150px;");
}
function removePop() {
    var item = document.getElementById("popup");
    item.setAttribute("style", "visibility: hidden; position: fixed; width: 300px; top: 50%; left: 50%; margin-top: -100px; margin-left: -150px;");
}